from selenium.webdriver.common.by import By
from time import sleep
import os
from typing import Optional
from base import InvoicePortal
from selenium.webdriver.common.by import By
import os
import time
from selenium.webdriver.chrome.webdriver import WebDriver


class SpiegelPortal(InvoicePortal):

    def login(self, driver: WebDriver, goto_login = True) -> None:

        # --- Loginseite ---
        print("🌐 Öffne Loginseite...")

        if goto_login:
            url = "https://gruppenkonto.spiegel.de/anmelden.html"
            driver.get(url)
            sleep(3)

        username_input = driver.find_element(By.ID, "username")        

        # Debug: Seitenquelle ausgeben, wenn Login-Formular nicht gefunden wird
        if "username" not in driver.page_source:
            print("⚠️ Login-Formular nicht im Quellcode gefunden.")
        else:
            # --- Login ---
            print("🔐 Fülle Loginformular aus...")
            try:
                username_input = driver.find_element(By.ID, "username")
            except Exception as e:
                print("❌ Fehler beim Finden des Loginformulars:", e)

            username_input.send_keys(self.username)
            print("🔓 Sende Benutzername ab...")

            # click on the submit button (button with id submit)
            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()

            # Warte auf Weiterleitung nach Login
            print("⏳ Warte auf Weiterleitung zum passwort Formular...")
            time.sleep(7)

            # Passwortfeld finden
            password_input = driver.find_element(By.ID, "password")
            password_input.send_keys(self.password)
            print("🔓 Sende Passwort ab...")

            # click on the submit button (button with id submit)
            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()

            print("⏳ Warte auf Weiterleitung...")
            time.sleep(7)

    def download_invoices(self, driver: WebDriver) -> Optional[int]:
        print("\n\n🚀 Spiegel Portal")

        # Login
        self.login(driver)
        print("🔐 Eingeloggt, suche nach Rechnungen...")

        try:
            
            # rechnungsseiten
            rechnungsseiten = [
                "https://gruppenkonto.spiegel.de/meinkonto/abonnements/rechnungen2.html?dnt_uSubId=P-2425840",
                "https://gruppenkonto.spiegel.de/meinkonto/abonnements/rechnungen2.html?dnt_uSubId=P-2425839"
            ]

            # Rechnungsseiten durchlaufen
            for rechnungsseite in rechnungsseiten:
                print(f"🌐 Gehe zur Rechnungsseite: {rechnungsseite}...")
                driver.get(rechnungsseite)
                time.sleep(10)  # Wartezeit für das Laden der Seite

                # Rechnungen herunterladen
                print("📄 Suche nach Rechnungen...")

                # loop through the rows of the .cms-table
                rows = driver.find_elements(By.CSS_SELECTOR, ".cms-table tbody tr")

                # print number of rows
                print(f"🔍 Gefundene Rechnungen: {len(rows)}")                

                search_month, search_year = map(int, self.target_month.split('.'))

                for row in rows[1:]:                    

                    # check the date (first column)
                    date_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(1)")

                    rechnungs_datum = date_cell.text
                    #trim
                    rechnungs_datum = rechnungs_datum.strip()

                    day, month, year = map(int, rechnungs_datum.split('.'))
                        
                    # Vergleiche Monat und Jahr mit Suchmonat
                    if year < search_year or (year == search_year and month < search_month):
                        print(f"🛑 Rechnungen vor {self.target_month} gefunden, Suche wird beendet.")
                        break  # Stoppe die Schleife, wenn Monate kleiner als Suchmonat sind
                    
                    if year > search_year or (year == search_year and month > search_month):
                        print(f"⏭️ Überspringe Rechnung vom {rechnungs_datum}, da nach Zielmonat.")
                        continue  # Ignoriere und fahre fort, wenn Monate größer als Suchmonat sind
                    
                    # check if the date is in the target month
                    if self.target_month in rechnungs_datum:
                        print(f"📥 Rechnung gefunden für {rechnungs_datum}, starte Download...")
                        # Download-Link (letzte Spalte)
                        download_link = row.find_element(By.CSS_SELECTOR, "td:nth-last-child(1) a")
                        download_url = download_link.get_attribute("href")
                        # Download der Rechnung
                        if download_url:
                            driver.get(download_url)
                            time.sleep(15)  # Wartezeit für das Laden der Seite
                            print(f"✅ Rechnung für {rechnungs_datum} heruntergeladen.")
                

        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {str(e)}")
            
        finally:
            print("✅ Spiegel Rechnungsportal geschlossen.")