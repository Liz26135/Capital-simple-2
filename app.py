
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide", page_title="Strategic Capital Allocation Optimizer")

st.title("Strategic Capital Allocation Optimizer")

uploaded = st.file_uploader("Sube archivo Excel", type=["xlsx"])

st.sidebar.header("Restricciones")
capital = st.sidebar.number_input("Capital disponible", value=1000000.0)

if uploaded:
    df = pd.read_excel(uploaded)
    st.dataframe(df)

    if "CAPEX" in df.columns and "VPN" in df.columns:
        aprobados = df[df["CAPEX"].cumsum() <= capital]
        st.metric("Proyectos aprobados", len(aprobados))
        st.metric("VPN esperado", float(aprobados["VPN"].sum()))

        fig = px.scatter(df, x="CAPEX", y="VPN", hover_name=df.columns[1] if len(df.columns)>1 else None)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Carga el dataset para iniciar.")
