import sqlite3
import pandas as pd
from datetime import date
from typing import Optional

# 1. Helper function to talk to the database
# This prevents us from writing "connect to database" over and over again
def run_query(query: str, params: tuple = ()):
    conn = sqlite3.connect("travel.sqlite")
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results

# 2. THE TOOL: Search Flights
# This is what the LLM will actually call when a user asks for a flight.
def fetch_user_flight_information(departure_airport: str, arrival_airport: str):
    """
    Searches for flights between two airports.
    """
    conn = sqlite3.connect("travel.sqlite")
    # We use pandas here because it makes the output look nice for the LLM to read
    df = pd.read_sql(
        "SELECT * FROM flights WHERE departure_airport = ? AND arrival_airport = ?",
        conn,
        params=(departure_airport, arrival_airport)
    )
    conn.close()
    
    if df.empty:
        return "No flights found for that route."
    
    # Convert the spreadsheet row into a text string the LLM can read
    return df.to_string()

# 3. THE TOOL: Search Hotels
def search_hotels(location: str):
    """
    Searches for hotels in a specific city.
    """
    conn = sqlite3.connect("travel.sqlite")
    df = pd.read_sql(
        "SELECT * FROM hotels WHERE location = ?",
        conn,
        params=(location,)
    )
    conn.close()
    
    if df.empty:
        return "No hotels found in that location."
        
    return df.to_string()

print("✅ tools.py is ready. The agent now has 'Hands'.")