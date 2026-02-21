from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class InstrumentService(TRAbstractService):
    """
    Service for managing Trade Republic instruments.
    """

    INSTRUMENT_TYPES = {
        "stock",
        "fund",
        "derivate",
        "crypto",
        "bond",
        "mutualFund",
        "privateFund",
    }

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_instrument(self, isin: str) -> dict:
        """
        Complete information for an instrument
        """

        data = await self.api.get_instrument(isin)

        if self.is_debug:
            TRUtils.save_data(data, f"instrument_{isin}.json", self.output_folder)

        return data

    async def fetch_instruments_by_type(self, instrument_type: str = "stock") -> list:
        """
        Complete list of instruments by type via search.
        """
        if instrument_type not in self.INSTRUMENT_TYPES:
            raise ValueError(f"Unsupported instrument type: {instrument_type}")

        data = await self.api.search(asset_type=instrument_type, query="", page_size=1, page=1)

        if self.is_debug:
            TRUtils.save_data(data, f"instruments_{instrument_type}.json", self.output_folder)

        return data.get("results", [])

    async def fetch_instruments(self):
        results: list = []
        for instrument_type in self.INSTRUMENT_TYPES:
            logger.info(f"Fetching all ISIN instruments of type '{instrument_type}'...")
            params = {
                "query": "",
                "asset_type": instrument_type,
                "aggregate": False,
                "page": 0,
                "page_size": 0,
            }

            # number of instruments
            params_count = params.copy()
            params_count["page_size"] = 1
            params_count["page"] = 1
            data = await self.api.search(**params_count)
            total_instruments = data.get("resultCount", 0)
            logger.info(f"Total instruments to fetch: {total_instruments}")

            batch_size = 20
            offset = 0
            cpt = 0

            while True:
                logger.debug(
                    f"   - [{cpt}-{instrument_type}-{offset}/{total_instruments}] Fetching instruments {offset + 1} to {min(offset + batch_size, total_instruments)}..."
                )
                params_batch = params.copy()
                params_batch["page_size"] = batch_size
                params_batch["page"] = cpt + 1
                cpt += 1
                data_batch = await self.api.search(**params_batch)
                logger.debug(f"Data batch: {data_batch}")
                logger.debug(f"   - Fetched {len(data_batch.get('results', []))} instruments.")
                results_batch = data_batch.get("results", [])
                for item in results_batch:
                    results.append(item)
                offset += batch_size
                if offset >= total_instruments:
                    break

            logger.info(f"Finished fetching instruments of type '{instrument_type}'. Total fetched: {len(results)}")
        if self.is_debug:
            TRUtils.save_data(results, "instruments_all_types.json", self.output_folder)

        logger.info(f"Successfully fetched all instruments. Total instruments fetched: {len(results)}")
        return results

    async def fetch_instrument_details(self, isin: str) -> dict:
        """
        Fetches complete instrument details.

        :param isin: ISIN code of the instrument
        :return: Instrument details
        """
        data = {}
        try:
            logger.debug(f"Fetching instrument details for {isin}.")
            data = await self.api.get_instrument(isin)
            if self.is_debug:
                TRUtils.save_data(data, f"instrument_details_{isin}.json", self.output_folder)
        except Exception as e:
            logger.error(f"Error fetching instrument details: {e}")
        return data

    async def fetch_instrument_suitability(self, isin: str) -> dict:
        """
        Fetches suitability information for an instrument.

        :param isin: ISIN code of the instrument
        :return: Suitability information
        """
        data = {}
        try:
            logger.debug(f"Fetching suitability for instrument {isin}.")
            data = await self.api.instrument_suitability(isin)
            if self.is_debug:
                TRUtils.save_data(data, f"instrument_suitability_{isin}.json", self.output_folder)
        except Exception as e:
            logger.error(f"Error fetching suitability: {e}")
        return data

    async def fetch_stock_details(self, isin: str) -> dict:
        """
        Fetches stock details.

        :param isin: ISIN code of the stock
        :return: Stock details
        """
        data = {}
        try:
            logger.debug(f"Fetching stock details for {isin}.")
            data = await self.api.stock_details(isin)
            if self.is_debug:
                TRUtils.save_data(data, f"stock_details_{isin}.json", self.output_folder)
        except Exception as e:
            logger.error(f"Error fetching stock details: {e}")
        return data
