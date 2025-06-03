from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Optional
from base import InvoicePortal
from datetime import datetime
import time
import locale
import os

# Set German locale to parse German month names
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except:
    pass  # On some systems this may not be available

class ZoomPortal(InvoicePortal):
    def download_invoices(self, driver: WebDriver) -> Optional[int]:

        print("\n\n🚀 Zoom Portal")
        print("🌐 Öffne Zoom Loginseite...")
        driver.get("https://www.zoom.us/signin#/login")
        time.sleep(5)

        print("🍪 Versuche Cookie-Banner zu akzeptieren...")
        try:
            cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_button.click()
            time.sleep(2)
        except Exception:
            print("ℹ️ Kein Cookie-Banner oder bereits akzeptiert")

        time.sleep(2)

        # skip login if already logged in
        if "https://zoom.us/signin#/login" in driver.current_url:
            
            print("🔐 Fülle Loginformular aus...")
            driver.find_element(By.ID, "email").send_keys(self.username)
            time.sleep(2)
            driver.find_element(By.ID, "password").send_keys(self.password)
            time.sleep(2)
            #driver.find_element(By.ID, "js_btn_login").click()
            driver.execute_script("document.getElementById('js_btn_login').click()")
            print("⏳ Warte auf Login...")
            time.sleep(15)

        print("📄 Lade Rechnungsseite...")
        driver.get("https://www.zoom.us/billing/report")
        time.sleep(15)


        rows = driver.find_elements(By.CSS_SELECTOR, "tr.zm-table__row")
        print(f"📑 {len(rows)} Rechnungszeilen gefunden")

        search_month, search_year = map(int, self.target_month.split('.'))

        # print the table html
        for row in rows:
            try:
                # print the row html    
                date_td = row.find_element(By.CSS_SELECTOR, ".zm-table_1_column_3 .cell")
                date_text = date_td.text.strip()  # e.g. "8. Dezember 2024"
                invoice_date = datetime.strptime(date_text, "%B %d, %Y")

                if invoice_date.year < search_year or (invoice_date.year == search_year and invoice_date.month < search_month):
                    print(f"🛑 Rechnung von {date_text} ist vor dem Zielmonat.")
                    break
                if invoice_date.year > search_year or (invoice_date.year == search_year and invoice_date.month > search_month):
                    print(f"⏭️ Rechnung von {date_text} ist nach dem Zielmonat.")
                    continue

                print(f"📥 Lade Rechnung vom {date_text}...")
                # print download directory
                
                download_button = row.find_element(By.CSS_SELECTOR, ".zm-button")
                download_button.click()
                time.sleep(10)
                return 1
            except Exception as e:
                print(f"⚠️ Fehler beim Verarbeiten einer Zeile: {e}")

        print("ℹ️ Keine passende Rechnung für den Zielmonat gefunden.")
        return 0
