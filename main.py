from abc import ABC, abstractmethod
from typing import Optional
import yaml
import os
from datetime import datetime, timedelta
from portals.dhl_portal import DHLPortal
from portals.spiegel_portal import SpiegelPortal
from portals.github_portal import GithubPortal
from portals.zoom_portal import ZoomPortal
from portals.domainfactory_portal import DomainFactoryPortal
from portals.awin_portal import AwinPortal

from utils.browser import get_browser

def load_credentials(path: str = "credentials.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_target_month() -> tuple[str, str]:
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    month_str = last_day_last_month.strftime("%m.%Y")
    download_folder = last_day_last_month.strftime("%Y-%m")
    return month_str, download_folder


def main():
    creds = load_credentials()
    month_str, download_folder = get_target_month()
    download_dir = os.path.join(os.getcwd(), f"belege/{download_folder}")
    os.makedirs(download_dir, exist_ok=True)

    print(f"🗓️ Suche nach Rechnungen für: {month_str}")
    print(f"📁 Zielordner: {download_dir}")

    driver = get_browser(download_dir, headless=False, profile_dir="~/selenium-profiles/zoom")
    #driver = get_browser(download_dir, headless=True)

    try:
        dhl = DHLPortal(
            username=creds["dhl"]["username"],
            password=creds["dhl"]["password"],
            download_dir=download_dir,
            target_month=month_str
        )
        spiegel = SpiegelPortal(
            username=creds["spiegel"]["username"],
            password=creds["spiegel"]["password"],
            download_dir=download_dir,
            target_month=month_str
        )

        zoom = ZoomPortal(
            username=creds["zoom"]["username"],
            password=creds["zoom"]["password"],
            download_dir=download_dir,
            target_month=month_str,
        )

        # df
        df = DomainFactoryPortal(
            username=creds["df"]["username"],
            password=creds["df"]["password"],
            download_dir=download_dir,
            target_month=month_str,
        )

        # awin
        awin = AwinPortal(
            username=creds["awin"]["username"],
            password=creds["awin"]["password"],
            download_dir=download_dir,
            target_month=month_str,
        )

        # tradedoubler

        # github

        github = GithubPortal(
            username=creds["github"]["username"],
            password=creds["github"]["password"],
            download_dir=download_dir,
            target_month=month_str,
        )

        #dhl.download_invoices(driver)
        #spiegel.download_invoices(driver)
        #github.download_invoices(driver)
        #zoom.download_invoices(driver)
        #df.download_invoices(driver)
        awin.download_invoices(driver)

    finally:
        print("🔚 Schließe Browser...")
        driver.quit()


if __name__ == "__main__":
    main()
