from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

def get_browser(download_dir: str, headless: bool = True, profile_dir: str = None) -> webdriver.Chrome:
    options = Options()
    
    # Set download preferences
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    })

    # Use persistent user profile if provided
    if profile_dir:
        abs_profile_dir = os.path.abspath(profile_dir)
        options.add_argument(f"--user-data-dir={abs_profile_dir}")

    # Add headless and other performance-related flags
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,800")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    return driver
