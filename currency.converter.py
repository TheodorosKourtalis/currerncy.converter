import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 10 languages with minimal translations
LANGUAGES = {
    "en": {"title": "💰 Currency Converter", "amount": "Amount", "convert": "Convert", "from_curr": "From", "to_curr": "To", "result": "Result"},
    "es": {"title": "💰 Conversor Divisas", "amount": "Cantidad", "convert": "Convertir", "from_curr": "De", "to_curr": "A", "result": "Resultado"},
    "fr": {"title": "💰 Convertisseur", "amount": "Montant", "convert": "Convertir", "from_curr": "De", "to_curr": "À", "result": "Résultat"},
    "de": {"title": "💰 Währungsrechner", "amount": "Betrag", "convert": "Konvertieren", "from_curr": "Von", "to_curr": "Zu", "result": "Ergebnis"},
    "it": {"title": "💰 Convertitore", "amount": "Importo", "convert": "Converti", "from_curr": "Da", "to_curr": "A", "result": "Risultato"},
    "pt": {"title": "💰 Conversor", "amount": "Quantia", "convert": "Converter", "from_curr": "De", "to_curr": "Para", "result": "Resultado"},
    "nl": {"title": "💰 Valutaomzetter", "amount": "Bedrag", "convert": "Converteer", "from_curr": "Van", "to_curr": "Naar", "result": "Resultaat"},
    "ja": {"title": "💰 通貨換算", "amount": "金額", "convert": "変換", "from_curr": "から", "to_curr": "へ", "result": "結果"},
    "zh": {"title": "💰 货币转换", "amount": "金额", "convert": "转换", "from_curr": "从", "to_curr": "到", "result": "结果"},
    "ru": {"title": "💰 Конвертер", "amount": "Сумма", "convert": "Конвертировать", "from_curr": "Из", "to_curr": "В", "result": "Результат"}
}

# Get language from URL params (new method)
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

# Language selector using query params
with st.sidebar:
    new_lang = st.selectbox(
        "🌐 Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: x.upper(),
        index=list(LANGUAGES.keys()).index(lang)
    )
    if new_lang != lang:
        st.query_params["lang"] = new_lang
        st.rerun()

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
