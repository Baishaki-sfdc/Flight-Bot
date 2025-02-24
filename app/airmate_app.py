import os
import re
import streamlit as st
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure API settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")

# Custom CSS
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
    if "collected_data" not in st.session_state:
        st.session_state.collected_data = {
            "departure_city": None,
            "destination": None,
            "travel_dates": None,
            "preferred_airline": None,
            "seating_class": None
        }
    if "booking_confirmed" not in st.session_state:
        st.session_state.booking_confirmed = False
    if "errors" not in st.session_state:  # NEW: Error tracking
        st.session_state.errors = []

# Validation functions (NEW SECTION)
def validate_dates(date_str):
    try:
        day, month, year = map(int, date_str.split('-'))
        # New logic: if the year from user input is less than the current year, prompt for a future date
        if year < datetime.today().year:
            return "❌ Date must be in the future"
        input_date = datetime(year, month, day).date()
        if input_date < datetime.today().date():
            return "❌ Date must be in the future"
        return None
    except ValueError:
        return "❌ Invalid date format. Use DD-MM-YYYY"

def validate_city(city):
    if not re.match(r"^[A-Za-z\s\-']{2,50}$", city):
        return "❌ Invalid city name"
    return None

def validate_class(seating_class):
    if not re.match(r"^(Economy|Premium Economy|Business|First)$", seating_class, re.IGNORECASE):
        return "❌ Invalid class. Choose: Economy, Premium Economy, Business, or First"
    return None

# Updated data processing with validation
def process_messages_for_data():
    st.session_state.errors = []  # Reset errors each processing cycle
    
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            content = msg["content"]
            
            # Extract and validate departure city
            if match := re.search(r"Departure City: (.*)", content):
                city = match.group(1).strip()
                if error := validate_city(city):
                    st.session_state.errors.append(error)
                else:
                    st.session_state.collected_data["departure_city"] = city
            # Extract and validate destination
            if match := re.search(r"Destination: (.*)", content):
                city = match.group(1).strip()
                if error := validate_city(city):
                    st.session_state.errors.append(error)
                else:
                    st.session_state.collected_data["destination"] = city
                    
            # Extract and validate dates
            if match := re.search(r"Travel Dates: (.*)", content):
                dates = match.group(1).strip()
                if error := validate_dates(dates.split(" to ")[0]):
                    st.session_state.errors.append(error)
                st.session_state.collected_data["travel_dates"] = dates

            # Validate seating class
            if match := re.search(r"Seating Class: (.*)", content):
                seat_class = match.group(1).strip()
                if error := validate_class(seat_class):
                    st.session_state.errors.append(error)
                else:
                    st.session_state.collected_data["seating_class"] = seat_class

# API Call Handler
def get_openrouter_response(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Data Extraction from Messages
def process_messages_for_data():
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            if match := re.search(r"Departure City: (.*)", msg["content"]):
                st.session_state.collected_data["departure_city"] = match.group(1)
            if match := re.search(r"Destination: (.*)", msg["content"]):
                st.session_state.collected_data["destination"] = match.group(1)
            if match := re.search(r"Travel Dates: (.*)", msg["content"]):
                st.session_state.collected_data["travel_dates"] = match.group(1)
            if match := re.search(r"Preferred Airline: (.*)", msg["content"]):
                st.session_state.collected_data["preferred_airline"] = match.group(1)
            if match := re.search(r"Seating Class: (.*)", msg["content"]):
                st.session_state.collected_data["seating_class"] = match.group(1)

# Updated flight search with error handling
def show_flight_options():
    data = st.session_state.collected_data
    
    # Check for unavailable routes (NEW)
    unavailable_routes = [
        ("Sydney", "Antarctica"),
        ("Tokyo", "Mars"),
        ("London", "North Pole")
    ]
    
    if (data["departure_city"], data["destination"]) in unavailable_routes:
        st.error("🚫 No flights available for this route")
        st.markdown("""
            <div class="flight-card">
                <h4>💡 Suggestions</h4>                
                <p>1. Try different dates</p>
                <p>2. Check nearby airports</p>
                <p>3. Consider alternative destinations</p>
            </div>
        """, unsafe_allow_html=True)
        return


# Flight display logic
def show_flight_options():
    st.subheader("Available Flights")
    flights = [
        {"airline": "AirMate 123", "departure": "08:00 AM", "price": "$450"},
        {"airline": "SkyHigh 456", "departure": "11:30 AM", "price": "$520"},
    ]
     # Create a list of flight option descriptions
    flight_descriptions = []
    for idx, flight in enumerate(flights, 1):
        flight_descriptions.append(f"Flight #{idx}: {flight['airline']} departing at {flight['departure']} for {flight['price']}")
    
    # Allow the user to select only one flight
    selected_option = st.radio("Select a flight", flight_descriptions, key="selected_flight")
    
    # Store the selected flight in session_state
    selected_index = flight_descriptions.index(selected_option)
    st.session_state.collected_data["selected_flight"] = flights[selected_index]
    
    # Display flight cards
    for idx, flight in enumerate(flights, 1):
        st.markdown(f"""
            <div class="flight-card">
                <h4>✈️ Flight #{idx}</h4>
                <p>Airline: {flight['airline']}</p>
                <p>Departure: {flight['departure']}</p>
                <p>Price: {flight['price']}</p>
            </div>
            """, unsafe_allow_html=True)



# Main App
def main():
    st.set_page_config(page_title="AirMate", page_icon="✈️")
    load_css()
    initialize_session()

    st.title("✈️ AirMate")
    st.sidebar.title("Settings")
    api_key=st.sidebar.text_input("Enter your api key:",type="password")

    #st.secrets["OPENROUTER_API_KEY"]
    #st.secrets["OPENROUTER_URL"]

     # Display errors (NEW)
    if st.session_state.errors:
        error_container = st.container()
        with error_container:
            st.error(" \n".join(st.session_state.errors))

    # Chat container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            div_class = "user-message" if message["role"] == "user" else "bot-message"
            st.markdown(f"<div class='{div_class}'>{message['content']}</div>", unsafe_allow_html=True)

    # User input
    with st.form("chat_input", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="input", placeholder="Enter your message here...")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Create system message with instructions
        system_message = {
            "role": "system",
            "content": """You are AirMate, an AI flight booking assistant. Guide the user through collecting:
        1. Departure City (valid city name)
        2. Destination (valid city name)
        3. Travel Dates (future dates in DD-MM-YYYY format)
        4. Preferred Airline
        5. Seating Class (Economy/Premium Economy/Business/First)
        
        Validate inputs as you go. Reject invalid inputs immediately.
        Keep responses concise. After collecting all info, show flight options.
        Use EXACT format:
        'Departure City: [value]
        Destination: [value]
        Travel Dates: [value]
        Preferred Airline: [value]
        Seating Class: [value]'"""
        }

        # Get AI response
        messages = [system_message] + st.session_state.messages
        ai_response = get_openrouter_response(messages)

        if ai_response:
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            process_messages_for_data()
            st.rerun()

    # Show flight options when all data collected
    if all(st.session_state.collected_data.values()) and not st.session_state.booking_confirmed:
        show_flight_options()
        if st.button("Confirm Booking"):
            st.session_state.booking_confirmed = True
            st.success("🎉 Booking confirmed! Your reference number: AM-20240601-1234")
            st.balloons()

if __name__ == "__main__":
    main()