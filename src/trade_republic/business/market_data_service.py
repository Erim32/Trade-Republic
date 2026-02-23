from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class MarketDataService(TRAbstractService):
    """
    Service for managing Trade Republic market data.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_ticker(self, isin: str, exchange: str = "LSX") -> dict | None:
        """
        Fetches and saves ticker information.

        :param isin: ISIN code of the instrument.
        :param exchange: Exchange code.
        """
        data: dict | None = None
        try:
            data: dict | None = await self.api.get_ticker(isin, exchange)

            if self.is_debug:
                logger.debug(f"Successfully fetched ticker information for ISIN {isin} on exchange {exchange}.")
                TRUtils.save_data(data, f"ticker_{isin}_{exchange}.json", self.output_folder)
        except Exception as e:
            logger.error(f"Error fetching ticker for ISIN {isin} on exchange {exchange} ({isin}.{exchange}): {e}")
            return None
        return data

    async def resolve_best_exchange(self, isin: str) -> str | None:
        """
        Determines the most relevant exchange
        :param isin: ISIN code of the instrument.

        """
        raise NotImplementedError("Method not implemented.")

    async def resolve_used_exchange(self, isin: str) -> str | None:
        """
        Fetches the exchanges used for a given instrument by its ISIN.
        :param isin: ISIN code of the instrument.
        """
        logger.info(f"Fetching exchanges for ISIN {isin}...")
        instrument_info = await self.api.get_instrument(isin)
        instrument_info_exchanges = instrument_info.get("exchanges", [])
        # filter keep only active exchanges
        logger.debug(f"Exchange slugs : {[ex.get('slug') for ex in instrument_info_exchanges]}")
        instrument_info_exchanges = [ex for ex in instrument_info_exchanges if ex.get("active")]
        # get price exchange
        logger.debug(f"Fetching ticker information for each active exchange of ISIN {isin}...")
        for ex in instrument_info_exchanges:
            logger.debug(f"   - Exchange: {ex['slug']}")
            ex["ticker"] = await self.fetch_ticker(isin, ex["slug"])
            logger.debug(f"recuped ticker: {ex['ticker']}")

        # in each ex["ticker"].get("bid").get("time") need to order by most recent exchange
        instrument_info_exchanges.sort(
            key=lambda x: x.get("ticker", {}).get("bid", {}).get("time", ""),
            reverse=True,
        )

        if self.is_debug:
            logger.info(f"Exchanges fetched and sorted for ISIN {isin}.")
            TRUtils.save_data(
                instrument_info_exchanges,
                f"instrument_{isin}_exchanges.json",
                self.output_folder,
            )

        if instrument_info_exchanges:
            return instrument_info_exchanges[0]["slug"]
        else:
            return None

    async def fetch_last_price(self, isin: str, exchange: str | None = None) -> dict | None:
        """
        Last price (auto-resolution if exchange is absent)

        :param isin: ISIN code of the instrument.
        :param exchange: Exchange code (optional, will be determined automatically if None)
        """
        try:
            logger.info(f"Fetching last price for ISIN {isin}...")
            logger.debug(
                f"   - Exchange provided: {exchange}"
                if exchange
                else "   - No exchange provided, automatic determination in progress..."
            )
            if not exchange:
                logger.debug(f"Searching for used exchange for ISIN {isin}...")
                exchange_selected = await self.resolve_used_exchange(isin)
            else:
                exchange_selected = exchange

            if not exchange_selected:
                logger.warning(f"Unable to fetch last price without exchange for ISIN {isin}.")
                return None

            ticker_data: dict | None = await self.fetch_ticker(isin, exchange_selected)

            if not ticker_data:
                logger.warning(f"Unable to fetch ticker data for ISIN {isin} on exchange {exchange_selected}.")
                return None

            logger.info(f"Successfully fetched instrument information for ISIN {isin} on exchange {exchange_selected}.")
            logger.debug("Display in the app :")
            logger.debug(f"   - Last ASK price / Seller : {ticker_data.get('ask', {}).get('price', None)}")
            logger.debug(f"   - Last BID price / Buyer : {ticker_data.get('bid', {}).get('price', None)}")

            TRUtils.save_data(ticker_data, f"instrument_{isin}_last_price.json", self.output_folder)

            return ticker_data
        except Exception as e:
            logger.error(f"Error fetching price for {isin}: {e}")
            return None

    ##
    # Watchlist Management
    ##

    async def fetch_watchlist(self) -> dict:
        """
        Fetches the watchlist.

        :return: Watchlist content
        """
        try:
            logger.debug("Fetching watchlist.")
            data = await self.api.watchlist()
            if self.is_debug:
                TRUtils.save_data(data, "watchlist.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return {}

    async def add_to_watchlist(self, isin: str) -> dict:
        """
        Adds an instrument to the watchlist.

        :param isin: ISIN code of the instrument
        :return: API response
        """
        try:
            logger.info(f"Adding ISIN {isin} to watchlist.")
            response = await self.api.add_watchlist(isin)
            logger.info(f"ISIN {isin} successfully added to watchlist.")
            if self.is_debug:
                TRUtils.save_data(response, f"watchlist_add_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return {}

    async def remove_from_watchlist(self, isin: str) -> dict:
        """
        Removes an instrument from the watchlist.

        :param isin: ISIN code of the instrument
        :return: API response
        """
        try:
            logger.info(f"Removing ISIN {isin} from watchlist.")
            response = await self.api.remove_watchlist(isin)
            logger.info(f"ISIN {isin} successfully removed from watchlist.")
            if self.is_debug:
                TRUtils.save_data(response, f"watchlist_remove_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return {}

    ##
    # News Management
    ##

    async def fetch_news(self, isin: str) -> dict:
        """
        Fetches news for an instrument.

        :param isin: ISIN code of the instrument
        :return: Instrument news
        """
        try:
            logger.info(f"Fetching news for ISIN {isin}.")
            data = await self.api.news(isin)
            if self.is_debug:
                TRUtils.save_data(data, f"news_{isin}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return {}

    async def fetch_news_subscriptions(self) -> dict:
        """
        Fetches news subscriptions.

        :return: Active subscriptions
        """
        try:
            logger.debug("Fetching news subscriptions.")
            data = await self.api.news_subscriptions()
            if self.is_debug:
                TRUtils.save_data(data, "news_subscriptions.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching subscriptions: {e}")
            return {}

    async def subscribe_to_news(self, isin: str) -> dict:
        """
        Subscribes to news for an instrument.

        :param isin: ISIN code of the instrument
        :return: API response
        """
        try:
            logger.info(f"Subscribing to news for ISIN {isin}.")
            response = await self.api.subscribe_news(isin)
            logger.info(f"Successfully subscribed to news for ISIN {isin}.")
            if self.is_debug:
                TRUtils.save_data(response, f"subscribe_news_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error subscribing to news: {e}")
            return {}

    async def unsubscribe_from_news(self, isin: str) -> dict:
        """
        Unsubscribes from news for an instrument.

        :param isin: ISIN code of the instrument
        :return: API response
        """
        try:
            logger.info(f"Unsubscribing from news for ISIN {isin}.")
            response = await self.api.unsubscribe_news(isin)
            logger.info(f"Successfully unsubscribed from news for ISIN {isin}.")
            if self.is_debug:
                TRUtils.save_data(response, f"unsubscribe_news_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error unsubscribing: {e}")
            return {}
