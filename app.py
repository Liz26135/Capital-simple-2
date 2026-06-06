
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Strategic Capital Allocation Dashboard", layout="wide")
st.title("Strategic Capital Allocation Dashboard")

uploaded_file = st.file_uploader("Sube un archivo Excel", type=["xlsx"])

def recommend_projects(df, budget):
    df = df.copy()
    df["Score"] = df["VPN"] / df["CAPEX"]
    df = df.sort_values("Score", ascending=False)

    approved, rejected = [], []
    spent = 0

    for _, row in df.iterrows():
        if spent + row["CAPEX"] <= budget:
            approved.append(row)
            spent += row["CAPEX"]
        else:
            rejected.append(row)

    return pd.DataFrame(approved), pd.DataFrame(rejected)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Datos cargados")
    st.dataframe(df)

    business_units = st.multiselect(
        "Unidad de Negocio",
        options=df["Unidad de Negocio"].unique(),
        default=list(df["Unidad de Negocio"].unique())
    )

    project_types = st.multiselect(
        "Tipo de Proyecto",
        options=df["Tipo"].unique(),
        default=list(df["Tipo"].unique())
    )

    max_capital = float(df["CAPEX"].sum())
    budget = st.slider("Capital disponible", 0.0, max_capital, max_capital)

    filtered = df[
        (df["Unidad de Negocio"].isin(business_units)) &
        (df["Tipo"].isin(project_types))
    ]

    st.subheader("KPIs")
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Capital Total", f"{filtered['CAPEX'].sum():,.0f}")
    c2.metric("VPN Total", f"{filtered['VPN'].sum():,.0f}")
    c3.metric("ROI Promedio", f"{filtered['ROI esperado'].mean():.2f}")
    c4.metric("Proyectos", len(filtered))
    c5.metric("Riesgo Promedio", f"{filtered['Volatilidad'].mean():.2f}")

    st.subheader("Visualizaciones")

    st.plotly_chart(px.bar(filtered, x="Proyecto", y="VPN", title="VPN por Proyecto"), use_container_width=True)
    st.plotly_chart(px.scatter(filtered, x="CAPEX", y="VPN", hover_name="Proyecto", title="CAPEX vs VPN"), use_container_width=True)
    st.plotly_chart(px.scatter(filtered, x="CAPEX", y="ROI esperado", size="Volatilidad",
                               hover_name="Proyecto", title="Bubble CAPEX vs ROI"), use_container_width=True)
    st.plotly_chart(px.pie(filtered, names="Unidad de Negocio", values="CAPEX",
                           title="CAPEX por Unidad de Negocio"), use_container_width=True)
    st.plotly_chart(px.histogram(filtered, x="ROI esperado", title="Histograma ROI"), use_container_width=True)

    corr_cols = ["CAPEX", "VPN", "ROI esperado", "Volatilidad", "Probabilidad de éxito", "Duración"]
    corr = filtered[corr_cols].corr(numeric_only=True)

    st.plotly_chart(px.imshow(corr, text_auto=True, title="Heatmap de Correlación"),
                    use_container_width=True)

    st.subheader("Curva de Markowitz")

    returns = filtered["ROI esperado"].values
    risks = filtered["Volatilidad"].values

    n_assets = len(filtered)

    if n_assets >= 2:
        portfolios = 2000
        port_returns = []
        port_risks = []
        sharpe = []

        for _ in range(portfolios):
            w = np.random.random(n_assets)
            w /= w.sum()

            r = np.dot(w, returns)
            risk = np.sqrt(np.dot(w**2, risks**2))

            port_returns.append(r)
            port_risks.append(risk)
            sharpe.append(r / risk if risk > 0 else 0)

        best = int(np.argmax(sharpe))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=port_risks,
            y=port_returns,
            mode="markers",
            name="Portafolios"
        ))

        fig.add_trace(go.Scatter(
            x=[port_risks[best]],
            y=[port_returns[best]],
            mode="markers",
            marker=dict(size=14),
            name="Mejor Sharpe"
        ))

        fig.update_layout(title="Riesgo vs Retorno")
        st.plotly_chart(fig, use_container_width=True)

    approved, rejected = recommend_projects(filtered, budget)

    st.subheader("Recomendación de Inversión")

    st.write("### Proyectos Aprobados")
    st.dataframe(approved)

    st.write("### Proyectos Rechazados")
    st.dataframe(rejected)

else:
    st.info("Sube un archivo Excel para comenzar.")
