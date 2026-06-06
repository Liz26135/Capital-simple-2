import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# Configuración de la página
st.set_page_config(layout="wide", page_title="Capital Allocation Optimizer", page_icon="📊")
st.title("Strategic Capital Allocation Optimizer (Académico)")

st.write("Modelo simplificado de frontera eficiente para asignación de capital entre proyectos.")

# --- SECCIÓN NUEVA: GENERADOR DE DATOS DUMMY ---
st.sidebar.header("⚙️ Generador de Datos de Prueba")
if st.sidebar.button("Generar Excel de Prueba"):
    # Crear datos aleatorios realistas
    np.random.seed(42)
    num_proyectos = 10
    datos_dummy = {
        "Proyecto": [f"Proyecto {chr(65 + i)}" for i in range(num_proyectos)],
        "CAPEX": np.random.randint(100000, 500000, size=num_proyectos),
        "ROI esperado": np.round(np.random.uniform(0.08, 0.25, size=num_proyectos), 4),
        "Volatilidad": np.round(np.random.uniform(0.04, 0.18, size=num_proyectos), 4)
    }
    df_creado = pd.DataFrame(datos_dummy)
    
    # Guardar en un buffer de memoria para la descarga
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_creado.to_excel(writer, index=False, sheet_name='Proyectos')
    
    # Botón de descarga invisible/automático en la barra lateral
    st.sidebar.success("¡Excel generado con éxito!")
    st.sidebar.download_button(
        label="📥 Descargar proyectos_dummy.xlsx",
        data=buffer.getvalue(),
        file_name="proyectos_dummy.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
st.sidebar.markdown("---")

# --- BLOQUE PRINCIPAL DE LA APLICACIÓN ---
st.sidebar.header("Parámetros de Optimización")
simulaciones = st.sidebar.slider("Simulaciones Monte Carlo", 100, 5000, 1000, 100)
capital_total = st.sidebar.number_input("Capital disponible ($)", value=1000000.0, step=50000.0)

archivo = st.file_uploader("Cargar archivo Excel con los proyectos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    columnas_requeridas = ["Proyecto", "CAPEX", "ROI esperado", "Volatilidad"]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]

    if faltantes:
        st.error(f"❌ Error: El archivo no contiene las columnas requeridas: {faltantes}")
    else:
        st.subheader("📋 Datos de los Proyectos Cargados")
        st.dataframe(df.style.format({
            "CAPEX": "${:,.2f}",
            "ROI esperado": "{:.2%}",
            "Volatilidad": "{:.2%}"
        }))

        retornos = df["ROI esperado"].values
        riesgos = df["Volatilidad"].values
        n = len(df)

        resultados = []
        pesos_guardados = []

        for _ in range(simulaciones):
            pesos = np.random.random(n)
            pesos /= pesos.sum()

            retorno = np.dot(pesos, retornos)
            riesgo = np.sqrt(np.sum((pesos * riesgos) ** 2))
            sharpe = retorno / max(riesgo, 1e-6)

            resultados.append([retorno, riesgo, sharpe])
            pesos_guardados.append(pesos)

        frontera = pd.DataFrame(resultados, columns=["Retorno", "Riesgo", "Sharpe"])
        idx = frontera["Sharpe"].idxmax()
        mejores_pesos = pesos_guardados[idx]

        st.subheader("📈 Frontera Eficiente (Simulación)")
        fig = px.scatter(
            frontera,
            x="Riesgo",
            y="Retorno",
            color="Sharpe",
            labels={"Riesgo": "Volatilidad del Portafolio", "Retorno": "ROI Esperado"},
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🎯 Asignación de Capital Recomendada (Max Sharpe)")
        asignacion = pd.DataFrame({
            "Proyecto": df["Proyecto"],
            "Peso %": mejores_pesos * 100,
            "Capital Asignado": mejores_pesos * capital_total
        })

        st.dataframe(asignacion.style.format({
            "Peso %": "{:.2f}%",
            "Capital Asignado": "${:,.2f}"
        }))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sharpe Máximo", round(frontera.loc[idx, "Sharpe"], 2))
        with col2:
            st.metric("ROI Esperado", f"{round(frontera.loc[idx, 'Retorno'] * 100, 2)}%")
        with col3:
            st.metric("Volatilidad", f"{round(frontera.loc[idx, 'Riesgo'] * 100, 2)}%")
else:
    st.info("💡 Por favor, carga un archivo Excel o usa el generador de la barra lateral izquierda.")