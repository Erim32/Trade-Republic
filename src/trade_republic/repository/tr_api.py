import asyncio
import itertools
import json
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

import requests
import websockets

from trade_republic.models.tr_exceptions import AuthenticationError, InvalidCredentialsError, ValidationError
from trade_republic.utils.logger import logger


class TRApi:
    """
    Class for managing WebSocket communications with the TradeRepublic API.
    """

    def __init__(self, token: str, max_concurrent_connections: int = 5):
        """
        Initializes the TR_API class.

        :param token: Session token for authentication.
        :param max_concurrent_connections: Maximum number of simultaneous WebSocket connections (default: 5).
        """
        self._token = token
        self.websocket_url = "wss://api.traderepublic.com"
        self.locale_config = {
            "locale": "fr",
            "platformId": "webtrading",
            "platformVersion": "safari - 18.3.0",
            "clientId": "app.traderepublic.com",
            "clientVersion": "3.151.3",
        }
        self._message_counter = itertools.count(1)
        self.max_concurrent_connections = max_concurrent_connections
        self.connection_semaphore = asyncio.Semaphore(max_concurrent_connections)
        logger.info(f"TRApi initialized with a maximum of {max_concurrent_connections} simultaneous connections.")

    ##
    # Authentification & Connexion
    ##

    @staticmethod
    def login(phone_number: str, pin: str, max_concurrent_connections: int = 5) -> "TRApi":
        """
        Establishes connection to the Trade Republic API.
        :param phone_number: Phone number for login.
        :param pin: PIN for login.
        :param max_concurrent_connections: Maximum number of simultaneous WebSocket connections (default: 5).
        :return: An instance of TRApi with an established connection.
        """

        phone_number = phone_number or os.getenv("TR_PHONE", "")
        pin = pin or os.getenv("TR_PIN", "")

        if not phone_number or not pin:
            error_msg = "Phone number or PIN not defined in environment variables (TR_PHONE, TR_PIN)."
            logger.error(error_msg)
            raise InvalidCredentialsError(error_msg)

        logger.info(f"Phone number: +**********{phone_number[-2:]}")
        try:
            token_session = TRApi._authenticate_traderepublic(phone_number, pin, "json")
            logger.info("Authentication successful. Token obtained.")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {e}") from e

        if not token_session:
            error_msg = "Authentication failed. Token is empty. Please check phone number and PIN."
            logger.error(error_msg)
            raise AuthenticationError(error_msg)

        return TRApi(token_session, max_concurrent_connections=max_concurrent_connections)

    @staticmethod
    def _authenticate_traderepublic(phone_number: str, pin: str, output_format: str) -> str:
        """
        Authenticates a Trade Republic user and returns the session token.
        :param phone_number: Phone number (international format)
        :param pin: Login PIN
        :param output_format: 'json' or 'csv'
        :return: Session token
        :raises AuthenticationError: if authentication fails
        :raises ValidationError: if output format is invalid
        """

        def headers_to_dict(response):
            """
            Transforms HTTP response headers into a structured dictionary.

            :param response: HTTP response object.
            :return: Dictionary containing structured headers.
            """
            extracted_headers = {}
            for header, header_value in response.headers.items():
                parsed_dict = {}
                entries = header_value.split(", ")
                for entry in entries:
                    key_value = entry.split(";")[0]
                    if "=" in key_value:
                        key, value = key_value.split("=", 1)
                        parsed_dict[key.strip()] = value.strip()
                extracted_headers[header] = parsed_dict if parsed_dict else header_value
            return extracted_headers

        # Validate output format
        if output_format.lower() not in {"json", "csv"}:
            raise ValidationError(f"Invalid format '{output_format}'. Please use 'json' or 'csv'.")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/144.0.7559.110 Safari/537.36"
            )
        }

        # Initialize connection
        response = requests.post(
            "https://api.traderepublic.com/api/v1/auth/web/login",
            json={"phoneNumber": phone_number, "pin": pin},
            headers=headers,
        ).json()

        process_id = response.get("processId")
        countdown = response.get("countdownInSeconds")

        if not process_id:
            raise AuthenticationError("Login initialization failed. Please check phone number and PIN.")

        # Enter 2FA code
        code = input(f"Enter the 2FA code received ({countdown} seconds remaining) or type 'SMS': ")

        if code == "SMS":
            requests.post(
                f"https://api.traderepublic.com/api/v1/auth/web/login/{process_id}/resend",
                headers=headers,
            )
            code = input("Enter the 2FA code received by SMS: ")

        # Device verification
        response = requests.post(
            f"https://api.traderepublic.com/api/v1/auth/web/login/{process_id}/{code}",
            headers=headers,
        )

        if response.status_code != 200:
            raise AuthenticationError("Device verification failed. Please check the 2FA code.")

        # Extract session token
        response_headers = headers_to_dict(response)
        session_token = response_headers.get("Set-Cookie", {}).get("tr_session")

        if not session_token:
            raise AuthenticationError("Session token not found in response headers.")

        return session_token

    async def ws_connect(self):
        """
        Establishes a WebSocket connection to the TradeRepublic API.

        :return: The connected WebSocket object.
        """
        websocket = await websockets.connect(self.websocket_url)
        await websocket.send(f"connect 31 {json.dumps(self.locale_config)}")
        await websocket.recv()
        logger.debug("WebSocket connection successful! Please wait...")

        return websocket

    @asynccontextmanager
    async def ws_connect_with_limit(self):
        """
        Context manager to establish a WebSocket connection with simultaneous connection limiting.

        Uses a semaphore to limit the number of active WebSocket connections.
        Connections exceeding the limit wait until a connection is freed.

        :return: The connected WebSocket object.
        """
        async with self.connection_semaphore:
            websocket = await self.ws_connect()
            try:
                yield websocket
            finally:
                await websocket.close()

    ##
    # Utility Methods
    ##

    def _extract_json(self, response: str, bracket_type: str = "{}") -> Any:
        """
        Extracts JSON from a WebSocket response.

        :param response: Raw WebSocket response.
        :param bracket_type: Type of brackets to look for ('{}' or '[]').
        :return: Parsed JSON data.
        """
        if bracket_type == "{}":
            start_char, end_char = "{", "}"
        else:
            start_char, end_char = "[", "]"

        start_index = response.find(start_char)
        end_index = response.rfind(end_char)

        if start_index != -1 and end_index != -1:
            json_str = response[start_index : end_index + 1]
        else:
            json_str = bracket_type

        return json.loads(json_str)

    async def _send_request(self, websocket, payload: dict, expect_array: bool = False) -> Any:
        """
        Sends a WebSocket request and retrieves the response.

        :param websocket: Connected WebSocket object.
        :param payload: Request payload.
        :param expect_array: If True, expects a JSON array, otherwise an object.
        :return: Parsed JSON data from the response.
        """
        message_id = next(self._message_counter)
        payload["token"] = self._token
        logger.debug(f"Sending request for message ID: {message_id}")
        debug_payload = {k: ("***" if k == "token" else v) for k, v in payload.items()}
        logger.debug(f"sub {message_id} {json.dumps(debug_payload)}")
        await websocket.send(f"sub {message_id} {json.dumps(payload)}")
        response: str = await websocket.recv()

        logger.debug(f"Response received for message ID: {message_id}")
        await websocket.send(f"unsub {message_id}")
        websocket.recv()  # DO NOT ADD AWAIT
        logger.debug(f"Unsubscribed for message ID: {message_id}")

        bracket_type = "[]" if expect_array else "{}"
        return self._extract_json(response, bracket_type)

    ##
    # Account & Liquidity Management
    ##

    async def get_accounts(self) -> list[dict]:
        """
        Fetches account information.

        :return: List of user accounts.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "accountPairs"}
            return await self._send_request(websocket, payload, expect_array=True)

    async def get_available_cash(self) -> list[dict]:
        """
        Fetches available cash information.

        :return: List of available amounts.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "availableCash"}
            return await self._send_request(websocket, payload, expect_array=True)

    async def cash(self):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "cash"})

    async def available_cash_for_payout(self):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "availableCashForPayout"})

    ###
    # Portfolio & Positions
    ###
    async def get_portfolio_by_type(self, sec_acc_no: str) -> dict:
        """
        Fetches the portfolio by type.

        :param sec_acc_no: Securities account number.
        :return: Portfolio dictionary by type.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "compactPortfolioByType", "secAccNo": sec_acc_no}
            return await self._send_request(websocket, payload)

    async def portfolio_status(self):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "portfolioStatus"})

    async def portfolio_history(self, timeframe):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "portfolioAggregateHistory", "range": timeframe})

    async def performance(self, isin, exchange="LSX"):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "performance", "id": f"{isin}.{exchange}"})

    ##
    # Transactions & History Methods
    ##

    async def get_transactions(self, after_cursor: str | None = None) -> dict:
        """
        Fetches a page of transactions.

        :param after_cursor: Pagination cursor (optional).
        :return: Dictionary containing transactions and the next cursor.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "timelineTransactions"}
            if after_cursor:
                payload["after"] = after_cursor

            return await self._send_request(websocket, payload)

    async def get_transaction_details(self, transaction_id: str) -> dict:
        """
        Fetches details of a specific transaction.

        :param transaction_id: Transaction ID.
        :return: Dictionary containing transaction details.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "timelineDetailV2", "id": transaction_id}
            response_data = await self._send_request(websocket, payload)

            transaction_data = {}
            for section in response_data.get("sections", []):
                if section.get("title") == "Transaction":
                    for item in section.get("data", []):
                        header = item.get("title")
                        value = item.get("detail", {}).get("text")
                        if header and value:
                            transaction_data[header] = value

            return transaction_data

    async def timeline(self, after=None):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "timeline", "after": after})

    async def timeline_detail(self, timeline_id):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "timelineDetail", "id": timeline_id})

    async def timeline_detail_order(self, order_id):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "timelineDetail", "orderId": order_id})

    async def timeline_detail_savings_plan(self, savings_plan_id):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "timelineDetail", "savingsPlanId": savings_plan_id})

    ##
    # Order and Market Methods
    ##

    async def order_overview(self):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "orders"})

    async def limit_order(
        self,
        isin,
        exchange,
        order_type,
        size,
        limit,
        expiry,
        expiry_date=None,
        warnings_shown=None,
    ):
        parameters = {
            "type": "simpleCreateOrder",
            "clientProcessId": str(uuid.uuid4()),
            "warningsShown": warnings_shown if warnings_shown else [],
            "parameters": {
                "instrumentId": isin,
                "exchangeId": exchange,
                "expiry": {"type": expiry},
                "limit": limit,
                "mode": "limit",
                "size": size,
                "type": order_type,
            },
        }
        if expiry == "gtd" and expiry_date:
            parameters["parameters"]["expiry"]["value"] = expiry_date

        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, parameters)

    async def market_order(
        self,
        isin,
        exchange,
        order_type,
        size,
        expiry,
        sell_fractions,
        expiry_date=None,
        warnings_shown=None,
    ):
        parameters = {
            "type": "simpleCreateOrder",
            "clientProcessId": str(uuid.uuid4()),
            "warningsShown": warnings_shown if warnings_shown else [],
            "parameters": {
                "instrumentId": isin,
                "exchangeId": exchange,
                "expiry": {"type": expiry},
                "mode": "market",
                "sellFractions": sell_fractions,
                "size": size,
                "type": order_type,
            },
        }
        if expiry == "gtd" and expiry_date:
            parameters["parameters"]["expiry"]["value"] = expiry_date

        logger.info(
            f"Sending order creation request for {order_type} {size} shares of {isin} at {exchange} with expiry {expiry}."
        )
        logger.debug(f"Payload: {json.dumps(parameters)}")
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, parameters)

    async def stop_market_order(
        self,
        isin,
        exchange,
        order_type,
        size,
        stop,
        expiry,
        expiry_date=None,
        warnings_shown=None,
    ):
        parameters = {
            "type": "simpleCreateOrder",
            "clientProcessId": str(uuid.uuid4()),
            "warningsShown": warnings_shown if warnings_shown else [],
            "parameters": {
                "instrumentId": isin,
                "exchangeId": exchange,
                "expiry": {"type": expiry},
                "mode": "stopMarket",
                "size": size,
                "stop": stop,
                "type": order_type,
            },
        }
        if expiry == "gtd" and expiry_date:
            parameters["parameters"]["expiry"]["value"] = expiry_date

        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, parameters)

    async def cancel_order(self, order_id):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "cancelOrder", "orderId": order_id})

    ##
    # Savings Plan Methods
    ##

    async def savings_plan_overview(self):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "savingsPlans"})

    async def savings_plan_parameters(self, isin: str):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "savingsPlanParameters", "instrumentId": isin})

    async def create_savings_plan(
        self,
        isin,
        amount,
        interval,
        start_date,
        start_date_type,
        start_date_value,
        warnings_shown=None,
    ):
        parameters = {
            "type": "createSavingsPlan",
            "warningsShown": warnings_shown if warnings_shown else [],
            "parameters": {
                "amount": amount,
                "instrumentId": isin,
                "interval": interval,
                "startDate": {
                    "nextExecutionDate": start_date,
                    "type": start_date_type,
                    "value": start_date_value,
                },
            },
        }
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, parameters)

    async def change_savings_plan(
        self,
        savings_plan_id,
        isin,
        amount,
        interval,
        start_date,
        start_date_type,
        start_date_value,
        warnings_shown=None,
    ):
        parameters = {
            "id": savings_plan_id,
            "type": "createSavingsPlan",
            "warningsShown": warnings_shown if warnings_shown else [],
            "parameters": {
                "amount": amount,
                "instrumentId": isin,
                "interval": interval,
                "startDate": {
                    "nextExecutionDate": start_date,
                    "type": start_date_type,
                    "value": start_date_value,
                },
            },
        }
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, parameters)

    async def cancel_savings_plan(self, savings_plan_id):
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "cancelSavingsPlan", "id": savings_plan_id})

    ##
    # Financial Instruments & Search
    ##

    async def get_ticker(self, isin: str, exchange: str = "LSX") -> dict:
        """
        Fetches ticker information for an ISIN.

        :param isin: ISIN code of the instrument.
        :param exchange: Exchange code (default: LSX).
        :return: Dictionary of ticker information.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "ticker", "id": f"{isin}.{exchange}"}
            return await self._send_request(websocket, payload)

    async def get_instrument(self, isin: str) -> dict:
        """
        Fetches instrument information by ISIN.

        :param isin: ISIN code of the instrument.
        :return: Dictionary of instrument information.
        """
        async with self.ws_connect_with_limit() as websocket:
            payload = {"type": "instrument", "id": isin}
            return await self._send_request(websocket, payload)

    async def instrument_suitability(self, isin: str):
        """
        Fetches suitability information for a given ISIN.
        :param isin: ISIN code of the instrument.
        :return: Dictionary of instrument suitability information.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "instrumentSuitability", "instrumentId": isin})

    async def stock_details(self, isin: str):
        """
        Fetches stock details for a given ISIN.
        :param isin: ISIN code of the stock.
        :return: Dictionary of stock details.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "stockDetails", "id": isin})

    async def search_tags(self):
        """
        Fetches available search tags for instrument search.
        :return: List of search tags.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "neonSearchTags"})

    async def search_suggested_tags(self, query):
        """
        Fetches suggested search tags based on a query.
        :param query: Search query string.
        :return: List of suggested search tags.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "neonSearchSuggestedTags", "data": {"q": query}})

    async def search(
        self,
        query,
        asset_type="stock",
        page=1,
        page_size=20,
        aggregate=False,
        only_savable=False,
        filter_index=None,
        filter_country=None,
        filter_sector=None,
        filter_region=None,
        filter_jurisdiction=None,
    ):
        """
        Searches for financial instruments based on a query and various filters.
        :param query: Search query string.
        :param asset_type: Type of asset to search for (default: "stock").
        :param page: Page number for pagination (default: 1).
        :param page_size: Number of results per page (default: 20).
        :param aggregate: If True, returns aggregated results (default: False).
        :param only_savable: If True, returns only savable instruments (default: False).
        :param filter_index: Filter by index (optional).
        :param filter_country: Filter by country (optional).
        :param filter_sector: Filter by sector (optional).
        :param filter_region: Filter by region (optional).
        :param filter_jurisdiction: Filter by jurisdiction (optional).
        :return: Search results based on the provided criteria.
        """

        search_parameters = {
            "q": query,
            "filter": [{"key": "type", "value": asset_type}],
            "page": page,
            "pageSize": page_size,
        }
        if only_savable:
            search_parameters["filter"].append({"key": "attribute", "value": "savable"})
        if filter_index:
            search_parameters["filter"].append({"key": "index", "value": filter_index})
        if filter_country:
            search_parameters["filter"].append({"key": "country", "value": filter_country})
        if filter_region:
            search_parameters["filter"].append({"key": "region", "value": filter_region})
        if filter_sector:
            search_parameters["filter"].append({"key": "sector", "value": filter_sector})
        if filter_jurisdiction:
            search_parameters["filter"].append({"key": "jurisdiction", "value": filter_jurisdiction})
        search_type = "neonSearch" if not aggregate else "neonSearchAggregations"
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": search_type, "data": search_parameters})

    ##
    # Watchlist & Suivi
    ##

    async def watchlist(self):
        """
        Fetches the user's watchlist.
        :return: List of instruments in the watchlist.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "watchlist"})

    async def add_watchlist(self, isin: str):
        """
        Adds an instrument to the user's watchlist.
        :param isin: ISIN code of the instrument to add.
        :return: Updated watchlist after adding the instrument.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "addToWatchlist", "instrumentId": isin})

    async def remove_watchlist(self, isin: str):
        """
        Removes an instrument from the user's watchlist.
        :param isin: ISIN code of the instrument to remove.
        :return: Updated watchlist after removing the instrument.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "removeFromWatchlist", "instrumentId": isin})

    ##
    # Alerts & News Methods
    ##

    async def price_alarm_overview(self):
        """
        Fetches the user's price alarms.
        :return: List of price alarms set by the user.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "priceAlarms"})

    async def create_price_alarm(self, isin: str, price: str):
        """
        Creates a price alarm for a specific instrument and target price.
        :param isin: ISIN code of the instrument.
        :param price: Target price for the alarm.
        :return: Details of the created price alarm.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(
                websocket,
                {
                    "type": "createPriceAlarm",
                    "instrumentId": isin,
                    "targetPrice": price,
                },
            )

    async def cancel_price_alarm(self, price_alarm_id: str):
        """
        Cancels a price alarm by its ID.
        :param price_alarm_id: ID of the price alarm to cancel.
        :return: Confirmation of the canceled price alarm.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "cancelPriceAlarm", "id": price_alarm_id})

    async def news(self, isin: str):
        """
        Fetches news related to a specific instrument.
        :param isin: ISIN code of the instrument.
        :return: List of news articles related to the instrument.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "neonNews", "isin": isin})

    async def news_subscriptions(self):
        """
        Fetches the user's current news subscriptions.
        :return: List of ISINs the user is subscribed to for news.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "newsSubscriptions"})

    async def subscribe_news(self, isin: str):
        """
        Subscribes the user to news updates for a specific instrument.
        :param isin: ISIN code of the instrument to subscribe to.
        :return: Confirmation of the news subscription.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "subscribeNews", "instrumentId": isin})

    async def unsubscribe_news(self, isin: str):
        """
        Unsubscribes the user from news updates for a specific instrument.
        :param isin: ISIN code of the instrument to unsubscribe from.
        :return: Confirmation of the news unsubscription.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "unsubscribeNews", "instrumentId": isin})

    ##
    #  Interface & User Experience
    ##
    async def experience(self):
        """
        Fetches user experience settings and information.
        :return: Dictionary containing user experience details.
        """

        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "experience"})

    async def motd(self):
        """
        Fetches the message of the day (MOTD) for the user.
        :return: Dictionary containing the message of the day.
        """

        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "messageOfTheDay"})

    async def neon_cards(self):
        """
        Fetches the user's neon cards, which may include personalized offers, insights, or features.
        :return: List of neon cards available to the user.
        """
        async with self.ws_connect_with_limit() as websocket:
            return await self._send_request(websocket, {"type": "neonCards"})
