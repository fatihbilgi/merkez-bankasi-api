import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets API ile iletişim kurabilmek için kimlik doğrulama yapın
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("merkez-bankasi-api-9bf92c90555a.json", scope)
gc = gspread.authorize(credentials)

# Google Sheets dokümanını açın (Doküman ID'sini almak için Google Sheets URL'sine bakın)
spreadsheet_id = "12Jp25Ei2IulYL0UbWXsI1vURE8Fl1l7UqjbVBNdQbNk"
sheet = gc.open_by_key(spreadsheet_id).sheet1

def get_exchange_rates():
    url = "https://www.tcmb.gov.tr/kurlar/today.xml"
    response = requests.get(url)

    if response.status_code == 200:
        # XML verilerini işleme kodu
        rates_data = process_data(response.text)
        update_google_sheets(rates_data)
    else:
        print("Hata oluştu - HTTP Kodu: {}".format(response.status_code))

def process_data(xml_data):
    # XML verilerini işleme kodu
    # Bu örnekte, xml.etree.ElementTree modülünü kullanarak XML verilerini işleyeceğiz
    import xml.etree.ElementTree as ET

    # XML verisini parse et
    root = ET.fromstring(xml_data)

    # Kurları depolamak için bir sözlük oluştur
    exchange_rates = {}

    # İstediğiniz döviz kodlarını belirtin
    desired_currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]

    # Döviz kurlarını çıkar
    for currency_node in root.findall(".//Currency"):
        currency_code = currency_node.get("Kod")
        if currency_code in desired_currencies:
            rate = float(currency_node.find("BanknoteBuying").text)  # Efektif alış kurları için "ForexBuying" kullanıldı
            exchange_rates[currency_code] = rate

    return exchange_rates

def update_google_sheets(data):
    # Google Sheets'e veriyi güncelleme kodu
    # Örneğin: sheet.append_row(["timestamp", "USD", "EUR", "GBP", "CAD", "AUD"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values_to_append = [timestamp] + [data.get(currency, "") for currency in ["USD", "EUR", "GBP", "CAD", "AUD"]]

    sheet.append_row(values_to_append)
    print("Veriler başarıyla Google Sheets'e yazıldı - {}".format(timestamp))

if __name__ == "__main__":
    get_exchange_rates()
