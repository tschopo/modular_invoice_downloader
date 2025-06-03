from abc import ABC, abstractmethod
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver

class InvoicePortal(ABC):
    def __init__(self, username: str, password: str, download_dir: str, target_month: str) -> None:
        self.username = username
        self.password = password
        self.download_dir = download_dir
        self.target_month = target_month

    @abstractmethod
    def download_invoices(self, driver: WebDriver) -> Optional[int]:        pass
