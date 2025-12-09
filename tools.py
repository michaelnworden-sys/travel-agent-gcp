import datetime
import pytz
import re
import requests
import parsedatetime as pdt
import googlemaps
from google.cloud import bigquery
from collections import defaultdict
from langchain_core.tools import tool

# Import the Local Knowledge we just created
from knowledge import TERMINAL_DATA

# ==============================================================================
# --- 1. CONFIGURATION AND KNOWLEDGE BASE ---
# ==============================================================================

# --- API KEYS ---
WSDOT_API_KEY = "2b0c0878-16f0-44b7-97e8-5c48f77e14fb" # Mike's WSDOT Key
GMAPS_API_KEY = "AIzaSyBtRzkN7I16ZhJZnVlv4XgSA4UBDvPgeRo" # Mike's Google Maps Key

# Initialize Google Maps
gmaps = googlemaps.Client(key=GMAPS_API_KEY)
GCS_IMAGE_BASE_URL = "https://storage.googleapis.com/ferry_data/NewWSF/ferryimages/"

SAN_JUAN_TERMINALS = {
    "Anacortes", "Friday Harbor", "Orcas", "Shaw", "Lopez"
}

# Used for Fare Logic (Westbound vs Eastbound)
WESTBOUND_TERMINALS = {
    'Seattle', 'Edmonds', 'Mukilteo', 'Fauntleroy', 'Southworth',
    'Anacortes', 'Coupeville', 'Point Defiance'
}

ROUND_TRIP_VEHICLE_ROUTES = {
    frozenset({'Fauntleroy', 'Vashon'}), frozenset({'Southworth', 'Vashon'}),
    frozenset({'Point Defiance', 'Tahlequah'})
}

TARGET_FARE_DESCRIPTIONS = {
    "Adult (age 19 - 64)",
    "Senior (age 65 & over) / <a href=https://wsdot.wa.gov/ferries/rider-information/ada#Reduced%20fare%20passenger%20tickets target=\"_blank\" title=\"Disability\">Disability</a>",
    "Youth (age 18 and under)", "Bicycle Surcharge Only (19 and over)",
    "Vehicle Under 22' (standard veh) & Driver", "Vehicle U22' (standard veh) & Sr/Disability Driver",
    "Motorcycle & Driver / Stowage Fare", "Motorcycle & Senior/Disability Driver / Stowage Fare",
    "Vehicle Under 40'"
}

TERMINAL_CLEANER_MAP = {
    # Aliases for Anacortes
    "mainland": "Anacortes", "anacortes": "Anacortes",
    "annacortes": "Anacortes", "anacortez": "Anacortes",
    # Aliases for Friday Harbor
    "san juan island": "Friday Harbor", "san juan": "Friday Harbor",
    "friday harbor": "Friday Harbor", "friday": "Friday Harbor",
    "fridayharbor": "Friday Harbor",
    # Aliases for Orcas
    "orcas island": "Orcas", "orcas": "Orcas", "orkus": "Orcas",
    # Aliases for Lopez
    "lopez island": "Lopez", "lopez": "Lopez",
    # Aliases for Shaw
    "shaw island": "Shaw", "shaw": "Shaw",
    # South Sound Aliases
    "winslow": "Bainbridge", "bainbridge island": "Bainbridge",
    "bainbridge": "Bainbridge", "colman dock": "Seattle",
    "seattle": "Seattle", "whidbey island": "Clinton",
    "clinton": "Clinton", "whidbey": "Clinton",
    "tacoma": "Point Defiance", "point defiance": "Point Defiance",
    "pt defiance": "Point Defiance", "vashon island": "Vashon",
    "vashon": "Vashon", "west seattle": "Fauntleroy",
    "fauntleroy": "Fauntleroy", "bremerton": "Bremerton",
    "coupeville": "Coupeville", "edmonds": "Edmonds",
    "kingston": "Kingston", "mukilteo": "Mukilteo",
    "port townsend": "Port Townsend", "pt townsend": "Port Townsend",
    "southworth": "Southworth", "tahlequah": "Tahlequah",
}

TERMINAL_PRETTIFIER_MAP = {
    "Anacortes": "Anacortes",
    "Friday Harbor": "Friday Harbor",
    "Orcas": "Orcas Island",
    "Shaw": "Shaw Island",
    "Lopez": "Lopez Island",
    "Bainbridge": "Bainbridge Island",
    "Point Defiance": "Tacoma (Point Defiance)",
    "Seattle": "Seattle (Colman Dock)"
}

TERMINAL_ID_MAP = {
    "Anacortes": "1", "Bainbridge": "3", "Bremerton": "4", "Clinton": "5",
    "Coupeville": "11", "Edmonds": "8", "Fauntleroy": "9", "Friday Harbor": "10",
    "Kingston": "12", "Lopez": "13", "Mukilteo": "14", "Orcas": "15",
    "Point Defiance": "16", "Port Townsend": "17", "Seattle": "7", "Shaw": "18",
    "Sidney B.C.": "19", "Southworth": "20", "Tahlequah": "21", "Vashon": "22",
}

# ==============================================================================
# --- 2. UNIVERSAL HELPER FUNCTIONS ---
# ==============================================================================

def _parse_human_time(time_phrase: str) -> dict:
    pacific_tz = pytz.timezone('America/Los_Angeles')
    cal = pdt.Calendar()
    now_pacific = datetime.datetime.now(pacific_tz)

    cleaned_phrase = re.sub(r' from| to| at| on|ferry|boat', '', time_phrase.lower(), flags=re.IGNORECASE).strip()
    result_datetime, parse_status = cal.parseDT(datetimeString=cleaned_phrase or "now", sourceTime=now_pacific)

    if parse_status == 0:
        result_datetime = now_pacific

    start_time = 0
    end_time = 2359
    lower_phrase = time_phrase.lower()
    
    if "morning" in lower_phrase:
        start_time, end_time = 500, 1159
    elif "afternoon" in lower_phrase:
        start_time, end_time = 1200, 1759
    elif "evening" in lower_phrase or "night" in lower_phrase:
        start_time, end_time = 1800, 2359

    if any(char.isdigit() for char in time_phrase) and not any(k in lower_phrase for k in ["morning", "afternoon", "evening"]):
        window_center = result_datetime
        two_hours_before = window_center - datetime.timedelta(hours=2)
        two_hours_after = window_center + datetime.timedelta(hours=2)
        start_time = int(two_hours_before.strftime('%H%M'))
        end_time = int(two_hours_after.strftime('%H%M'))

    return {
        "iso_time": result_datetime.isoformat(),
        "travel_day": result_datetime.strftime('%A'),
        "start_time": start_time,
        "end_time": end_time,
        "formatted_date": result_datetime.strftime('%A, %B %d')
    }

def _format_time_from_int(time_int: int) -> str:
    if time_int is None: return ""
    hours, minutes = divmod(time_int, 100)
    dt = datetime.time(hour=hours, minute=minutes)
    return dt.strftime('%I:%M %p').strip()

def _convert_wsf_time(wsf_time_str: str) -> str:
    match = re.search(r"\((\d+)", wsf_time_str)
    if not match: return ""
    timestamp_s = int(match.group(1)) / 1000.0
    pacific_dt = datetime.datetime.fromtimestamp(timestamp_s, tz=pytz.timezone('America/Los_Angeles'))
    return pacific_dt.strftime("%I:%M %p").strip()

# --- FARE HELPERS ---
def _simplify_fare_description(description):
    if not description: return ''
    simplified = description.replace('<a href=https://wsdot.wa.gov/ferries/rider-information/ada#Reduced%20fare%20passenger%20tickets target=\"_blank\" title=\"Disability\">Disability</a>', 'Disability')
    simplified = simplified.replace('Senior (age 65 & over) / Disability', 'Senior (65+) / Disability Passenger')
    simplified = simplified.replace('Adult (age 19 - 64)', 'Adult Passenger (19-64)')
    simplified = simplified.replace('Youth (age 18 and under)', 'Youth Passenger (18 & under)')
    simplified = simplified.replace('Bicycle Surcharge Only (19 and over)', 'Bicycle (Surcharge, passenger fare extra)')
    simplified = simplified.replace('Vehicle Under 22\' (standard veh) & Driver', 'Vehicle (<22 ft) & Driver')
    simplified = simplified.replace('Vehicle U22\' (standard veh) & Sr/Disability Driver', 'Vehicle (<22 ft) & Senior/Disability Driver')
    simplified = simplified.replace('Motorcycle & Driver / Stowage Fare', 'Motorcycle & Driver')
    simplified = simplified.replace('Motorcycle & Senior/Disability Driver / Stowage Fare', 'Motorcycle & Senior/Disability Driver')
    simplified = simplified.replace('Vehicle Under 40\'', 'Vehicle (<40 ft)')
    return simplified

def _determine_fare_direction(departure_terminal):
    return "Westbound" if departure_terminal in WESTBOUND_TERMINALS else "Eastbound"

def _format_currency(amount):
    if not isinstance(amount, (int, float)): return str(amount)
    return f"${amount:,.2f}"

# ==============================================================================
# --- 3. SCHEDULE LOGIC (San Juan & South Sound) ---
# ==============================================================================

def get_san_juan_schedule(departure_terminal: str, arrival_terminal: str, time_components: dict) -> dict:
    try:
        # Note: This requires Google Cloud Authentication to work locally
        client = bigquery.Client()
        travel_day = time_components['travel_day']
        start_time = time_components['start_time']
        end_time = time_components['end_time']

        time_condition = "(t1.departure_time >= @start_time AND t1.departure_time <= @end_time)"
        if start_time > end_time:
            time_condition = "(t1.departure_time >= @start_time OR t1.departure_time <= @end_time)"

        table_id = "lumina-content-intelligence.san_juan_ferry_schedules.schedules"
        query = f"""
            WITH ValidTripIDs AS (
                SELECT DISTINCT t1.trip_id FROM `{table_id}` AS t1
                JOIN `{table_id}` AS t2 ON t1.trip_id = t2.trip_id
                WHERE LOWER(t1.departure_terminal) = LOWER(@departure_terminal)
                  AND LOWER(t2.arrival_terminal) = LOWER(@arrival_terminal)
                  AND LOWER(t1.days_of_operation) LIKE CONCAT('%', LOWER(@travel_day), '%')
                  AND {time_condition}
                  AND t1.departure_time <= t2.departure_time
            )
            SELECT vessel_name, trip_id, departure_terminal, departure_time, arrival_terminal, notes
            FROM `{table_id}`
            WHERE trip_id IN (SELECT trip_id FROM ValidTripIDs)
            ORDER BY trip_id, departure_time;
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("departure_terminal", "STRING", departure_terminal),
                bigquery.ScalarQueryParameter("arrival_terminal", "STRING", arrival_terminal),
                bigquery.ScalarQueryParameter("travel_day", "STRING", travel_day),
                bigquery.ScalarQueryParameter("start_time", "INT64", start_time),
                bigquery.ScalarQueryParameter("end_time", "INT64", end_time),
            ]
        )
        results = client.query(query, job_config=job_config).result()

        grouped_trips = defaultdict(list)
        for row in results:
            grouped_trips[row.trip_id].append(dict(row))

        formatted_trips = []
        for trip_id, legs in grouped_trips.items():
            start_index, end_index = -1, -1
            for i, leg in enumerate(legs):
                if leg['departure_terminal'].lower() == departure_terminal.lower():
                    start_index = i
                    break
            for i, leg in enumerate(legs):
                if leg['arrival_terminal'].lower() == arrival_terminal.lower():
                    end_index = i
            
            if start_index != -1 and end_index != -1 and start_index <= end_index:
                relevant_legs = legs[start_index : end_index + 1]
                if not relevant_legs: continue

                trip_data = {
                    "departure_time": _format_time_from_int(relevant_legs[0]['departure_time']),
                    "vessel_name": relevant_legs[0]['vessel_name'],
                    "stops": [leg['arrival_terminal'] for leg in relevant_legs[:-1]],
                    "notes": "; ".join(sorted({leg['notes'] for leg in relevant_legs if leg['notes']}))
                }
                formatted_trips.append(trip_data)

        formatted_trips.sort(key=lambda x: datetime.datetime.strptime(x['departure_time'], '%I:%M %p'))
        return {"success": True, "sailings": formatted_trips}

    except Exception as e:
        return {"success": False, "error": f"BigQuery database error: {str(e)}"}

def _apply_wsdot_smart_filtering(sailings: list, date_time_query: str, time_components: dict) -> list:
    def _parse_sailing_time(time_str: str):
        try: return datetime.datetime.strptime(time_str.strip(), '%I:%M %p').time()
        except (ValueError, TypeError): return None

    normalized_query = date_time_query.lower().strip()
    target_dt = datetime.datetime.fromisoformat(time_components['iso_time'])
    immediate_keywords = ["now", "next", "immediately", "asap", "right now", "soonest", "earliest", "first available"]

    if any(word in normalized_query for word in immediate_keywords):
        # Rule 1: Immediate
        future = [
            s for s in sailings 
            if _parse_sailing_time(s["departure_time"]) and _parse_sailing_time(s["departure_time"]) >= target_dt.time()
        ]
        return future[:3]

    elif any(k in normalized_query for k in ["morning", "afternoon", "evening", "night"]):
        # Rule 2: Time of Day
        time_morn_start, time_morn_end = datetime.time(4, 0), datetime.time(11, 59)
        time_aft_start, time_aft_end = datetime.time(12, 0), datetime.time(17, 59)
        time_eve_start = datetime.time(18, 0)
        
        if "morning" in normalized_query:
            return [
                s for s in sailings 
                if _parse_sailing_time(s["departure_time"]) 
                and time_morn_start <= _parse_sailing_time(s["departure_time"]) <= time_morn_end
            ]
        elif "afternoon" in normalized_query:
            return [
                s for s in sailings 
                if _parse_sailing_time(s["departure_time"]) 
                and time_aft_start <= _parse_sailing_time(s["departure_time"]) <= time_aft_end
            ]
        else: # Evening
            return [
                s for s in sailings 
                if _parse_sailing_time(s["departure_time"]) 
                and (_parse_sailing_time(s["departure_time"]) >= time_eve_start 
                     or _parse_sailing_time(s["departure_time"]) < time_morn_start)
            ]
            
    elif not any(char.isdigit() for char in normalized_query):
        # Rule 3: General day
        return sailings

    else:
        # Rule 4: Specific time window
        ref_time = target_dt.time()
        start = (target_dt - datetime.timedelta(hours=2)).time()
        end = (target_dt + datetime.timedelta(hours=2)).time()
        if start > end:
            return [
                s for s in sailings 
                if _parse_sailing_time(s["departure_time"]) 
                and (_parse_sailing_time(s["departure_time"]) >= start 
                     or _parse_sailing_time(s["departure_time"]) <= end)
            ]
        else:
            return [
                s for s in sailings 
                if _parse_sailing_time(s["departure_time"]) 
                and start <= _parse_sailing_time(s["departure_time"]) <= end
            ]

def get_south_sound_schedule(departure_terminal: str, arrival_terminal: str, date_time_query: str, time_components: dict) -> dict:
    try:
        departure_id = TERMINAL_ID_MAP.get(departure_terminal)
        arrival_id = TERMINAL_ID_MAP.get(arrival_terminal)

        if not departure_id or not arrival_id:
            return {"success": False, "error": f"Could not find an API ID for '{departure_terminal}' or '{arrival_terminal}'."}

        formatted_date = datetime.datetime.fromisoformat(time_components['iso_time']).strftime('%Y-%m-%d')
        api_url = f"http://www.wsdot.wa.gov/Ferries/API/Schedule/rest/schedule/{formatted_date}/{departure_id}/{arrival_id}?apiaccesscode={WSDOT_API_KEY}"

        response = requests.get(api_url)
        response.raise_for_status()
        schedule_data = response.json()

        if not schedule_data or not schedule_data.get("TerminalCombos"):
            return {"success": True, "sailings": [], "message": "No sailings found for that route and date."}

        all_sailings = []
        for sailing in schedule_data["TerminalCombos"][0]["Times"]:
            if sailing.get("DepartingTime"):
                all_sailings.append({
                    "departure_time": _convert_wsf_time(sailing.get("DepartingTime", "")),
                    "vessel_name": sailing.get("VesselName", "Unknown"),
                    "stops": [],
                    "notes": ""
                })
        
        filtered_sailings = _apply_wsdot_smart_filtering(all_sailings, date_time_query, time_components)

        target_dt = datetime.datetime.fromisoformat(time_components['iso_time'])
        pacific_tz = pytz.timezone('America/Los_Angeles')
        now_pacific = datetime.datetime.now(pacific_tz)

        if target_dt.date() == now_pacific.date():
            current_time = now_pacific.time()
            future_sailings = []
            for s in filtered_sailings:
                try:
                    sailing_time = datetime.datetime.strptime(s['departure_time'], '%I:%M %p').time()
                    if sailing_time >= current_time:
                        future_sailings.append(s)
                except (ValueError, TypeError):
                    continue
            filtered_sailings = future_sailings

        if not filtered_sailings:
            return {"success": True, "sailings": [], "message": f"No remaining sailings were found for '{date_time_query}'."}

        return {"success": True, "sailings": filtered_sailings}

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"WSDOT API call failed: {e}"}
    except Exception as e:
        return {"success": False, "error": f"An error occurred in South Sound logic: {str(e)}"}

# ==============================================================================
# --- 4. THE LANGGRAPH TOOL DEFINITIONS ---
# ==============================================================================

@tool
def get_ferry_schedule(departure_terminal: str, arrival_terminal: str, date_time_query: str):
    """
    Fetches the Washington State Ferry schedule.
    """
    print(f"\n🔎 DEBUG: Tool called with: Dep={departure_terminal}, Arr={arrival_terminal}, Time={date_time_query}")
    
    # 1. Clean Inputs
    clean_departure = TERMINAL_CLEANER_MAP.get(departure_terminal.lower().strip(), departure_terminal.title())
    clean_arrival = TERMINAL_CLEANER_MAP.get(arrival_terminal.lower().strip(), arrival_terminal.title())
    print(f"🔎 DEBUG: Cleaned Names: {clean_departure} -> {clean_arrival}")

    # 2. Parse Time
    try:
        time_components = _parse_human_time(date_time_query)
        print(f"🔎 DEBUG: Parsed Time: {time_components['iso_time']} (Travel Day: {time_components['travel_day']})")
    except Exception as e:
        print(f"❌ DEBUG ERROR in Time Parsing: {e}")
        return {"error": f"Time parsing failed: {e}"}

    # 3. Route to Backend
    schedule_result = {}
    if clean_departure in SAN_JUAN_TERMINALS or clean_arrival in SAN_JUAN_TERMINALS:
        print("🔎 DEBUG: Routing to San Juan (BigQuery)...")
        schedule_result = get_san_juan_schedule(clean_departure, clean_arrival, time_components)
    else:
        print("🔎 DEBUG: Routing to South Sound (API)...")
        schedule_result = get_south_sound_schedule(clean_departure, clean_arrival, date_time_query, time_components)

    print(f"🔎 DEBUG: Result Success Status: {schedule_result.get('success')}")
    if not schedule_result.get('success'):
        print(f"❌ DEBUG ERROR MESSAGE: {schedule_result.get('error')}")

    # 4. Return Results
    return {
        "departure": TERMINAL_PRETTIFIER_MAP.get(clean_departure, clean_departure),
        "arrival": TERMINAL_PRETTIFIER_MAP.get(clean_arrival, clean_arrival),
        "date": time_components['formatted_date'],
        "sailings": schedule_result.get("sailings", []),
        "error": schedule_result.get("error", None),
        "message": schedule_result.get("message", None)
    }

@tool
def get_ferry_fares(departure_terminal: str, arrival_terminal: str):
    """
    Fetches the Washington State Ferry fares (prices) for a given route.
    Returns both passenger and vehicle fares.
    """
    print(f"\n💰 DEBUG: Fare Tool called with: Dep={departure_terminal}, Arr={arrival_terminal}")

    # 1. Clean Inputs
    clean_departure = TERMINAL_CLEANER_MAP.get(departure_terminal.lower().strip(), departure_terminal.strip().title())
    clean_arrival = TERMINAL_CLEANER_MAP.get(arrival_terminal.lower().strip(), arrival_terminal.strip().title())

    # 2. Validate IDs
    departure_id = TERMINAL_ID_MAP.get(clean_departure)
    arrival_id = TERMINAL_ID_MAP.get(clean_arrival)

    if not departure_id or not arrival_id:
        return {"error": f"Invalid terminal names. Could not find ID for {clean_departure} or {clean_arrival}."}

    # 3. Determine Direction & Date
    fare_direction = _determine_fare_direction(clean_departure)
    trip_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # 4. Call WSDOT API
    api_url = f"http://www.wsdot.wa.gov/Ferries/API/Fares/rest/farelineitems/{trip_date}/{departure_id}/{arrival_id}/false?apiaccesscode={WSDOT_API_KEY}"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        raw_fare_data = response.json()
    except Exception as e:
        return {"error": f"WSDOT API Error: {str(e)}"}

    # 5. Process Fares
    passenger_fares = []
    vehicle_fares = []

    for item in raw_fare_data:
        if item.get('FareLineItem') in TARGET_FARE_DESCRIPTIONS:
            is_passenger_fare = item.get('Category') == 'Passenger'
            simplified_desc = _simplify_fare_description(item.get('FareLineItem'))
            cost = item.get('Amount', 0.0)
            fare_details = {"description": simplified_desc, "cost": _format_currency(cost), "notes": "(One Way)"}

            # Round Trip Logic
            if is_passenger_fare:
                fare_details["notes"] = "(Round Trip)"
            else: 
                current_route = frozenset({clean_departure, clean_arrival})
                is_san_juan = (clean_departure == 'Anacortes' and clean_arrival in SAN_JUAN_TERMINALS) or \
                                (clean_arrival == 'Anacortes' and clean_departure in SAN_JUAN_TERMINALS)
                if is_san_juan or current_route in ROUND_TRIP_VEHICLE_ROUTES:
                    fare_details["notes"] = "(Round Trip)"

            # "Free" Eastbound Logic
            if fare_direction == "Eastbound" and is_passenger_fare:
                fare_details["cost"] = "Free"
                fare_details["notes"] = "(Paid Westbound)"

            # Youth Logic
            if "Youth" in simplified_desc:
                fare_details["cost"] = "Free"
            
            if is_passenger_fare:
                passenger_fares.append(fare_details)
            else:
                vehicle_fares.append(fare_details)

    return {
        "departure": TERMINAL_PRETTIFIER_MAP.get(clean_departure, clean_departure),
        "arrival": TERMINAL_PRETTIFIER_MAP.get(clean_arrival, clean_arrival),
        "direction": fare_direction,
        "passenger_fares": passenger_fares,
        "vehicle_fares": vehicle_fares
    }

# ==============================================================================
# --- 5. NEW LOCAL KNOWLEDGE TOOLS ---
# ==============================================================================

@tool
def get_terminal_town_description(terminal_name: str):
    """
    Returns a pre-written description of the terminal town and an image URL.
    Use this when a user asks "What is it like in Clinton?" or "Tell me about the terminal area."
    """
    print(f"\n🏙️ DEBUG: Town Description Tool called for: {terminal_name}")
    
    clean_name = TERMINAL_CLEANER_MAP.get(terminal_name.lower().strip(), terminal_name.title())
    
    if clean_name not in TERMINAL_DATA:
        return {"error": f"No description found for {terminal_name}. Try a major terminal name."}
    
    data = TERMINAL_DATA[clean_name]
    
    # Construct Image URL
    # Note: We remove spaces for the filename (e.g., "Friday Harbor" -> "FridayHarbor.jpg")
    image_name = clean_name.replace(" ", "")
    image_url = f"{GCS_IMAGE_BASE_URL}{image_name}.jpg"
    
    return {
        "terminal_name": clean_name,
        "description": data["description"],
        "image_url": image_url
    }

@tool
def search_terminal_area(terminal_name: str, search_query: str):
    """
    Searches for businesses (coffee, food, etc.) near a specific terminal using Google Maps.
    Use this when a user asks "Is there coffee near the dock?" or "Where can I eat in Kingston?"
    """
    print(f"\n🗺️ DEBUG: Search Tool called for: {terminal_name}, Query: {search_query}")
    
    clean_name = TERMINAL_CLEANER_MAP.get(terminal_name.lower().strip(), terminal_name.title())
    
    if clean_name not in TERMINAL_DATA:
        return {"error": f"Unknown terminal area: {terminal_name}. Cannot perform search."}
    
    data = TERMINAL_DATA[clean_name]
    
    # 1. Get Search Config
    coords = data.get("searchCenterCoordinates", data["coordinates"])
    radius = data.get("searchRadius", 2000)
    
    # 2. Call Google Places API
    try:
        location = (coords['latitude'], coords['longitude'])
        places_result = gmaps.places_nearby(location=location, keyword=search_query, radius=radius)
        
        if not places_result or not places_result.get('results'):
            return {"message": f"No results found for '{search_query}' near {clean_name}."}
        
        # 3. Simplify Results for the Agent
        simplified_places = []
        for place in places_result['results'][:5]: # Limit to top 5
            simplified_places.append({
                "name": place.get('name'),
                "rating": place.get('rating', 'N/A'),
                "address": place.get('vicinity', 'No address provided'),
                "open_now": place.get('opening_hours', {}).get('open_now', 'Unknown')
            })
            
        return {
            "terminal": clean_name,
            "query": search_query,
            "results": simplified_places,
            "notes": data.get("notesForGemini", "")
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Google Maps API Error: {e}")
        return {"error": f"Search failed due to technical error: {e}"}