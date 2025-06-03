from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime
from typing import Optional
from base import InvoicePortal
import time
from calendar import month_abbr


class AwinPortal(InvoicePortal):
    def parse_awin_date(self, text: str) -> datetime:
        parts = text.strip().split()
        if len(parts) != 3:
            raise ValueError(f"Unerwartetes Datumsformat: {text}")
        day = int(parts[0])
        month = list(month_abbr).index(parts[1])  # 'Mar' → 3
        year = int(parts[2])
        return datetime(year, month, day)

    def download_invoices(self, driver: WebDriver) -> Optional[int]:
        print("🌐 Öffne Awin Loginseite...")
        driver.get("https://ui.awin.com/idp/us/awin/login/prelogin?redirect=%2Flogin%3FnetworkGroup%3Dawin")
        time.sleep(3)

        # Schritt 1: E-Mail eingeben und weiter
        print("📧 Trage E-Mail ein...")
        driver.find_element(By.ID, "email").send_keys(self.username)
        driver.find_element(By.ID, "login").click()
        time.sleep(5)

        # Prüfe, ob Passwortseite erscheint
        if "password" in driver.page_source:
            print("🔐 Trage Passwort ein...")
            driver.find_element(By.ID, "password").send_keys(self.password)
            driver.find_element(By.CLASS_NAME, "_button-login-password").click()
            time.sleep(10)
        else:
            print("✅ Bereits eingeloggt oder Passwort nicht erforderlich.")

        # Rechnungsseite öffnen
        print("📄 Öffne Zahlungsseite...")
        driver.get("https://ui.awin.com/finance/publisher/588499/payments/history/network/awin?paymentRegion=2")
        time.sleep(10)

        rows = driver.find_elements(By.CSS_SELECTOR, "#paymentHistory table tbody tr")
        print(f"📑 {len(rows)} Rechnungszeilen gefunden")

        search_month, search_year = map(int, self.target_month.split('.'))
        count = 0

        for row in rows:
            try:
                date_td = row.find_elements(By.TAG_NAME, "td")[0]
                date_str = date_td.text.strip()  # z. B. "17 Mar 2025"
                invoice_date = self.parse_awin_date(date_str)

                if invoice_date.year < search_year or (invoice_date.year == search_year and invoice_date.month < search_month):
                    print(f"🛑 Rechnung von {date_str} ist vor dem Zielmonat.")
                    break
                if invoice_date.year > search_year or (invoice_date.year == search_year and invoice_date.month > search_month):
                    print(f"⏭️ Rechnung von {date_str} ist nach dem Zielmonat.")
                    continue

                # Download-Link (letzter <a> in letzter Zelle)
                last_td = row.find_elements(By.TAG_NAME, "td")[-1]
                download_link = last_td.find_elements(By.TAG_NAME, "a")[-1]
                href = download_link.get_attribute("href")

                if href:
                    print(f"📥 Lade Rechnung vom {date_str} herunter...")
                    driver.get(href)
                    time.sleep(5)
                    count += 1
                    break

            except Exception as e:
                print(f"⚠️ Fehler beim Verarbeiten einer Zeile: {e}")
                continue

        if count == 0:
            print("ℹ️ Keine passende Rechnung für den Zielmonat gefunden.")
        else:
            print(f"✅ {count} Awin-Rechnung(en) heruntergeladen.")

        return count
