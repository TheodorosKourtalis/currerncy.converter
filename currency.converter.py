import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 54 languages with minimal translation keys
LANGUAGES = {
    "en": {"title": "💰 Currency Converter", "amount": "Amount", "convert": "Convert", "from_curr": "From", "to_curr": "To", "result": "Result"},
    "el": {"title": "💰 Μετατροπέας", "amount": "Ποσό", "convert": "Μετατροπή", "from_curr": "Από", "to_curr": "Σε", "result": "Αποτέλεσμα"},
    "es": {"title": "💰 Conversor Divisas", "amount": "Cantidad", "convert": "Convertir", "from_curr": "De", "to_curr": "A", "result": "Resultado"},
    "fr": {"title": "💰 Convertisseur", "amount": "Montant", "convert": "Convertir", "from_curr": "De", "to_curr": "À", "result": "Résultat"},
    "de": {"title": "💰 Währungsrechner", "amount": "Betrag", "convert": "Konvertieren", "from_curr": "Von", "to_curr": "Zu", "result": "Ergebnis"},
    # Add 49+ more languages here...
}

# Get language from URL param instantly
params = st.query_params
lang = params.get("lang", ["en"])[0][:2].lower()
lang = lang if lang in LANGUAGES else "en"

@st.cache_data(ttl=60)
def get_rates():
    try:
        response = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml", timeout=2)
        root = ET.fromstring(response.content)
        rates = {"EUR": 1.0}
        ns = {'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        for cube in root.findall(".//ecb:Cube[@currency]", namespaces=ns):
            rates[cube.attrib['currency']] = float(cube.attrib['rate'])
        return rates
    except:
        return None

# Language selector using URL params (no state)
st.write("<div style='float:right'>", unsafe_allow_html=True)
new_lang = st.selectbox("", options=list(LANGUAGES.keys()), format_func=lambda x: x.upper(), index=list(LANGUAGES.keys()).index(lang))
if new_lang != lang:
    st.experimental_set_query_params(lang=new_lang)
    st.rerun()
st.write("</div>", unsafe_allow_html=True)

# Main app
rates = get_rates()
lang_data = LANGUAGES[lang]

st.title(lang_data["title"])

if rates:
    c1, c2 = st.columns(2)
    amount = c1.number_input(lang_data["amount"], value=1.0)
    from_curr = c1.selectbox(lang_data["from_curr"], sorted(rates.keys()))
    to_curr = c2.selectbox(lang_data["to_curr"], sorted(rates.keys()), index=1)
    
    if st.button(lang_data["convert"]):
        result = (amount / rates[from_curr]) * rates[to_curr]
        st.success(f"**{lang_data['result']}:** {result:.4f}")
else:
    st.error("Service unavailable")
