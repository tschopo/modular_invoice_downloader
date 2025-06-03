from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Optional
import time
import os
from datetime import datetime
from base import InvoicePortal


class GithubPortal(InvoicePortal):
    def download_invoices(self, driver: WebDriver) -> Optional[int]:
        print("\n\n🚀 GitHub Portal")
        print("🌐 Öffne GitHub Loginseite...")
        driver.get("https://github.com/login")
        time.sleep(3)

        print("🔐 Fülle Loginformular aus...")
        driver.find_element(By.ID, "login_field").send_keys(self.username)
        driver.find_element(By.ID, "password").send_keys(self.password + Keys.RETURN)
        time.sleep(5)

        print("🔍 Navigiere zur Rechnungsübersicht...")
        driver.get("https://github.com/account/billing/history")
        time.sleep(5)

        search_month, search_year = map(int, self.target_month.split('.'))
        count = 0

        items = driver.find_elements(By.CSS_SELECTOR, "li.Box-row")
        print(f"📄 {len(items)} Rechnungszeilen gefunden")


        for item in items:

            try:
                date_elements = item.find_elements(By.CSS_SELECTOR, ".date time")
                if not date_elements:
                    print("⚠️ Keine Datumsangaben gefunden, überspringe...")
                    continue  # skip items without a date

                date_text = date_elements[0].text
                invoice_date = datetime.strptime(date_text.strip(), "%Y-%m-%d")

                if invoice_date.year == search_year and invoice_date.month == search_month:
                    print(f"📥 Lade Rechnung vom {invoice_date.strftime('%d.%m.%Y')}...")

                    link = item.find_element(By.CSS_SELECTOR, "a[id^='preview-receipt']")
                    pdf_url = link.get_attribute("href")
                    if pdf_url:
                        if not pdf_url.startswith("https://"):
                            pdf_url = "https://github.com" + pdf_url

                        driver.get(pdf_url)
                    time.sleep(3)
                    return 1  # found and downloaded

            except Exception as e:
                print(f"⚠️ Fehler beim Verarbeiten einer Zeile: {e}")

        print("ℹ️ Keine Rechnung für den Zielmonat gefunden.")
        return 0


        print(f"✅ {count} GitHub-Rechnungen heruntergeladen.")
        return count
