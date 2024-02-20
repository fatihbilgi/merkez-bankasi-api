import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets API auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("merkez-bankasi-api-9bf92c90555a.json", scope)
gc = gspread.authorize(credentials)

# Open google sheets
spreadsheet_id = "12Jp25Ei2IulYL0UbWXsI1vURE8Fl1l7UqjbVBNdQbNk"
sheet = gc.open_by_key(spreadsheet_id).sheet1

def get_exchange_rates():
    url = "https://www.tcmb.gov.tr/kurlar/today.xml"
    response = requests.get(url)

    if response.status_code == 200:
        # XML data process
        rates_data = process_data(response.text)
        update_google_sheets(rates_data)
    else:
        print("Hata oluştu - HTTP Kodu: {}".format(response.status_code))

def process_data(xml_data):
    # xml.etree.ElementTree process
    import xml.etree.ElementTree as ET

    # Parse XML
    root = ET.fromstring(xml_data)

    # Create dictionary
    exchange_rates = {}

    # Select Currencies
    desired_currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]

    # Find Currencies
    for currency_node in root.findall(".//Currency"):
        currency_code = currency_node.get("Kod")
        if currency_code in desired_currencies:
            rate = float(currency_node.find("BanknoteBuying").text)  # Efektif alış kurları için "ForexBuying" kullanıldı
            exchange_rates[currency_code] = rate

    return exchange_rates

def update_google_sheets(data):
    # Update Google Sheets data
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values_to_append = [timestamp] + [data.get(currency, "") for currency in ["USD", "EUR", "GBP", "CAD", "AUD"]]

    sheet.append_row(values_to_append)
    print("Veriler başarıyla Google Sheets'e yazıldı - {}".format(timestamp))

if __name__ == "__main__":
    get_exchange_rates()
