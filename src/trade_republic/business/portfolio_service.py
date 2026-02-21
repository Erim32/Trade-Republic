from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.business.account_service import AccountService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class PortfolioService(TRAbstractService):
    """
    Service for managing Trade Republic portfolios.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_portfolio_by_type(self, securities_account_number: str):
        """
        Fetches and saves the portfolio by type.

        :param securities_account_number: Securities account number.
        """
        data = await self.api.get_portfolio_by_type(securities_account_number)

        return data

    async def fetch_portfolio(self, tr_client) -> list:
        """
        Fetches and saves the portfolio.
        :param by_account: If True, returns the portfolio by account.
        """
        account_service: AccountService = tr_client.account_service

        logger.info("Fetching global portfolio by account...")
        portfolio_data = []
        portfolio_data = await account_service.fetch_accounts_details(tr_client)
        return portfolio_data

    async def fetch_portfolio_positions(
        self, tr_client, french_classification: bool = False, add_cash: bool = True
    ) -> list:
        """
        Fetches and saves portfolio positions.
            :param by_account: If True, returns portfolio positions by account.
        """
        portfolio_data = await self.fetch_portfolio(tr_client)

        def group_categories(data):
            """
            Groups positions by categoryType from an array of portfolios.
            :param data: List of portfolios to group.
            :return: Dictionary with grouped categories and products.
            """
            # Dictionary to group positions by categoryType
            categories_dict = {}
            all_products = []

            # Iterate through each element in the array
            for item in data:
                # Group the categories
                for category in item.get("categories", []):
                    category_type = category["categoryType"]
                    positions = category.get("positions", [])

                    # If the category already exists, add the positions
                    if category_type in categories_dict:
                        categories_dict[category_type].extend(positions)
                    else:
                        categories_dict[category_type] = positions

                # Collect all products
                all_products.extend(item.get("products", []))

            # Build the final result
            result = {
                "categories": [
                    {"categoryType": category_type, "positions": positions}
                    for category_type, positions in categories_dict.items()
                ],
                "products": all_products,
            }

            return result

        for account in portfolio_data:
            acc_product_type = account.get("productType")
            for category in account.get("portfolio", {}).get("categories", []):
                for position in category.get("positions", []):
                    if french_classification:
                        if acc_product_type == "DEFAULT":  # DEFAULT CTO
                            position["account_label"] = "CTO"
                        elif acc_product_type == "TAX_WRAPPER":  # FRENCH PEA
                            position["account_label"] = "PEA"
                        else:
                            position["account_label"] = "UNKNOWN"

                    instrument_infos = position.get("instrument_info", {})
                    instrument_infos_primary_exchange = (
                        instrument_infos.get("primaryExchange") or (instrument_infos.get("exchanges") or [None])[0]
                    )
                    if instrument_infos_primary_exchange:
                        position["ticker"] = instrument_infos_primary_exchange.get("symbolAtExchange")
                    else:
                        position["ticker"] = None

            if add_cash:
                # Add cash available for each account as a position as "productType": "CASH"
                cash_available = account.get("cash_available", {})
                cash_device_currency = cash_available.get("currencyId", "EUR")
                account_label = (
                    account.get("portfolio", {})
                    .get("categories", [None])[0]
                    .get("positions", [None])[0]
                    .get("account_label", "UNKNOWN")
                )
                cash_position = {
                    "instrumentType": "CASH",
                    "netSize": cash_available.get("amount", 0),
                    "current_valuation": cash_available.get("amount", 0),
                    "isin": cash_device_currency,
                    "name": "Cash Available",
                    "ticker": cash_device_currency,
                    "currency": cash_device_currency,
                    "productType": "CASH",
                    "averageBuyIn": 1,
                    "current_price": 1,
                }
                if french_classification:
                    cash_position["account_label"] = account_label

                # add to positions
                account.get("portfolio", {}).get("categories", [None])[0].get("positions", []).append(cash_position)

        grouped_portfolio = group_categories([account.get("portfolio", {}) for account in portfolio_data])

        # merge all positions in one list
        positions = []
        for category in grouped_portfolio.get("categories", []):
            positions.extend(category.get("positions", []))

        if self.is_debug:
            TRUtils.save_data(positions, "debug_portfolio_positions.json", self.output_folder)

        return positions

    async def fetch_portfolio_status(self) -> dict:
        """
        Fetches the portfolio status.

        :return: Portfolio status
        """
        try:
            logger.debug("Fetching portfolio status.")
            data = await self.api.portfolio_status()
            if self.is_debug:
                TRUtils.save_data(data, "portfolio_status.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching portfolio status: {e}")
            return {}

    async def fetch_portfolio_history(self, timeframe: str = "1y") -> dict:
        """
        Fetches the portfolio history.

        :param timeframe: Time period ('1w', '1m', '3m', '6m', '1y', 'all')
        :return: Portfolio history
        """
        try:
            logger.info(f"Fetching portfolio history for period {timeframe}.")
            data = await self.api.portfolio_history(timeframe)
            if self.is_debug:
                TRUtils.save_data(data, f"portfolio_history_{timeframe}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching portfolio history: {e}")
            return {}

    async def fetch_performance(self, isin: str, exchange: str = "LSX") -> dict:
        """
        Fetches performance data for an instrument.

        :param isin: ISIN code of the instrument
        :param exchange: Exchange code
        :return: Performance data
        """
        try:
            logger.debug(f"Fetching performance for ISIN {isin} on {exchange}.")
            data = await self.api.performance(isin, exchange)
            if self.is_debug:
                TRUtils.save_data(data, f"performance_{isin}_{exchange}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching performance: {e}")
            return {}
