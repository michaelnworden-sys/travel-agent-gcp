import requests
import datetime

# Your API Key
API_KEY = "2b0c0878-16f0-44b7-97e8-5c48f77e14fb"

# Route: Seattle (7) to Bainbridge (3)
DEPARTURE_ID = "7"
ARRIVAL_ID = "3"

# Date: Tomorrow
tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
formatted_date = tomorrow.strftime('%Y-%m-%d')

# Construct URL
url = f"http://www.wsdot.wa.gov/Ferries/API/Schedule/rest/schedule/{formatted_date}/{DEPARTURE_ID}/{ARRIVAL_ID}?apiaccesscode={API_KEY}"

print(f"Testing Connection to: {url}")
print("Waiting for WSDOT...")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! API is working.")
        # Print first sailing to prove it
        first_time = data["TerminalCombos"][0]["Times"][0]["DepartingTime"]
        print(f"Found a sailing at raw time: {first_time}")
    else:
        print(f"❌ FAILURE. API returned error.")
        print(response.text)

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")