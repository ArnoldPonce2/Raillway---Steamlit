import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from datetime import datetime

# -----------------------
# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Simulador Logístico CEMEX", layout="wide")
st.title("🚂 Simulador Logístico CEMEX")
st.markdown("Visualización de rutas, KPIs logísticos y alertas inteligentes.")

# -----------------------
# SIMULACIÓN DE DATOS
data = pd.DataFrame({
    "vehiculo": ["Camión 1"] * 3 + ["Tren 1"] * 3,
    "lat": [21.8823, 21.8850, 21.8900, 21.8700, 21.8750, 21.8800],
    "lon": [-102.2826, -102.2700, -102.2600, -102.3000, -102.2850, -102.2700],
    "timestamp": [
        "2025-07-01T08:00:00", "2025-07-01T08:30:00", "2025-07-01T09:00:00",
        "2025-07-01T08:15:00", "2025-07-01T08:45:00", "2025-07-01T09:15:00"
    ],
    "volumen_ton": [100, 120, 110, 90, 130, 95]
})
data["timestamp"] = pd.to_datetime(data["timestamp"])

# -----------------------
# CONTROLES DE USUARIO
if not data.empty:
    sim_time = st.slider("Selecciona el tiempo de simulación",
                         min_value=data["timestamp"].min(),
                         max_value=data["timestamp"].max(),
                         value=data["timestamp"].min(),
                         format="HH:mm")
else:
    st.error("No hay datos disponibles para simular.")
    st.stop()

# -----------------------
# MAPA
m = folium.Map(location=[21.88, -102.28], zoom_start=13)

# Filtra y pinta los puntos activos a la hora seleccionada
for vehiculo in data["vehiculo"].unique():
    df_v = data[(data["vehiculo"] == vehiculo) & (data["timestamp"] <= sim_time)]
    if not df_v.empty:
        folium.PolyLine(df_v[["lat", "lon"]].values, color="blue" if "Camión" in vehiculo else "green").add_to(m)
        folium.Marker(location=df_v.iloc[-1][["lat", "lon"]],
                      popup=f"{vehiculo} - {df_v.iloc[-1]['volumen_ton']} ton").add_to(m)

st.subheader("🗺️ Mapa de rutas")
st_folium(m, width=700)

# -----------------------
# KPIs
st.subheader("📊 KPI - Volumen transportado")
kpi = data[data["timestamp"] <= sim_time].groupby("vehiculo")["volumen_ton"].sum()

fig = go.Figure()
for vehiculo in kpi.index:
    fig.add_trace(go.Bar(name=vehiculo, x=[vehiculo], y=[kpi[vehiculo]]))
fig.update_layout(barmode='group', yaxis_title="Toneladas")
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# ALERTAS
st.subheader("⚠️ Alertas")
if any(kpi > 120):
    st.error("¡Alerta! Un vehículo está transportando más de 120 toneladas.")
elif sim_time == data["timestamp"].max():
    st.success("✅ Simulación completada sin alertas.")
else:
    st.info("Simulación en curso. Sin anomalías detectadas.")
