import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import streamlit as st
from users import *
import requests
import io


def loss_ratio(claims, gep):
    return claims/gep

def ri_cost(erp, erc, ri_claims, gep):
    return (erp - erc - ri_claims)/gep

def comm_ratio(comm, gwp):
    return (comm/gwp)


# Fungsi halaman login
def login_page():
    st.title("MNC Insurance Actuarial Data Analysis Dashboard!")
    st.subheader("Created by Actuary Department")

    st.write("Aplikasi ini masih dalam tahap pengembangan, request dapat dikirimkan via email ke henry.sihombing@mnc-insurance.com")
    name = st.text_input("Masukkan nama Anda:")
    
    if name in our_users:
        password = st.text_input("Masukkan password:", type="password")
        if password == our_users[name]:
            st.session_state.logged_in = True
            st.session_state.username = name
            st.rerun()
        elif password:
            st.error("Password salah!")
    elif name:
        st.warning("Nama tidak ditemukan.")


# Fungsi halaman utama setelah login
import pandas as pd
import altair as alt



def multiselect_dropdown(label, options, key_prefix):
    key = f"{key_prefix}_selected"
    trigger_select_all = f"{key_prefix}_select_all_trigger"
    trigger_clear = f"{key_prefix}_clear_trigger"
    trigger_clear_all = "clear_all_filters_trigger"

    # Set default session state
    if key not in st.session_state:
        st.session_state[key] = []

    # Trigger individual "select all"
    if st.session_state.get(trigger_select_all, False):
        st.session_state[key] = options
        st.session_state[trigger_select_all] = False

    # Trigger individual "clear"
    if st.session_state.get(trigger_clear, False):
        st.session_state[key] = []
        st.session_state[trigger_clear] = False

    # Trigger global "clear all"
    if st.session_state.get(trigger_clear_all, False):
        st.session_state[key] = []

    col1, col2, col3 = st.columns([5, 1, 1])
    selected = col1.multiselect(label, options=options, default=st.session_state[key], key=key)

    col2.button("☑️", key=f"{key_prefix}_select_all", help="Select all", 
                on_click=lambda: st.session_state.update({trigger_select_all: True}))
    col3.button("🗑️", key=f"{key_prefix}_clear", help="Clear selection", 
                on_click=lambda: st.session_state.update({trigger_clear: True}))

    return selected



def main_dashboard():
    st.set_page_config(layout="wide")
    st.title("MNC Insurance Actuarial Data Analysis Dashboard")
    st.subheader("Created by Actuary Department")
    st.write("Request ke henry.sihombing@mnc-insurance.com")
    file_url = "https://drive.google.com/uc?export=download&id=1MMW6WShqSni52onkXLnOOG5bD_IBMzDz"
    
    # Ambil file dari Google Drive
    response = requests.get(file_url)
    response.raise_for_status()  # Biar error-nya ketangkep kalau gagal download

    # Baca file Parquet langsung dari memory
    df = pd.read_parquet(io.BytesIO(response.content))

    st.sidebar.header("Filter Data")

    # Prepare filter options
    all_cob = sorted(df['COB'].dropna().unique().tolist())
    all_fronting = sorted(df['IS_FRONTING'].dropna().unique().tolist())
    all_account = sorted(df['ACCOUNT_NAME'].dropna().unique().tolist())
    all_insured = sorted(df['INSURED_NAME'].dropna().unique().tolist())
    all_policy = sorted(df['POLICY_NO'].dropna().unique().tolist())


    # Tombol clear all
    if st.sidebar.button("Reset All Filters"):
        st.session_state["clear_all_filters_trigger"] = True
        st.rerun()
    else:
        st.session_state["clear_all_filters_trigger"] = False  # Reset setelah klik

    with st.sidebar.expander("COB"):
        selected_cob = multiselect_dropdown("COB", all_cob, "cob")

    with st.sidebar.expander("IS_FRONTING"):
        selected_fronting = multiselect_dropdown("IS_FRONTING", all_fronting, "fronting")

    with st.sidebar.expander("ACCOUNT_NAME"):
        selected_account = multiselect_dropdown("ACCOUNT_NAME", all_account, "account")

    with st.sidebar.expander("INSURED_NAME"):
        selected_insured = multiselect_dropdown("INSURED_NAME", all_insured, "insured")

    with st.sidebar.expander("POLICY_NO"):
        selected_policy = multiselect_dropdown("POLICY_NO", all_policy, "policy")

    # Apply filters
    if selected_cob:
        df = df[df['COB'].isin(selected_cob)]
    if selected_fronting:
        df = df[df['IS_FRONTING'].isin(selected_fronting)]
    if selected_account:
        df = df[df['ACCOUNT_NAME'].isin(selected_account)]
    if selected_insured:
        df = df[df['INSURED_NAME'].isin(selected_insured)]
    if selected_policy:
        df = df[df['POLICY_NO'].isin(selected_policy)]

    st.info(f"Jumlah baris data setelah filter: {len(df):,}")
    if df.empty:
        st.warning("Tidak ada data yang sesuai dengan filter.")
        return

    rp_1 = df.pivot_table(index = 'UW_YEAR', values = ['OUR_SUM_INSURED', 'POLICY_UNIT_NO', 'NO_OF_CLAIM' ,'GROSS_WRITTEN_PREMIUM', 'GEP', 'OUR_COMMISSION', 'AMT_GROSS_CLAIM'],
                          aggfunc={'OUR_SUM_INSURED':'sum', 'POLICY_UNIT_NO':'count', 'NO_OF_CLAIM': 'sum','GROSS_WRITTEN_PREMIUM':'sum', 'GEP':'sum', 'OUR_COMMISSION':'sum', 'AMT_GROSS_CLAIM':'sum'})
    rp_1 = rp_1[[
    'OUR_SUM_INSURED',
    'POLICY_UNIT_NO',
    'NO_OF_CLAIM',
    'GROSS_WRITTEN_PREMIUM',
    'GEP',
    'OUR_COMMISSION',
    'AMT_GROSS_CLAIM'
    ]]
    rp_1['LOSS_RATIO'] = (loss_ratio(rp_1['AMT_GROSS_CLAIM'], rp_1['GEP']))
    formatted_rp_1 = rp_1.style.format({
    'OUR_SUM_INSURED': '{:,.0f}',
    'POLICY_UNIT_NO': '{:,.0f}',
    'NO_OF_CLAIM': '{:,.0f}',
    'GROSS_WRITTEN_PREMIUM': '{:,.0f}',
    'GEP': '{:,.0f}',
    'OUR_COMMISSION': '{:,.0f}',
    'AMT_GROSS_CLAIM': '{:,.0f}',
    'LOSS_RATIO': '{:.2%}'
    })
    st.markdown("Summary Risk Profile")
    st.dataframe(formatted_rp_1, use_container_width=True)

    st.subheader("Combined Ratio Calculator")
    CoR = df.pivot_table(index = 'UW_YEAR', values = ['GROSS_WRITTEN_PREMIUM', 'GEP', 'AMT_GROSS_CLAIM', 'AMT_RI_CLAIM', 'ERP', 'ERC'],
                          aggfunc={'GROSS_WRITTEN_PREMIUM':'sum', 'GEP':'sum', 'AMT_GROSS_CLAIM':'sum', 'AMT_RI_CLAIM': 'sum', 'ERP': 'sum', 'ERC': 'sum'})
    CoR['LOSS RATIO'] = (loss_ratio(rp_1['AMT_GROSS_CLAIM'], rp_1['GEP']))
    CoR['RI COST/(GAIN)'] = (ri_cost(CoR['ERP'], CoR['ERC'], CoR['AMT_RI_CLAIM'], CoR['GEP']))
    with st.form("form_persen"):
        comm_ojk = st.number_input(
            "COMM OJK (%)", 
            min_value=0.0, 
            max_value=100.0,
            value=25.0, 
            step=0.1, 
            format="%.1f"
        )
        comm_ovr = st.number_input(
            "COMM OVR (%)", 
            min_value=0.0, 
            max_value=100.0,
            value=15.0, 
            step=0.1, 
            format="%.1f"
        )
        
        # HARUS ADA DI SINI
        submit = st.form_submit_button("Submit")

    if submit:
        CoR['COMM (OJK)'] = comm_ojk/100
        CoR['COMM (OVR)'] =  comm_ovr/100
        CoR['OPEX'] = 0.15
        CoR['CoR'] = CoR['LOSS RATIO'] + CoR['RI COST/(GAIN)'] + CoR['COMM (OJK)'] + CoR['COMM (OVR)'] + CoR['OPEX']
        CoR_shown = CoR[['LOSS RATIO', 'RI COST/(GAIN)', 'COMM (OJK)', 'COMM (OVR)', 'OPEX', 'CoR']]
        formatted_CoR = CoR_shown.style.format({
            'LOSS RATIO': '{:.2%}',
            'RI COST/(GAIN)': '{:.2%}',
            'OPEX': '{:.2%}',
            'COMM (OJK)':'{:.2%}',
            'COMM (OVR)':'{:.2%}',
            'CoR':'{:.2%}'
            })
        
        st.dataframe(formatted_CoR, use_container_width=True)
            # Siapkan data chart
        CoR_chart = CoR.reset_index()[['UW_YEAR', 'CoR']]
        CoR_chart['color'] = CoR_chart['CoR'].apply(lambda x: 'red' if x > 1 else 'green')
        CoR_chart['label'] = (CoR_chart['CoR'] * 100).round(1).astype(str) + '%'

        # Bar chart dengan warna kondisi
        bar = alt.Chart(CoR_chart).mark_bar().encode(
            x=alt.X('UW_YEAR:O', title='UW Year', axis=alt.Axis(labelAngle=0)),  # =H label horizontal
            y=alt.Y('CoR:Q', title='Combined Ratio', axis=alt.Axis(format='%')),
            color=alt.Color('color:N', scale=None, legend=None),
            tooltip=[
                alt.Tooltip('UW_YEAR', title='UW Year'),
                alt.Tooltip('CoR', title='CoR', format='.2%')
            ]
        )

        # Label CoR di atas bar
        text = alt.Chart(CoR_chart).mark_text(
            dy=-10,
            size=12,
            fontWeight='bold'
        ).encode(
            x='UW_YEAR:O',
            y='CoR:Q',
            text='label',
            color=alt.value('black')
        )

        st.markdown("### Combined Ratio per UW Year")
        st.altair_chart((bar + text).properties(width=700, height=400), use_container_width=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
