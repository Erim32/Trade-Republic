from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class SearchService(TRAbstractService):
    """
    Service for managing Trade Republic searches.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def search_instruments(
        self,
        query: str,
        asset_type: str = "stock",
        page: int = 1,
        page_size: int = 20,
        aggregate: bool = False,
        only_savable: bool = False,
        filter_index: str = "",
        filter_country: str = "",
        filter_sector: str = "",
        filter_region: str = "",
        filter_jurisdiction: str = "",
    ) -> dict:
        """
        Searches for instruments according to various criteria.

        :param query: Search term
        :param asset_type: Asset type ('stock', 'fund', 'crypto', etc.)
        :param page: Page number
        :param page_size: Number of results per page
        :param aggregate: If True, returns aggregated results
        :param only_savable: If True, returns only savable instruments
        :param filter_index: Filter by index
        :param filter_country: Filter by country
        :param filter_sector: Filter by sector
        :param filter_region: Filter by region
        :param filter_jurisdiction: Filter by jurisdiction
        :return: Search results
        """
        try:
            logger.info(f"Searching for instruments with term: '{query}'")
            results = await self.api.search(
                query=query,
                asset_type=asset_type,
                page=page,
                page_size=page_size,
                aggregate=aggregate,
                only_savable=only_savable,
                filter_index=filter_index,
                filter_country=filter_country,
                filter_sector=filter_sector,
                filter_region=filter_region,
                filter_jurisdiction=filter_jurisdiction,
            )
            count = len(results.get("results", []))
            logger.info(f"Search completed: {count} result(s) found.")
            if self.is_debug:
                TRUtils.save_data(results, f"search_{query}_{page}.json", self.output_folder)
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return {}

    async def search_by_country(
        self, country: str, asset_type: str = "stock", page: int = 1, page_size: int = 20
    ) -> dict:
        """
        Searches for instruments filtered by country.

        :param country: Country code
        :param asset_type: Asset type
        :param page: Page number
        :param page_size: Number of results per page
        :return: Search results
        """
        return await self.search_instruments(
            query="",
            asset_type=asset_type,
            page=page,
            page_size=page_size,
            filter_country=country,
        )

    async def search_by_sector(
        self, sector: str, asset_type: str = "stock", page: int = 1, page_size: int = 20
    ) -> dict:
        """
        Searches for instruments filtered by sector.

        :param sector: Sector name
        :param asset_type: Asset type
        :param page: Page number
        :param page_size: Number of results per page
        :return: Search results
        """
        return await self.search_instruments(
            query="",
            asset_type=asset_type,
            page=page,
            page_size=page_size,
            filter_sector=sector,
        )

    async def get_search_tags(self) -> dict:
        """
        Fetches available search tags.

        :return: Dictionary of available tags
        """
        try:
            logger.debug("Fetching search tags.")
            tags = await self.api.search_tags()
            if self.is_debug:
                TRUtils.save_data(tags, "search_tags.json", self.output_folder)
            return tags
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return {}

    async def get_suggested_tags(self, query: str) -> dict:
        """
        Fetches suggested tags for a query.

        :param query: Search term
        :return: Suggested tags
        """
        try:
            logger.debug(f"Fetching suggested tags for: '{query}'")
            suggestions = await self.api.search_suggested_tags(query)
            if self.is_debug:
                TRUtils.save_data(suggestions, f"suggested_tags_{query}.json", self.output_folder)
            return suggestions
        except Exception as e:
            logger.error(f"Error fetching suggested tags: {e}")
            return {}
