from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger


class TestService(TRAbstractService):
    """
    Service for test / development management.
    """

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        super().__init__(api, output_folder, is_debug)

    async def test(self) -> str:
        data = await self.api.create_price_alarm("XF000BTC0017", 50000.0)
        logger.debug(f"Test result: {data}")
        return data
