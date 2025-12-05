import sqlite3
import pandas as pd

# 1. Connect to a new database file
conn = sqlite3.connect("travel.sqlite")
cursor = conn.cursor()

# 2. Load the "Flight" data (We are mocking up some Swiss Air flights)
# In a real app, this would be your connection to the Airline's backend
flights_data = [
    {"flight_id": 1, "flight_no": "LX0112", "scheduled_departure": "2024-05-01 10:30:00-05:00", "scheduled_arrival": "2024-05-01 14:30:00+02:00", "departure_airport": "ORD", "arrival_airport": "ZRH", "status": "On Time", "aircraft_code": "SU9", "actual_departure": None, "actual_arrival": None},
    {"flight_id": 2, "flight_no": "LX0113", "scheduled_departure": "2024-05-02 11:30:00-05:00", "scheduled_arrival": "2024-05-02 15:30:00+02:00", "departure_airport": "ZRH", "arrival_airport": "ORD", "status": "On Time", "aircraft_code": "SU9", "actual_departure": None, "actual_arrival": None},
]

# 3. Load Hotel Data
hotels_data = [
    {"id": 1, "name": "Hilton Zurich City", "location": "Zurich", "price_tier": "Luxury", "checkin_time": "15:00", "checkout_time": "11:00"},
    {"id": 2, "name": "Low Budget Stay", "location": "Zurich", "price_tier": "Economy", "checkin_time": "16:00", "checkout_time": "10:00"},
]

# 4. Convert to DataFrames and save to SQL
print("Creating Flights Table...")
pd.DataFrame(flights_data).to_sql("flights", conn, if_exists="replace", index=False)

print("Creating Hotels Table...")
pd.DataFrame(hotels_data).to_sql("hotels", conn, if_exists="replace", index=False)

# 5. Create a "Bookings" table so we can write to it later
cursor.execute("""
CREATE TABLE IF NOT EXISTS ticket_bookings (
    ticket_no TEXT PRIMARY KEY,
    book_ref TEXT NOT NULL,
    flight_id INTEGER NOT NULL,
    flight_date TEXT NOT NULL,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
)
""")

conn.commit()
conn.close()

print("✅ SUCCESS! 'travel.sqlite' has been created in your folder.")