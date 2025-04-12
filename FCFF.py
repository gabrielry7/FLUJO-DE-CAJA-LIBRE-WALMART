import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Flujo de Caja Libre - Walmart",
    page_icon="💵",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Flujo de Caja Libre - Walmart")
st.markdown("""
Esta aplicación te permite calcular y visualizar el Flujo de Caja Libre (FCF) de Walmart
bajo diferentes escenarios. Puedes ajustar las variables clave para ver cómo impactan los resultados financieros.
""")

# Datos históricos (extraídos de la imagen)
historical_data = {
    "Año": ["2023", "2024", "2025 Est"],
    "Ingresos": [648.13, 679.92, 715.12],
    "Crecimiento de Ingresos (%)": [6.0, 4.9, 5.2],
    "EBIT": [27.01, 29.96, 32.01],
    "Margen EBIT (%)": [4.2, 4.4, 4.5],
    "Impuestos": [5.58, 6.53, 6.91],
    "Tasa Impositiva (%)": [21, 22, 22],
    "EBIAT": [21.43, 23.42, 25.09],
    "Depreciación y Amortización": [11.85, 12.72, 13.39],
    "D&A (% de ingresos)": [1.8, 1.9, 1.9],
    "CAPEX": [20.61, 22.63, 19.16],
    "CAPEX (% de ingresos)": [3.2, 3.3, 2.7],
    "Cambio en Capital de Trabajo": [-1.94, -3.52, -2.16],
    "Cambio en WC (% de ingresos)": [-0.3, -0.5, -0.3],
    "FCF": [14.61, 17.03, 21.49]
}

df_historical = pd.DataFrame(historical_data)

# Crear tabs para diferentes secciones
tab1, tab2, tab3 = st.tabs(["Datos Históricos", "Proyección de FCF", "Análisis de Escenarios"])

with tab1:
    st.header("Datos Históricos")
    st.dataframe(df_historical, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución de Ingresos y EBIT")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_historical["Año"],
            y=df_historical["Ingresos"],
            name="Ingresos",
            marker_color="lightblue"
        ))
        fig1.add_trace(go.Scatter(
            x=df_historical["Año"],
            y=df_historical["EBIT"],
            name="EBIT",
            mode="lines+markers",
            marker_color="darkblue",
            yaxis="y2"
        ))
        fig1.update_layout(
            yaxis=dict(title="Ingresos (MM USD)"),
            yaxis2=dict(title="EBIT (MM USD)", overlaying="y", side="right"),
            hovermode="x unified"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Componentes del FCF")
        fig2 = px.bar(
            df_historical,
            x="Año",
            y=["EBIAT", "Depreciación y Amortización", "CAPEX", "Cambio en Capital de Trabajo"],
            barmode="group",
            title="Componentes del Flujo de Caja Libre"
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Proyección de Flujo de Caja Libre")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros de Proyección")
        projection_years = st.slider("Años de proyección", 3, 10, 5)
        revenue_growth = st.slider("Crecimiento anual de ingresos (%)", 0.0, 10.0, 5.2, 0.1)
        ebit_margin = st.slider("Margen EBIT (%)", 3.0, 8.0, 4.5, 0.1)
        tax_rate = st.slider("Tasa impositiva (%)", 15.0, 30.0, 22.0, 0.5)
        da_percent = st.slider("D&A (% de ingresos)", 1.0, 3.0, 1.9, 0.1)
        capex_percent = st.slider("CAPEX (% de ingresos)", 1.0, 5.0, 2.7, 0.1)
        wc_percent = st.slider("Cambio en Capital de Trabajo (% de ingresos)", -2.0, 2.0, -0.3, 0.1)
    
    # Crear proyección
    last_revenue = df_historical["Ingresos"].iloc[-1]
    years = [f"202{i}" for i in range(5, 5 + projection_years)]
    
    projected_revenues = [last_revenue]
    for _ in range(projection_years):
        projected_revenues.append(projected_revenues[-1] * (1 + revenue_growth/100))
    projected_revenues = projected_revenues[1:]  # Eliminar el valor inicial
    
    projection_data = {
        "Año": years,
        "Ingresos": projected_revenues,
        "Crecimiento de Ingresos (%)": [revenue_growth] * projection_years,
        "EBIT": [rev * ebit_margin/100 for rev in projected_revenues],
        "Margen EBIT (%)": [ebit_margin] * projection_years,
        "Impuestos": [rev * ebit_margin/100 * tax_rate/100 for rev in projected_revenues],
        "Tasa Impositiva (%)": [tax_rate] * projection_years,
        "EBIAT": [rev * ebit_margin/100 * (1 - tax_rate/100) for rev in projected_revenues],
        "Depreciación y Amortización": [rev * da_percent/100 for rev in projected_revenues],
        "D&A (% de ingresos)": [da_percent] * projection_years,
        "CAPEX": [rev * capex_percent/100 for rev in projected_revenues],
        "CAPEX (% de ingresos)": [capex_percent] * projection_years,
        "Cambio en Capital de Trabajo": [rev * wc_percent/100 for rev in projected_revenues],
        "Cambio en WC (% de ingresos)": [wc_percent] * projection_years,
    }
    
    # Calcular FCF
    projection_data["FCF"] = [
        projection_data["EBIAT"][i] + projection_data["Depreciación y Amortización"][i] - 
        projection_data["CAPEX"][i] - projection_data["Cambio en Capital de Trabajo"][i]
        for i in range(projection_years)
    ]
    
    df_projection = pd.DataFrame(projection_data)
    
    with col2:
        st.subheader("Resultados de la Proyección")
        st.dataframe(df_projection.round(2), use_container_width=True)
    
    st.subheader("Proyección de Flujo de Caja Libre")
    fig3 = px.line(
        df_projection, 
        x="Año", 
        y="FCF",
        markers=True,
        title="Proyección de Flujo de Caja Libre"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Componentes del FCF
    st.subheader("Desglose de Componentes del FCF Proyectado")
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_projection["Año"],
        y=df_projection["EBIAT"],
        name="EBIAT",
        marker_color="green"
    ))
    fig4.add_trace(go.Bar(
        x=df_projection["Año"],
        y=df_projection["Depreciación y Amortización"],
        name="D&A (+)",
        marker_color="blue"
    ))
    fig4.add_trace(go.Bar(
        x=df_projection["Año"],
        y=[-x for x in df_projection["CAPEX"]],
        name="CAPEX (-)",
        marker_color="red"
    ))
    fig4.add_trace(go.Bar(
        x=df_projection["Año"],
        y=[-x for x in df_projection["Cambio en Capital de Trabajo"]],
        name="Cambio en WC (-)",
        marker_color="orange"
    ))
    fig4.add_trace(go.Scatter(
        x=df_projection["Año"],
        y=df_projection["FCF"],
        name="FCF",
        mode="lines+markers",
        line=dict(color="black", width=2)
    ))
    fig4.update_layout(barmode="relative")
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Análisis de Escenarios")
    
    st.markdown("""
    Compara diferentes escenarios ajustando los parámetros para cada uno.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Escenario Pesimista")
        pessimistic_growth = st.slider("Crecimiento de ingresos (%)", 0.0, 10.0, 3.0, 0.1, key="pes_growth")
        pessimistic_ebit = st.slider("Margen EBIT (%)", 2.0, 8.0, 3.5, 0.1, key="pes_ebit")
        pessimistic_capex = st.slider("CAPEX (% de ingresos)", 1.0, 6.0, 3.5, 0.1, key="pes_capex")
    
    with col2:
        st.subheader("Escenario Base")
        base_growth = st.slider("Crecimiento de ingresos (%)", 0.0, 10.0, 5.0, 0.1, key="base_growth")
        base_ebit = st.slider("Margen EBIT (%)", 2.0, 8.0, 4.5, 0.1, key="base_ebit")
        base_capex = st.slider("CAPEX (% de ingresos)", 1.0, 6.0, 2.7, 0.1, key="base_capex")
    
    with col3:
        st.subheader("Escenario Optimista")
        optimistic_growth = st.slider("Crecimiento de ingresos (%)", 0.0, 10.0, 6.5, 0.1, key="opt_growth")
        optimistic_ebit = st.slider("Margen EBIT (%)", 2.0, 8.0, 5.5, 0.1, key="opt_ebit")
        optimistic_capex = st.slider("CAPEX (% de ingresos)", 1.0, 6.0, 2.0, 0.1, key="opt_capex")
    
    # Calcular escenarios
    projection_years = 5
    years = [f"202{i}" for i in range(5, 5 + projection_years)]
    
    # Función para calcular FCF en cada escenario
    def calculate_scenario(growth_rate, ebit_margin, capex_percent):
        last_revenue = df_historical["Ingresos"].iloc[-1]
        projected_revenues = [last_revenue]
        
        for _ in range(projection_years):
            projected_revenues.append(projected_revenues[-1] * (1 + growth_rate/100))
        projected_revenues = projected_revenues[1:]
        
        ebiat = [rev * ebit_margin/100 * (1 - tax_rate/100) for rev in projected_revenues]
        da = [rev * da_percent/100 for rev in projected_revenues]
        capex = [rev * capex_percent/100 for rev in projected_revenues]
        wc = [rev * wc_percent/100 for rev in projected_revenues]
        
        fcf = [ebiat[i] + da[i] - capex[i] - wc[i] for i in range(projection_years)]
        
        return {
            "Ingresos": projected_revenues,
            "EBIAT": ebiat,
            "FCF": fcf
        }
    
    # Calcular los tres escenarios
    pessimistic = calculate_scenario(pessimistic_growth, pessimistic_ebit, pessimistic_capex)
    base = calculate_scenario(base_growth, base_ebit, base_capex)
    optimistic = calculate_scenario(optimistic_growth, optimistic_ebit, optimistic_capex)
    
    # Mostrar resultados comparativos
    st.subheader("Comparación de Escenarios - FCF Proyectado")
    
    scenario_data = pd.DataFrame({
        "Año": years,
        "FCF Pesimista": pessimistic["FCF"],
        "FCF Base": base["FCF"],
        "FCF Optimista": optimistic["FCF"]
    })
    
    fig5 = px.line(
        scenario_data,
        x="Año",
        y=["FCF Pesimista", "FCF Base", "FCF Optimista"],
        title="Comparación de FCF en diferentes escenarios",
        markers=True
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # Tabla de resultados
    st.subheader("Resumen de Escenarios")
    
    scenario_summary = pd.DataFrame({
        "Medida": ["Crecimiento de Ingresos (%)", "Margen EBIT (%)", "CAPEX (% de ingresos)", 
                  "FCF Acumulado 5 años", "FCF Promedio Anual"],
        "Pesimista": [pessimistic_growth, pessimistic_ebit, pessimistic_capex, 
                     sum(pessimistic["FCF"]), sum(pessimistic["FCF"])/projection_years],
        "Base": [base_growth, base_ebit, base_capex, 
                sum(base["FCF"]), sum(base["FCF"])/projection_years],
        "Optimista": [optimistic_growth, optimistic_ebit, optimistic_capex, 
                     sum(optimistic["FCF"]), sum(optimistic["FCF"])/projection_years]
    })
    
    st.dataframe(scenario_summary.round(2), use_container_width=True)
    
    # Agregar visualización de barras para FCF acumulado
    st.subheader("FCF Acumulado por Escenario (5 años)")
    
    accumulated_data = pd.DataFrame({
        "Escenario": ["Pesimista", "Base", "Optimista"],
        "FCF Acumulado": [sum(pessimistic["FCF"]), sum(base["FCF"]), sum(optimistic["FCF"])]
    })
    
    fig6 = px.bar(
        accumulated_data,
        x="Escenario",
        y="FCF Acumulado",
        color="Escenario",
        text_auto=True,
        title="FCF Acumulado por Escenario (5 años)"
    )
    st.plotly_chart(fig6, use_container_width=True)

# Añadir notas y conclusiones
st.markdown("""
### Notas y Consideraciones

- El Flujo de Caja Libre (FCF) es una medida importante del efectivo que una empresa puede generar después de contabilizar los gastos operativos y de capital.
- La fórmula utilizada es: FCF = EBIAT + Depreciación y Amortización - CAPEX - Cambio en Capital de Trabajo
- Los factores clave que afectan el FCF incluyen el crecimiento de ingresos, márgenes operativos, inversiones de capital y gestión del capital de trabajo.
- Esta herramienta te permite explorar diferentes escenarios para la valuación de Walmart.

### Cómo usar esta aplicación

1. En la pestaña "Datos Históricos", puedes revisar la información financiera pasada.
2. En "Proyección de FCF", puedes ajustar los parámetros para crear una proyección personalizada.
3. En "Análisis de Escenarios", puedes comparar tres escenarios diferentes (pesimista, base y optimista).
""")