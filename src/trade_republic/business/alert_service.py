from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class AlertService(TRAbstractService):
    """
    Service for managing Trade Republic alerts.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_price_alarms(self) -> dict:
        """
        Fetches all price alerts.

        :return: Dictionary containing price alerts
        """
        try:
            data = await self.api.price_alarm_overview()
            logger.info(f"Fetched {len(data.get('priceAlarms', []))} price alerts.")
            if self.is_debug:
                TRUtils.save_data(data, "price_alarms_overview.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching price alerts: {e}")
            return {}

    async def create_price_alert(self, isin: str, price: float) -> dict:
        """
        Creates a price alert for an instrument.

        :param isin: ISIN code of the instrument
        :param price: Target price for the alert
        :return: API response
        """
        try:
            logger.info(f"Creating price alert for ISIN {isin} at price {price} EUR.")
            response = await self.api.create_price_alarm(isin, price)
            logger.info(f"Price alert successfully created for ISIN {isin}.")
            if self.is_debug:
                TRUtils.save_data(response, f"alert_created_{isin}_{price}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return {}

    async def cancel_price_alert(self, price_alarm_id: str) -> dict:
        """
        Cancels a price alert.

        :param price_alarm_id: ID of the price alert to cancel
        :return: API response
        """
        try:
            logger.info(f"Canceling price alert {price_alarm_id}.")
            response = await self.api.cancel_price_alarm(price_alarm_id)
            logger.info(f"Price alert {price_alarm_id} successfully canceled.")
            if self.is_debug:
                TRUtils.save_data(response, f"alert_cancelled_{price_alarm_id}.json", self.output_folder)
            return response
        except Exception as e:
            logger.error(f"Error canceling alert: {e}")
            return {}
