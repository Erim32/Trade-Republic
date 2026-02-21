from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class OrderService(TRAbstractService):
    """
    Service for managing Trade Republic orders.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_orders(self):
        """
        Fetches the list of orders.

        :return: List of orders
        """
        response = await self.api.order_overview()
        logger.info(f"Fetched {len(response.get('orders', []))} orders.")
        logger.debug(f"Response: {response}")
        if self.is_debug:
            TRUtils.save_data(response, "debug_orders_overview.json", self.output_folder)
        return response

    async def create_limit_order(
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
        """
        Creates a limit order.
        :param isin: `string` : ISIN of the instrument
        :param exchange: string`: identifies a stock exchange, usually `"LSX"` for *Lang & Schwarz Exchange*
        :param order_type: `string`: allowed values are `"buy"` or `"sell"
        :param size: `int`: number of shares to buy/sell
        :param limit: `float`: limit price for the order
        :param expiry: `string`: allowed values are `"gfd"` (good for day), `"gtd"` (good till date) and `"gtc"` (good till cancelled)
        :param expiry_date: `string` or `None`: date until which the order is valid if `expiry` is `"gtd"`
        `list of strings` (optional): may contain one or more of the following values: `"targetMarket"`, `"userExperience"`, `"unknown"` - however an empty list also seems to always be accepted

        :return: Response from the API
        """

        response = await self.api.limit_order(
            isin, exchange, order_type, size, limit, expiry, expiry_date, warnings_shown
        )

        logger.info(
            f"Created limit order with ISIN {isin} on exchange {exchange} for {size} shares at limit price {limit}."
        )
        logger.debug(f"Response: {response}")
        if self.is_debug:
            TRUtils.save_data(response, "debug_create_limit_order.json", self.output_folder)

        return response

    async def create_market_order(
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
        """
        Creates a market order.
        :param isin: `string` : ISIN of the instrument
        :param exchange: string`: identifies a stock exchange, usually `"LSX"` for *Lang & Schwarz Exchange*
        :param order_type: `string`: allowed values are `"buy"` or `"sell"
        :param size: `int`: number of shares to buy/sell
        :param sell_fractions: `bool`: sell remaining fractional shares
        :param expiry: `string`: allowed values are `"gfd"` (good for day), `"gtd"` (good till date) and `"gtc"` (good till cancelled`
        :param expiry_date: `string` or `None`: date until which the order is valid if `expiry` is `"gtd"`
        `list of strings` (optional): may contain one or more of the following values: `"targetMarket"`, `"userExperience"`, `"unknown"` - however an empty list also seems to always be accepted

        :return: Response from the API
        """

        response = await self.api.market_order(
            isin, exchange, order_type, size, expiry, sell_fractions, expiry_date, warnings_shown
        )

        logger.info(f"Created market order with ISIN {isin} on exchange {exchange} for {size} shares.")
        logger.debug(f"Response: {response}")
        if self.is_debug:
            TRUtils.save_data(response, "debug_create_market_order.json", self.output_folder)

        return response

    async def create_stop_market_order(
        self,
        isin: str,
        exchange: str,
        order_type: str,
        size: int,
        stop: float,
        expiry: str,
        expiry_date: str = "",
        warnings_shown: list = [],
    ) -> dict:
        """
        Creates a stop-market order.
        :param isin: ISIN of the instrument
        :param exchange: Exchange ("LSX" by default)
        :param order_type: Order type ("buy" or "sell")
        :param size: Number of shares
        :param stop: Stop price
        :param expiry: Order duration ("gfd", "gtd", "gtc")
        :param expiry_date: Expiration date if "gtd"
        :param warnings_shown: Accepted warnings
        :return: API response
        """
        response = await self.api.stop_market_order(
            isin, exchange, order_type, size, stop, expiry, expiry_date, warnings_shown
        )
        logger.info(
            f"Created stop-market order with ISIN {isin} on exchange {exchange} for {size} shares at stop price {stop}."
        )
        logger.debug(f"Response: {response}")
        if self.is_debug:
            TRUtils.save_data(response, "debug_create_stop_market_order.json", self.output_folder)
        return response

    async def cancel_order(self, order_id: str) -> dict:
        """
        Cancels an existing order.

        :param order_id: ID of the order to cancel
        :return: API response
        """
        try:
            logger.info(f"Canceling order {order_id}.")
            response = await self.api.cancel_order(order_id)
            logger.info(f"Order {order_id} canceled successfully.")
            if self.is_debug:
                TRUtils.save_data(response, f"debug_cancel_order_{order_id}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return {}

    ##
    # Savings Plans Management
    ##

    async def get_savings_plan_parameters(self, isin: str) -> dict:
        """
        Fetches the parameters for a savings plan.

        :param isin: ISIN of the instrument
        :return: Savings plan parameters
        """
        try:
            logger.info(f"Fetching savings plan parameters for ISIN {isin}.")
            response = await self.api.savings_plan_parameters(isin)
            logger.info(f"Savings plan parameters fetched for ISIN {isin}.")
            if self.is_debug:
                TRUtils.save_data(response, f"savings_plan_parameters_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error fetching savings plan parameters: {e}")
            return {}

    async def fetch_savings_plans(self) -> dict:
        """
        Fetches the list of savings plans.

        :return: Savings plans
        """
        try:
            logger.debug("Fetching savings plans.")
            response = await self.api.savings_plan_overview()
            logger.info(f"Fetched {len(response.get('savingsPlans', []))} savings plans.")
            if self.is_debug:
                TRUtils.save_data(response, "savings_plans_overview.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error fetching savings plans: {e}")
            return {}

    async def create_savings_plan(
        self,
        isin: str,
        amount: float,
        interval: str,
        start_date: str,
        start_date_type: str,
        start_date_value: str,
        warnings_shown: list = [],
    ) -> dict:
        """
        Creates a savings plan.

        :param isin: ISIN of the instrument
        :param amount: Amount to save
        :param interval: Interval ('weekly', 'monthly', 'quaterly', 'yearly')
        :param start_date: Start date
        :param start_date_type: Start date type
        :param start_date_value: Start date value
        :param warnings_shown: Accepted warnings
        :return: API response
        """
        try:
            logger.info(f"Creating a savings plan for ISIN {isin} with amount {amount} EUR.")
            response = await self.api.create_savings_plan(
                isin, amount, interval, start_date, start_date_type, start_date_value, warnings_shown
            )
            logger.info(f"Savings plan created successfully for ISIN {isin}.")
            if self.is_debug:
                TRUtils.save_data(response, f"savings_plan_created_{isin}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error creating savings plan: {e}")
            return {}

    async def change_savings_plan(
        self,
        savings_plan_id: str,
        isin: str,
        amount: float,
        interval: str,
        start_date: str,
        start_date_type: str,
        start_date_value: str,
        warnings_shown: list = [],
    ) -> dict:
        """
        Modifies a savings plan.

        :param savings_plan_id: ID of the savings plan
        :param isin: ISIN of the instrument
        :param amount: Amount to save
        :param interval: Interval
        :param start_date: Start date
        :param start_date_type: Start date type
        :param start_date_value: Start date value
        :param warnings_shown: Accepted warnings
        :return: API response
        """
        try:
            logger.info(f"Modifying savings plan {savings_plan_id}.")
            response = await self.api.change_savings_plan(
                savings_plan_id, isin, amount, interval, start_date, start_date_type, start_date_value, warnings_shown
            )
            logger.info(f"Savings plan {savings_plan_id} modified successfully.")
            if self.is_debug:
                TRUtils.save_data(response, f"savings_plan_modified_{savings_plan_id}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error modifying savings plan: {e}")
            return {}

    async def cancel_savings_plan(self, savings_plan_id: str) -> dict:
        """
        Cancels a savings plan.

        :param savings_plan_id: ID of the savings plan
        :return: API response
        """
        try:
            logger.info(f"Canceling savings plan {savings_plan_id}.")
            response = await self.api.cancel_savings_plan(savings_plan_id)
            logger.info(f"Savings plan {savings_plan_id} canceled successfully.")
            if self.is_debug:
                TRUtils.save_data(response, f"savings_plan_cancelled_{savings_plan_id}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error canceling savings plan: {e}")
            return {}
