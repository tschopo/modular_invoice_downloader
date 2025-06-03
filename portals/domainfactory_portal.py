from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from typing import Optional
import time
from base import InvoicePortal
from datetime import datetime

class DomainFactoryPortal(InvoicePortal):
    def download_invoices(self, driver: WebDriver) -> Optional[int]:

        print("\n\n🚀 Domainfactory Portal")

        print("🌐 Öffne DomainFactory Rechnungsseite...")
        driver.get("https://sso.df.eu/?app=cp&path=%2Fkunde%2Findex.php%3Fmodule%3Drechnungen&realm=idp")
        time.sleep(3)

        # Check for SSO redirect (login page)
        if "sso.df.eu" in driver.current_url:
            print("🔐 Login erforderlich...")
            driver.find_element(By.ID, "1").send_keys(self.username)
            time.sleep(1)
            driver.find_element(By.ID, "2").send_keys(self.password)
            time.sleep(1.5)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(5)
            print("🔓 Login gesendet")

        # Optional: Datenweitergabe bestätigen
        try:
            radio = driver.find_element(By.NAME, "daten_checked")
            radio.click()
            time.sleep(1)
            driver.find_element(By.ID, "weiterAuftrag").click()
            print("✅ Datenschutzbestätigung abgeschlossen")
            time.sleep(3)
        except Exception:
            print("ℹ️ Keine Datenschutzseite")

        # Click on year button
        search_month, search_year = map(int, self.target_month.split('.'))
        print(f"📅 Suche Rechnungen für: {self.target_month}")
        try:
            year_button = driver.find_element(By.XPATH, f"//button[contains(@class, 'group-opener') and contains(., '{search_year}')]")
            year_button.click()
            print(f"🗂️ Jahr {search_year} geöffnet")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Jahr-Button nicht gefunden: {e}")
            return 0

        # Format target for matching (e.g. '09.04.2025')
        month_padded = f"{search_month:02d}"
        match_str = f".{month_padded}.{search_year}"

        links = driver.find_elements(By.CSS_SELECTOR, "a.astab.link")
        matched = 0
        for link in links:
            try:
                # debug print
                print(link.get_attribute("data-tabtitle"))

                tab_title = link.get_attribute("data-tabtitle")
                if not tab_title:
                    continue


                # Check if the link contains the target month
                # # Extract date from tab_title
                try:
                    date_part = tab_title.replace("Rechnung vom ", "").strip()  # "09.04.2025"
                    invoice_date = datetime.strptime(date_part, "%d.%m.%Y")
                except Exception as e:
                    print(f"⚠️ Konnte Datum nicht parsen aus: {tab_title}")
                    continue

                # Compare with target month
                target_month, target_year = map(int, self.target_month.split('.'))

                if invoice_date.year < target_year or (invoice_date.year == target_year and invoice_date.month < target_month):
                    print(f"🛑 Rechnung vor Zielmonat {self.target_month} – abbrechen.")
                    break

                if invoice_date.year > target_year or (invoice_date.year == target_year and invoice_date.month > target_month):
                    print(f"⏭️ Überspringe {invoice_date.strftime('%d.%m.%Y')} – nach Zielmonat.")
                    continue

                # If equal: download PDF
                parent_td = link.find_element(By.XPATH, "..")
                pdf_links = parent_td.find_elements(By.TAG_NAME, "a")
                for a in pdf_links:
                    if "PDF" in a.text:
                        print(f"📥 Lade Rechnung vom {invoice_date.strftime('%d.%m.%Y')}...")
                        a.click()
                        time.sleep(3)
                        matched += 1
                        break
              
            except Exception as e:
                print(f"⚠️ Fehler beim Laden einer Rechnung: {e}")

        print(f"✅ {matched} Rechnungen geladen.")
        return matched
