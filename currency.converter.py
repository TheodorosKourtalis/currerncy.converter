import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Ρυθμίσεις γλώσσας
LANGUAGES = {
    "en": {
        "title": "💰 Real-Time Currency Converter",
        "amount": "Amount",
        "from_curr": "From Currency",
        "to_curr": "To Currency",
        "convert": "Convert",
        "result": "Converted Amount",
        "error": "Error fetching data! Please try again later.",
        "last_update": "Last update"
    },
    "el": {
        "title": "💰 Μετατροπέας Συναλλάγματος σε Πραγματικό Χρόνο",
        "amount": "Ποσό",
        "from_curr": "Από Νόμισμα",
        "to_curr": "Σε Νόμισμα",
        "convert": "Μετατροπή",
        "result": "Μετατρεπμένο Ποσό",
        "error": "Σφάλμα φόρτωσης δεδομένων! Δοκιμάστε ξανά αργότερα.",
        "last_update": "Τελευταία ενημέρωση"
    }
}

# Αρχικοποίηση session state για γλώσσα
if 'lang' not in st.session_state:
    st.session_state.lang = "el"

def fetch_exchange_rates():
    """Λήψη δεδομένων από το ECB XML"""
    try:
        response = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml")
        root = ET.fromstring(response.content)
        namespaces = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01'}
        
        rates = {"EUR": 1.0}
        for cube in root.findall(".//*[@currency]"):
            currency = cube.attrib['currency']
            rate = cube.attrib['rate']
            rates[currency] = float(rate)
        
        # Ημερομηνία ενημέρωσης
        time = root.find(".//{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube[@time]")
        update_date = time.attrib['time'] if time is not None else datetime.today().strftime('%Y-%m-%d')
        
        return rates, update_date
    except:
        return None, None

def switch_language():
    """Αλλαγή γλώσσας"""
    st.session_state.lang = "el" if st.session_state.lang == "en" else "en"

# Λήψη δεδομένων
exchange_rates, update_date = fetch_exchange_rates()
currencies = list(exchange_rates.keys()) if exchange_rates else ["EUR"]

# Δημιουργία διεπαφής
lang = LANGUAGES[st.session_state.lang]

st.title(lang["title"])

# Κουμπί αλλαγής γλώσσας
st.button("Ελληνικά / English", on_click=switch_language)

if exchange_rates:
    # Πεδίο εισαγωγής ποσού
    amount = st.number_input(lang["amount"], min_value=0.0, value=1.0)

    # Επιλογή νομισμάτων
    col1, col2 = st.columns(2)
    with col1:
        from_curr = st.selectbox(lang["from_curr"], currencies, index=0)
    with col2:
        to_curr = st.selectbox(lang["to_curr"], currencies, index=1)

    # Μετατροπή
    if st.button(lang["convert"]):
        try:
            converted_amount = (amount / exchange_rates[from_curr]) * exchange_rates[to_curr]
            st.success(f"**{lang['result']}:** {converted_amount:.2f} {to_curr}")
            st.caption(f"{lang['last_update']}: {update_date}")
        except:
            st.error(lang["error"])
else:
    st.error(lang["error"])
