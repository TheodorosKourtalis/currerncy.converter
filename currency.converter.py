import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# ========== ΡΥΘΜΙΣΕΙΣ ==========
CURRENCIES = {
    "EUR": "Ευρώ 🇪🇺",
    "USD": "Δολάριο ΗΠΑ 🇺🇸",
    "GBP": "Λίρα Αγγλίας 🇬🇧",
    "JPY": "Γιεν Ιαπωνίας 🇯🇵",
    "BTC": "Bitcoin ₿",
    "CHF": "Φράγκο Ελβετίας 🇨🇭"
}

THEME = {
    "primary_color": "#2E86C1",
    "secondary_color": "#AED6F1",
    "font": "sans serif"
}

# ========== ΛΗΨΗ ΔΕΔΟΜΕΝΩΝ ==========
@st.cache_data(ttl=3600 * 3)  # Cache για 3 ώρες
def get_rates():
    rates = {"EUR": 1.0}
    
    try:
        # FIAT από ECB
        ecb_data = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml").text
        for line in ecb_data.split("\n"):
            if 'currency="' in line and 'rate="' in line:
                currency = line.split('currency="')[1].split('"')[0]
                rate = float(line.split('rate="')[1].split('"')[0])
                rates[currency] = rate
        
        # Crypto από CoinGecko (χωρίς API key)
        crypto = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur").json()
        rates["BTC"] = crypto["bitcoin"]["eur"]
    except Exception as e:
        st.error(f"Σφάλμα: {str(e)}")
    return rates

# ========== ΙΣΤΟΡΙΚΑ ΔΕΔΟΜΕΝΑ ==========
def get_history(base: str, target: str):
    symbol = f"{base}{target}=X" if base != "BTC" else f"{target}-{base}"
    try:
        data = yf.download(symbol, start=datetime.now() - timedelta(days=365), end=datetime.now())
        return data["Close"].reset_index()
    except:
        return pd.DataFrame()

# ========== UI ==========
def main():
    # Ρυθμίσεις σελίδας
    st.set_page_config(
        page_title="💰 Ultra Converter",
        page_icon="💶",
        layout="centered"
    )
    
    # Header
    st.markdown(f"<h1 style='text-align:center; color:{THEME['primary_color']};'>💰 ULTRA CURRENCY CONVERTER</h1>", unsafe_allow_html=True)
    
    # Μετατροπέας
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("**ΠΟΣΟ**", min_value=0.0, value=100.0, step=0.1)
            from_curr = st.selectbox("**ΑΠΟ**", options=CURRENCIES.keys(), format_func=lambda x: CURRENCIES[x])
        with col2:
            to_curr = st.selectbox("**ΣΕ**", options=CURRENCIES.keys(), format_func=lambda x: CURRENCIES[x])
        
        # Κουμπί μετατροπής
        if st.button("**ΜΕΤΑΤΡΟΠΗ 🔄**", use_container_width=True, type="primary"):
            rates = get_rates()
            if rates:
                converted = (amount / rates[from_curr]) * rates[to_curr]
                st.success(f"**{amount} {CURRENCIES[from_curr]} = {converted:.2f} {CURRENCIES[to_curr]}**")
            else:
                st.error("Δεν μπορώ να φέρω τα δεδομένα τώρα 😢")
    
    # Γράφημα
    st.markdown("---")
    st.subheader("📈 ΙΣΤΟΡΙΚΟ 1 ΕΤΟΥΣ")
    history = get_history(from_curr, to_curr)
    if not history.empty:
        fig = px.line(
            history, 
            x="Date", 
            y="Close", 
            labels={"Close": "Τιμή"},
            color_discrete_sequence=[THEME["primary_color"]]
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None,
            yaxis_title=f"{from_curr} → {to_curr}"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Δεν υπάρχουν δεδομένα για αυτή την ισοτιμία")

if __name__ == "__main__":
    main()
