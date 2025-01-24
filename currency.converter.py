import streamlit as st
import requests
import xml.etree.ElementTree as ET

LANGUAGES = {
    "en": {"title": "💰 Currency Converter", "amount": "Amount", "convert": "Convert", 
           "from_curr": "From", "to_curr": "To", "result": "Result"},
    "el": {"title": "💰 Μετατροπέας", "amount": "Ποσό", "convert": "Μετατροπή",
           "from_curr": "Από", "to_curr": "Σε", "result": "Αποτέλεσμα"},
    "es": {"title": "💰 Conversor Divisas", "amount": "Cantidad", "convert": "Convertir",
           "from_curr": "De", "to_curr": "A", "result": "Resultado"},
    "fr": {"title": "💰 Convertisseur", "amount": "Montant", "convert": "Convertir",
           "from_curr": "De", "to_curr": "À", "result": "Résultat"},
    "de": {"title": "💰 Währungsrechner", "amount": "Betrag", "convert": "Konvertieren",
           "from_curr": "Von", "to_curr": "Zu", "result": "Ergebnis"},
}

# Get language from URL params
params = st.query_params.to_dict()
lang_param = params.get("lang", ["en"])
lang = lang_param[0][:2].lower() if lang_param else "en"
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

# HTML for language selector floating right
st.write("""
<div style='float: right; margin-top: -60px;'>
    <div class="stSelectbox">
""", unsafe_allow_html=True)

# Language selector (Streamlit component inside HTML)
new_lang = st.selectbox(
    label="Language",
    options=list(LANGUAGES.keys()),
    format_func=lambda x: x.upper(),
    index=list(LANGUAGES.keys()).index(lang),
    key="lang_selector"
)

# Close HTML divs
st.write("""
    </div>
</div>
""", unsafe_allow_html=True)

# Update query params if language changed
if new_lang != lang:
    st.query_params["lang"] = new_lang
    st.rerun()

# Main app content
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
