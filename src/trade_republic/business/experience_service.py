from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class ExperienceService(TRAbstractService):
    """
    Service for managing Trade Republic user experience.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def fetch_experience(self) -> dict:
        """
        Fetches the user experience configuration.

        :return: Experience configuration
        """
        try:
            logger.debug("Fetching experience configuration.")
            data = await self.api.experience()
            if self.is_debug:
                TRUtils.save_data(data, "experience_config.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching experience configuration: {e}")
            return {}

    async def fetch_message_of_the_day(self) -> dict:
        """
        Fetches the message of the day.

        :return: Message of the day
        """
        try:
            logger.debug("Fetching message of the day.")
            data = await self.api.motd()
            if self.is_debug:
                TRUtils.save_data(data, "message_of_the_day.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching message of the day: {e}")
            return {}

    async def fetch_neon_cards(self) -> dict:
        """
        Fetches Neon cards (user interface content).

        :return: Neon cards
        """
        try:
            logger.debug("Fetching Neon cards.")
            data = await self.api.neon_cards()
            if self.is_debug:
                TRUtils.save_data(data, "neon_cards.json", self.output_folder)
            return data
        except Exception as e:
            logger.error(f"Error fetching Neon cards: {e}")
            return {}
