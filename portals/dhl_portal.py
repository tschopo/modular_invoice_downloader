from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from time import sleep
from typing import Optional
import os
from base import InvoicePortal


class DHLPortal(InvoicePortal):
    def download_invoices(self, driver: WebDriver) -> Optional[int]:

        try:
            LOGIN_URL = "https://sso.geschaeftskunden.dhl.de/auth/realms/GkpExternal/protocol/openid-connect/auth?client_id=gui&redirect_uri=https%3A%2F%2Fgeschaeftskunden.dhl.de%2Fbilling%2Finvoice%2Foverview&state=1f653d81-1476-477d-9ff2-f6ab4a9bc6c5&response_mode=fragment&response_type=code&scope=openid&nonce=f6fab592-b151-42f8-9a92-cfa93e573fc7&ui_locales=de-DE&code_challenge=0SPP9JWSDRLdj0PSVuURa94IslWfTQGywTpR09AfNgA&code_challenge_method=S256"
            driver.get(LOGIN_URL)
            sleep(3)

            username_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.submit()

            # --- Loginseite ---
            print("🌐 Öffne Loginseite...")
            driver.get(LOGIN_URL)
            sleep(3)

            # Debug: Seitenquelle ausgeben, wenn Login-Formular nicht gefunden wird
            if "username" not in driver.page_source:
                print("⚠️ Login-Formular nicht im Quellcode gefunden.")
            else:
                # --- Login ---
                print("🔐 Fülle Loginformular aus...")
                try:
                    username_input = driver.find_element(By.ID, "username")
                    password_input = driver.find_element(By.ID, "password")
                except Exception as e:
                    print("❌ Fehler beim Finden des Loginformulars:", e)

                username_input.send_keys(self.username)
                password_input.send_keys(self.password)
                print("🔓 Sende Loginformular ab...")
                password_input.submit()

                # Warte auf Weiterleitung nach Login
                print("⏳ Warte auf Weiterleitung nach Login...")
                sleep(10)
            
            # Cookie-Banner akzeptieren
            try:
                print("🍪 Suche nach Cookie-Banner...")
                cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                print("🍪 Cookie-Banner gefunden, klicke auf 'Akzeptieren'...")
                cookie_button.click()
                sleep(2)
                print("✅ Cookies akzeptiert")
            except Exception as e:
                print("ℹ️ Kein Cookie-Banner gefunden oder bereits akzeptiert:", e)

            # --- Tabelle laden ---
            print("📄 Suche nach Rechnungstabelle...")
            print("⏱️ Warte 15 Sekunden, damit die Seite vollständig laden kann...")
            sleep(15)  # Längere Wartezeit für langsame Verbindungen

            # Debug: Screenshot machen, wenn verfügbar
            if not driver.current_url.startswith("data:"):
                try:
                    screenshot_path = os.path.join(os.getcwd(), "debug_screenshot.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"📸 Debug-Screenshot gespeichert: {screenshot_path}")
                except Exception as e:
                    print("⚠️ Konnte keinen Screenshot erstellen:", e)
            
            try:
                # Versuche, die Tabelle zu finden
                rows = driver.find_elements(By.CSS_SELECTOR, ".dhlTable tbody tr")
                
                if not rows:
                    print("⚠️ Tabelle gefunden, aber keine Zeilen. Versuche alternative Selektoren...")
                    # Alternative Selektoren probieren
                    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            except Exception as e:
                print("❌ Fehler beim Suchen der Tabelle:", e)
                rows = []
                    
            if not rows:
                print("❌ Keine Rechnungszeilen gefunden – evtl. nicht eingeloggt oder keine Daten vorhanden.")
                print("Aktueller HTML-Inhalt:")
                print(driver.page_source[:1000] + "...")  # Ersten 1000 Zeichen ausgeben
            else:
                print(f"📊 {len(rows)} Rechnungszeilen gefunden. Prüfe nach Monat {self.target_month}...")
                downloads_count = 0
                
                search_month, search_year = map(int, self.target_month.split('.'))
                
                for row in rows:
                    try:
                        # Versuche Standard-Selektor
                        date_td = row.find_element(By.CSS_SELECTOR, "td.clickDVNotDis")
                    except Exception:
                        try:
                            # Fallback: Versuche ersten TD-Element
                            date_cells = row.find_elements(By.TAG_NAME, "td")
                            if date_cells:
                                date_td = date_cells[0]  # Vermutlich das Datums-Element
                            else:
                                print("⚠️ Keine TD-Elemente in dieser Zeile gefunden, überspringe...")
                                continue
                        except Exception as e:
                            print("⚠️ Fehler beim Verarbeiten einer Zeile:", e)
                            continue
                    
                    rechnungs_datum = date_td.text.strip()

                    # check if date is in the format "dd.mm.yyyy"
                    if not rechnungs_datum or len(rechnungs_datum.split('.')) != 3:
                        print("⚠️ Ungültiges Datumsformat gefunden, überspringe...")
                        continue

                    try:
                        day, month, year = map(int, rechnungs_datum.split('.'))
                        
                        # Vergleiche Monat und Jahr mit Suchmonat
                        if year < search_year or (year == search_year and month < search_month):
                            print(f"🛑 Rechnungen vor {self.target_month} gefunden, Suche wird beendet.")
                            break  # Stoppe die Schleife, wenn Monate kleiner als Suchmonat sind
                        
                        if year > search_year or (year == search_year and month > search_month):
                            print(f"⏭️ Überspringe Rechnung vom {rechnungs_datum}, da nach Zielmonat.")
                            continue  # Ignoriere und fahre fort, wenn Monate größer als Suchmonat sind
                    except Exception as e:
                        print(f"⚠️ Fehler beim Parsen des Datums {rechnungs_datum}: {e}")
                        continue


                    print("🔎 Gefundene Rechnung:", rechnungs_datum)
                    
                    if self.target_month in rechnungs_datum:
                        print(f"✅ Lade PDF für {rechnungs_datum}...")
                        try:
                            pdf_button = row.find_element(By.CSS_SELECTOR, ".svgIcon-pdf")
                        except Exception:
                            try:
                                # Alternative Selektoren für den PDF-Button
                                pdf_button = row.find_element(By.CSS_SELECTOR, "[title*='PDF']")
                            except Exception:
                                print("⚠️ Konnte PDF-Button nicht finden, versuche letzten Button in der Zeile...")
                                buttons = row.find_elements(By.TAG_NAME, "button")
                                if buttons:
                                    pdf_button = buttons[-1]  # Letzter Button könnte PDF sein
                                else:
                                    print("❌ Keine Buttons in dieser Zeile gefunden, überspringe...")
                                    continue
                        
                        pdf_button.click()
                        sleep(2)
                        downloads_count += 1
                    else:
                        print("⏭️ Überspringe, da nicht im Zielmonat.")
                        
                
                print(f"✅ {downloads_count} Rechnungen für {self.target_month} heruntergeladen.")

        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {str(e)}")
            
        finally:
            print("✅ DHL Rechnungsportal geschlossen.")