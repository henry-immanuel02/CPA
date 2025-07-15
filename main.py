import streamlit as st
from functions import *
from users import *

# Inisialisasi session state login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Routing antar halaman
if st.session_state.logged_in:
    main_dashboard()
else:
    login_page()