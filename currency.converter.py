import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Custom CSS for styling
st.markdown("""
    <style>
        .result-box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
            margin-top: 20px;
        }
        .refresh-button {
            float: right;
        }
    </style>
""", unsafe_allow_html=True)

# Language settings
LANGUAGES = {
    "en": {
        "title": "💰 Real-Time Currency Converter",
        "amount": "Amount",
        "from_curr": "From Currency",
        "to_curr": "To Currency",
        "convert": "Convert",
        "result": "Converted Amount",
        "error": "Error fetching data! Please try again later.",
        "last_update": "Last update",
        "switch_button": "Switch to Greek 🇬🇷",
        "refresh": "Refresh Rates 🔄"
    },
    "el": {
        "title": "💰 Μετατροπέας Συναλλάγματος σε Πραγματικό Χρόνο",
        "amount": "Ποσό",
        "from_curr": "Από Νόμισμα",
        "to_curr": "Σε Νόμισμα",
        "convert": "Μετατροπή",
        "result": "Μετατρεπμένο Ποσό",
        "error": "Σφάλμα φόρτωσης δεδομένων! Δοκιμάστε ξανά αργότερα.",
        "last_update": "Τελευταία ενημέρωση",
        "switch_button": "Αλλαγή σε Αγγλικά 🇬🇧",
        "refresh": "Ανανέωση τιμών 🔄"
    }
}

# Initialize session state
if 'lang' not in st.session_state:
    st.session_state.lang = "el"
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

@st.cache_data(ttl=3600, show_spinner="Fetching exchange rates...")
def fetch_exchange_rates(refresh_counter):
    """Fetch exchange rates from ECB XML with error handling"""
    try:
        response = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml", timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        rates = {"EUR": 1.0}
        
        for cube in root.findall(".//{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube[@currency]"):
            currency = cube.attrib['currency']
            rates[currency] = float(cube.attrib['rate'])
        
        time_element = root.find(".//{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube[@time]")
        update_date = time_element.attrib.get('time', datetime.today().strftime('%Y-%m-%d'))
        
        return rates, update_date
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None

# UI Components
lang = LANGUAGES[st.session_state.lang]

# Language switcher and title
col1, col2 = st.columns([4, 1])
with col1:
    st.title(lang["title"])
with col2:
    if st.button(lang["switch_button"]):
        st.session_state.lang = "el" if st.session_state.lang == "en" else "en"

# Fetch data with refresh capability
exchange_rates, update_date = fetch_exchange_rates(st.session_state.refresh_counter)

# Refresh button
if st.button(lang["refresh"], help="Get latest exchange rates"):
    st.session_state.refresh_counter += 1
    st.rerun()

# Show last update date if available
if exchange_rates and update_date:
    st.caption(f"{lang['last_update']}: {update_date}")

# Main conversion form
disabled = not exchange_rates
conversion_result = None

with st.form("conversion_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input(
            lang["amount"],
            min_value=0.0,
            value=1.0,
            step=0.1,
            disabled=disabled,
            help="Enter the amount you want to convert"
        )
    
    with col2:
        currencies = sorted(exchange_rates.keys()) if exchange_rates else ["EUR"]
        from_curr = st.selectbox(
            lang["from_curr"],
            currencies,
            index=0,
            disabled=disabled,
            help="Select source currency"
        )
    
    to_curr = st.selectbox(
        lang["to_curr"],
        currencies,
        index=1 if len(currencies) > 1 else 0,
        disabled=disabled,
        help="Select target currency"
    )
    
    submitted = st.form_submit_button(lang["convert"], disabled=disabled)

# Handle conversion
if submitted and exchange_rates:
    try:
        if from_curr == to_curr:
            conversion_result = amount
        else:
            conversion_result = (amount / exchange_rates[from_curr]) * exchange_rates[to_curr]
    except Exception as e:
        st.error(f"{lang['error']}: {str(e)}")

# Display results
if conversion_result is not None:
    st.markdown(f"<div class='result-box'>"
                f"<h3 style='text-align: center; color: #2ecc71;'>"
                f"{conversion_result:.2f} {to_curr}</h3></div>", 
                unsafe_allow_html=True)
    st.write(f"*{lang['result']}*")

# Error message if rates unavailable
if not exchange_rates:
    st.error(lang["error"])
    st.info("Please try refreshing the rates or check your internet connection.")
