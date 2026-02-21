import os
from abc import ABC

from trade_republic.models.tr_exceptions import ServiceInitializationError
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger


class TRAbstractService(ABC):
    """
    Abstract class for business services.
    Provides common functionality for specific services.
    """

    api: TRApi
    output_folder: str
    is_debug: bool = os.getenv("LOG_LEVEL", "INFO").upper() == "DEBUG"

    def __init__(self, api: TRApi, output_folder: str, is_debug: bool = False):
        self.api = api
        self.output_folder = output_folder
        self.is_debug = is_debug

        if self.api is None:
            raise ServiceInitializationError("TRApi instance cannot be None. Authentication may have failed.")

        if self.is_debug:
            logger.debug(f"TRAbstractService initialized with output folder: {self.output_folder}")

    def get_api(self) -> TRApi:
        """
        Returns the TR_API instance used by the service.
        """
        return self.api

    def get_output_folder(self) -> str:
        """
        Returns the output folder configured for the service.
        """
        return self.output_folder

    @staticmethod
    def login(phone_number: str = "", pin: str = "", max_concurrent_connections: int = 5):
        """
        Establishes connection to the Trade Republic API.

        :param phone_number: Phone number
        :param pin: Login PIN
        :param max_concurrent_connections: Maximum number of simultaneous WebSocket connections (default: 5)
        """
        return TRApi.login(phone_number=phone_number, pin=pin, max_concurrent_connections=max_concurrent_connections)
