import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Language settings - preloaded for instant switching
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
        "switch": "🇬🇷 ΕΛ",
        "refresh": "🔄 Refresh"
    },
    "el": {
        "title": "💰 Μετατροπέας Συναλλάγματος",
        "amount": "Ποσό",
        "from_curr": "Από Νόμισμα",
        "to_curr": "Σε Νόμισμα",
        "convert": "Μετατροπή",
        "result": "Μετατρεπμένο Ποσό",
        "error": "Σφάλμα φόρτωσης! Δοκιμάστε ξανά.",
        "last_update": "Ενημέρωση",
        "switch": "🇬🇧 EN",
        "refresh": "🔄 Ανανέωση"
    }
}

# Session state initialization
if 'lang' not in st.session_state:
    st.session_state.lang = "el"
if 'rates' not in st.session_state:
    st.session_state.rates = None
if 'date' not in st.session_state:
    st.session_state.date = None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_exchange_rates():
    """Ultra-fast XML parsing with minimal operations"""
    try:
        response = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml", timeout=3)
        root = ET.fromstring(response.content)
        rates = {"EUR": 1.0}
        
        # Fast namespace-aware parsing
        ns = {'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        cubes = root.findall(".//ecb:Cube[@currency]", namespaces=ns)
        
        for cube in cubes:
            rates[cube.attrib['currency']] = float(cube.attrib['rate'])
        
        time_element = root.find(".//ecb:Cube[@time]", namespaces=ns)
        return rates, time_element.attrib.get('time', datetime.today().strftime('%Y-%m-%d'))
    except Exception:
        return None, None

# Layout configuration for instant response
st.set_page_config(layout="centered")

# Language toggle in sidebar for better performance
with st.sidebar:
    if st.button(LANGUAGES[st.session_state.lang]["switch"]):
        st.session_state.lang = "el" if st.session_state.lang == "en" else "en"

# Main content
lang = LANGUAGES[st.session_state.lang]

# Header with refresh button
col1, col2 = st.columns([4, 1])
with col1:
    st.title(lang["title"])
with col2:
    if st.button(lang["refresh"], help=""):
        st.cache_data.clear()
        st.session_state.rates, st.session_state.date = fetch_exchange_rates()

# Fetch rates only once per session
if st.session_state.rates is None:
    st.session_state.rates, st.session_state.date = fetch_exchange_rates()

# Conversion form
if st.session_state.rates:
    with st.form("converter"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input(
                lang["amount"],
                min_value=0.0,
                value=1.0,
                step=0.1
            )
        
        with col2:
            currencies = sorted(st.session_state.rates.keys())
            from_curr = st.selectbox(lang["from_curr"], currencies)
        
        to_curr = st.selectbox(lang["to_curr"], currencies, index=1)
        
        if st.form_submit_button(lang["convert"], use_container_width=True):
            try:
                rate_from = st.session_state.rates[from_curr]
                rate_to = st.session_state.rates[to_curr]
                result = (amount / rate_from) * rate_to
                st.success(f"**{lang['result']}:** {result:.2f} {to_curr}")
                st.caption(f"{lang['last_update']}: {st.session_state.date}")
            except:
                st.error(lang["error"])
else:
    st.error(lang["error"])
