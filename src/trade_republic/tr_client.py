from trade_republic.business._abstract_service import TRAbstractService
from trade_republic.business._test_service import TestService
from trade_republic.business.account_service import AccountService
from trade_republic.business.alert_service import AlertService
from trade_republic.business.experience_service import ExperienceService
from trade_republic.business.instrument_service import InstrumentService
from trade_republic.business.market_data_service import MarketDataService
from trade_republic.business.order_service import OrderService
from trade_republic.business.portfolio_service import PortfolioService
from trade_republic.business.search_service import SearchService
from trade_republic.business.transaction_service import TransactionService
from trade_republic.repository.tr_api import TRApi
from trade_republic.utils.logger import logger
from trade_republic.utils.tr_utils import TRUtils


class TRClient:
    """
    Main client class for interacting with the Trade Republic API.
    Provides access to various services for managing accounts, portfolios, transactions, and more.
    """

    _api: TRApi

    account_service: AccountService
    alert_service: AlertService
    experience_service: ExperienceService
    instrument_service: InstrumentService
    market_data_service: MarketDataService
    portfolio_service: PortfolioService
    search_service: SearchService
    test_service: TestService
    transaction_service: TransactionService
    order_service: OrderService

    def __init__(
        self, phone: str = "", pin: str = "", output_folder: str = "output", max_concurrent_connections: int = 5
    ) -> None:
        """
        Initializes the TRClient and establishes a connection to the Trade Republic API.
        :param phone: Phone number for login.
        :param pin: PIN for login.
        :param output_folder: Folder to save output files (default: "output").
        :param max_concurrent_connections: Maximum number of simultaneous WebSocket connections (default: 5).
        """

        self._api: TRApi = TRAbstractService.login(phone, pin, max_concurrent_connections=max_concurrent_connections)
        self.output_folder: str = output_folder

        self.account_service: AccountService = AccountService(self._api, self.output_folder)
        self.alert_service: AlertService = AlertService(self._api, self.output_folder)
        self.experience_service: ExperienceService = ExperienceService(self._api, self.output_folder)
        self.instrument_service: InstrumentService = InstrumentService(self._api, self.output_folder)
        self.market_data_service: MarketDataService = MarketDataService(self._api, self.output_folder)
        self.portfolio_service: PortfolioService = PortfolioService(self._api, self.output_folder)
        self.search_service: SearchService = SearchService(self._api, self.output_folder)
        self.test_service: TestService = TestService(self._api, self.output_folder)
        self.transaction_service: TransactionService = TransactionService(self._api, self.output_folder)
        self.order_service: OrderService = OrderService(self._api, self.output_folder)
        logger.info("TRClient initialized successfully.")

    def display_json(self, data: dict):
        """
        Utility method to display JSON data in a readable format.
        :param data: JSON data to display.
        """
        TRUtils.display_json(data)

    def save_json(self, data: dict | list, filename: str):
        """
        Utility method to save JSON data to a file.
        :param data: JSON data to save.
        :param filename: Name of the file to save the data to.
        """
        TRUtils.save_json(data, filename, self.output_folder)

    def load_json(self, filename: str) -> dict | list:
        """
        Utility method to load JSON data from a file.
        :param filename: Name of the file to load the data from.
        :return: Loaded JSON data.
        """

        return TRUtils.load_json_from_file(filename, self.output_folder)
