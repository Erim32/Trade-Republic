from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class AccountService(TRAbstractService):
    """
    Service for managing Trade Republic accounts.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_accounts(self) -> list[dict]:
        """
        Fetches and saves account information.
        """
        dict_list = await self.api.get_accounts()

        if self.is_debug:
            logger.info(f"Successfully fetched account information. Number of accounts: {len(dict_list)}")
            TRUtils.save_data(dict_list, "trade_republic_profile_accounts.json", self.output_folder)

        return dict_list

    async def fetch_available_cash(self):
        """
        Fetches and saves available cash information.
        """
        data = await self.api.get_available_cash()

        if self.is_debug:
            logger.info("Successfully fetched available cash information.")
            TRUtils.save_data(data, "trade_republic_available_cash.json", self.output_folder)

        # Extract amount and currency from the first item
        if data and isinstance(data, list) and len(data) > 0:
            cash_info = data[0] if data else {}
            amount = cash_info.get("amount", None)
            device_currency = cash_info.get("currencyId", None)

        else:
            amount = None
            device_currency = None

        return data, amount, device_currency

    async def fetch_cash(self) -> dict:
        """
        Fetches account cash information.

        :return: Cash information
        """
        try:
            logger.debug("Fetching cash information.")
            data = await self.api.cash()
            if self.is_debug:
                TRUtils.save_data(data, "cash_info.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching cash: {e}")
            return {}

    async def fetch_available_cash_for_payout(self) -> dict:
        """
        Fetches available cash for withdrawal.

        :return: Available cash for withdrawal
        """
        try:
            logger.debug("Fetching available cash for withdrawal.")
            data = await self.api.available_cash_for_payout()
            if self.is_debug:
                TRUtils.save_data(data, "available_cash_for_payout.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching cash for withdrawal: {e}")
            return {}

    async def fetch_portfolio_by_account(self, securities_account_number: str):
        """
        Fetches and saves the portfolio by type.

        :param securities_account_number: Securities account number.
        """
        data = await self.api.get_portfolio_by_type(securities_account_number)

        if self.is_debug:
            logger.info(f"Successfully fetched portfolio by type for account {securities_account_number}.")
            TRUtils.save_data(
                data,
                f"portfolio_by_type_{securities_account_number}.json",
                self.output_folder,
            )

        return data

    ##
    # Advanced methods
    ##

    async def fetch_accounts_details(self, client) -> list:
        account_service = client.account_service
        accounts = await account_service.fetch_accounts()
        instrument_service = client.instrument_service
        portfolio_service = client.portfolio_service
        markets_data_service = client.market_data_service
        if not accounts:
            accounts = await account_service.fetch_accounts()

        (
            data_cash,
            amount,
            device_currency,
        ) = await account_service.fetch_available_cash()
        for account in accounts:
            cash_acc_no = account.get("cashAccountNumber")
            sec_acc_no = account.get("securitiesAccountNumber")

            # Enrich cash available
            if cash_acc_no:
                cash_data = None
                for item in data_cash:
                    if item.get("accountNumber") == cash_acc_no:
                        cash_data = item
                        break

                account["cash_available"] = cash_data or {
                    "accountNumber": cash_acc_no,
                    "amount": 0,
                    "currencyId": None,
                }

            # Enrich securities portfolio
            if sec_acc_no:
                logger.info(f"Fetching portfolio by type for account {sec_acc_no}...")
                account["portfolio"] = await portfolio_service.fetch_portfolio_by_type(sec_acc_no)
                # Complete portfolio positions with instrument and ticker info
                portfolio = account.get("portfolio", {})
                categories = portfolio.get("categories", [])
                for category in categories:
                    positions = category.get("positions", [])
                    for position in positions:
                        isin = position.get("isin")
                        if isin:
                            logger.debug(f"Fetching instrument information for {isin}...")
                            instrument_info = await instrument_service.fetch_instrument(isin)
                            position["instrument_info"] = instrument_info

                            logger.debug(f"Fetching ticker information for {isin}...")
                            exchange_ids = instrument_info.get("exchangeIds", [])
                            if len(exchange_ids) == 0 or "LSX" in exchange_ids:
                                exchange_ids = ["LSX"]  # Default exchange
                            else:
                                exchange_ids = exchange_ids[0:1]  # TODO : Retrieve optimal exchange

                            for exchange_code in exchange_ids:
                                ticker_info = await markets_data_service.fetch_ticker(isin, exchange_code)
                                position["ticker_info"] = position.get("ticker_info", {})
                                position["ticker_info"][exchange_code] = ticker_info

                            # Add current valuation if available
                            logger.debug("Calculating current valuation...")
                            position_amount = float(position.get("netSize", 0))
                            ticker_info = position["ticker_info"].get(exchange_ids[0], {})
                            price_bid = float(ticker_info.get("bid", {}).get("price", 0))
                            price_ask = float(ticker_info.get("ask", {}).get("price", 0))
                            price = price_bid if price_bid > 0 else price_ask
                            position["current_price"] = float(price)
                            position["current_valuation"] = price * position_amount
        return accounts
