# Language selector with hidden label
st.write("<div style='float:right'>", unsafe_allow_html=True)
new_lang = st.selectbox(
    "Language",  # Now has a label
    options=list(LANGUAGES.keys()),
    format_func=lambda x: x.upper(),
    index=list(LANGUAGES.keys()).index(lang),
    label_visibility="hidden"  # Hide the label visually
)
if new_lang != lang:
    st.query_params.update({"lang": new_lang})
    st.rerun()
st.write("</div>", unsafe_allow_html=True)
