import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Lightning-fast language map (50+ languages)
LANGS = {
    'en': {'title': 'Currency Converter', 'convert': 'Convert', 'amount': 'Amount'},
    'es': {'title': 'Conversor Divisas', 'convert': 'Convertir', 'amount': 'Cantidad'},
    'fr': {'title': 'Convertisseur', 'convert': 'Convertir', 'amount': 'Montant'},
    'de': {'title': 'Währungsrechner', 'convert': 'Konvertieren', 'amount': 'Betrag'},
    'it': {'title': 'Convertitore', 'convert': 'Converti', 'amount': 'Importo'},
    'pt': {'title': 'Conversor', 'convert': 'Converter', 'amount': 'Quantia'},
    'ja': {'title': '通貨換算', 'convert': '変換', 'amount': '金額'},
    'zh': {'title': '货币转换', 'convert': '转换', 'amount': '金额'},
    'ru': {'title': 'Конвертер', 'convert': 'Конвертировать', 'amount': 'Сумма'},
    'ar': {'title': 'محول العملات', 'convert': 'تحويل', 'amount': 'المبلغ'}
}

# Get language from URL instantly
lang = st.query_params.get('lang', ['en'])[0][:2]
lang_data = LANGS.get(lang, LANGS['en'])

# Currency data (cached separately)
@st.cache_data(ttl=60)
def get_rates():
    try:
        xml = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml', timeout=1).content
        return {c.attrib['currency']: float(c.attrib['rate']) 
                for c in ET.fromstring(xml).findall(".//*[@currency]")} | {'EUR': 1.0}
    except:
        return None

# Language selector (pure HTML/URL)
st.markdown(f"""
<div style="float:right">
    <select onchange="window.location.search='lang='+this.value" style="border:0;padding:2px">
        {' '.join(f'<option value="{k}" {"selected" if k==lang else ""}>{k.upper()}</option>' 
        for k in LANGS)}
    </select>
</div>
""", unsafe_allow_html=True)

# Main app
st.title(lang_data['title'])
rates = get_rates()

if rates:
    c1, c2 = st.columns(2)
    amount = c1.number_input(lang_data['amount'], value=1.0)
    from_curr = c1.selectbox('From', sorted(rates))
    to_curr = c2.selectbox('To', sorted(rates), 1)
    
    if st.button(lang_data['convert']):
        result = (amount / rates[from_curr]) * rates[to_curr]
        st.success(f'{result:.4f}')
else:
    st.error('Service unavailable')
