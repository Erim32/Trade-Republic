from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class TransactionService(TRAbstractService):
    """
    Service for managing Trade Republic transactions.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_transactions(self, extract_details: bool = False):
        """
        Fetches all transactions and saves them.

        :param extract_details: If True, fetches details for each transaction.
        """
        all_data = []
        after_cursor = None

        while True:
            data = await self.api.get_transactions(after_cursor)

            if not data.get("items"):
                break

            if extract_details:
                for transaction in data["items"]:
                    transaction_id = transaction.get("id")
                    if transaction_id:
                        details = await self.api.get_transaction_details(transaction_id)
                        transaction.update(details)
                    all_data.append(transaction)
            else:
                all_data.extend(data["items"])

            after_cursor = data.get("cursors", {}).get("after")
            if not after_cursor:
                break

        if self.is_debug:
            logger.info(f"Successfully fetched transactions. Number of transactions: {len(all_data)}")
            TRUtils.save_data(all_data, "trade_republic_transactions.json", self.output_folder)

        return all_data

    async def fetch_transaction(self, transaction_id: str) -> dict:
        """
        Fetches transaction details
        """
        data = await self.api.get_transaction_details(transaction_id)

        if self.is_debug:
            TRUtils.save_data(data, f"transaction_{transaction_id}.json", self.output_folder)

        return data

    async def fetch_timeline(self, after: str = "") -> dict:
        """
        Fetches the transaction timeline.

        :param after: Cursor for paginating results
        :return: Timeline with transactions
        """
        try:
            logger.debug("Fetching timeline.")
            data = await self.api.timeline(after=after)
            if self.is_debug:
                TRUtils.save_data(data, f"timeline{('_' + after) if after else ''}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching timeline: {e}")
            return {}

    async def fetch_timeline_detail(self, timeline_id: str) -> dict:
        """
        Fetches timeline details.

        :param timeline_id: Timeline ID
        :return: Timeline details
        """
        try:
            logger.debug(f"Fetching timeline details for {timeline_id}.")
            data = await self.api.timeline_detail(timeline_id)
            if self.is_debug:
                TRUtils.save_data(data, f"timeline_detail_{timeline_id}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching timeline details: {e}")
            return {}

    async def fetch_timeline_detail_order(self, order_id: str) -> dict:
        """
        Fetches timeline details for an order.

        :param order_id: Order ID
        :return: Timeline details
        """
        try:
            logger.debug(f"Fetching timeline details for order {order_id}.")
            data = await self.api.timeline_detail_order(order_id)
            if self.is_debug:
                TRUtils.save_data(data, f"timeline_detail_order_{order_id}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching timeline details: {e}")
            return {}

    async def fetch_timeline_detail_savings_plan(self, savings_plan_id: str) -> dict:
        """
        Fetches timeline details for a savings plan.

        :param savings_plan_id: Savings plan ID
        :return: Timeline details
        """
        try:
            logger.debug(f"Fetching timeline details for savings plan {savings_plan_id}.")
            data = await self.api.timeline_detail_savings_plan(savings_plan_id)
            if self.is_debug:
                TRUtils.save_data(data, f"timeline_detail_savings_plan_{savings_plan_id}.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching timeline details: {e}")
            return {}
