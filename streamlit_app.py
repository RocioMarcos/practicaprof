# ==========================================================
# DASHBOARD DE ANÁLISIS DE TRÁFICO WEB - DGIPSE
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.colors import qualitative
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ==========================================================
# CONFIGURACIÓN INICIAL
# ==========================================================
st.set_page_config(
    page_title="Análisis de Tráfico DGIPSE", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados mejorados
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .anomaly-metric {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-left: 5px solid #ff6b6b;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3498db;
        font-weight: 600;
    }
    .plot-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e0e6ed;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER PRINCIPAL
# ==========================================================
st.markdown('<p class="main-header">📊 Dashboard Interactivo - Análisis de Tráfico Web</p>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 3rem; font-size: 1.2rem; color: #5a67d8;'>
    Monitoreo inteligente del tráfico web de <strong>dgipse.gob.ar</strong> 
    <br>Detección proactiva de anomalías y optimización del rendimiento
</div>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR CON CONFIGURACIONES
# ==========================================================
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    
    st.markdown("### 🔍 Parámetros de Análisis")
    contamination_rate = st.slider(
        "Sensibilidad detección anomalías", 
        min_value=0.01, 
        max_value=0.2, 
        value=0.05,
        help="Ajusta la sensibilidad del algoritmo para detectar comportamientos anómalos"
    )
    
    n_clusters = st.slider(
        "Número de clusters", 
        min_value=2, 
        max_value=5, 
        value=3,
        help="Número de grupos para segmentación de usuarios"
    )
    
    st.markdown("---")
    st.markdown("### 📈 Personalización Gráficos")
    theme = st.selectbox(
        "Tema de colores",
        ["Plotly", "Viridis", "Plasma", "Inferno", "Dark24"],
        help="Selecciona la paleta de colores para los gráficos"
    )
    
    st.markdown("---")
    st.markdown("#### 📊 Información")
    st.markdown("""
    **DGIPSE** - Dirección General de Informática y Procesamiento de Santiago del Estero
    
    🎯 **Objetivos:**
    - Monitoreo proactivo
    - Detección de bots
    - Optimización de recursos
    - Mejora experiencia usuario
    """)

# ==========================================================
# CARGA DE DATOS
# ==========================================================
st.markdown("### 📁 Carga de Datos")
uploaded_file = st.file_uploader(
    "Subí tu archivo `datos.json` para comenzar el análisis", 
    type=["json"], 
    help="Archivo JSON con los logs de acceso web en el formato especificado"
)

if uploaded_file:
    df = pd.read_json(uploaded_file)

    # ==========================================================
    # FUNCIONES AUXILIARES
    # ==========================================================
    def extract_browser(user_agent):
        browsers = {
            'Chrome': 'Chrome',
            'Firefox': 'Firefox', 
            'Safari': 'Safari',
            'Edge': 'Edge',
            'Opera': 'Opera'
        }
        for key, value in browsers.items():
            if key in user_agent:
                return value
        return 'Otros'

    def extract_os(user_agent):
        os_list = {
            'Windows': 'Windows',
            'Mac': 'Mac',
            'Linux': 'Linux',
            'Android': 'Android',
            'iOS': 'iOS'
        }
        for key, value in os_list.items():
            if key in user_agent:
                return value
        return 'Otros'

    def extract_device(user_agent):
        mobile_indicators = ['Mobile', 'Android', 'iPhone', 'iPad']
        if any(indicator in user_agent for indicator in mobile_indicators):
            return 'Móvil'
        return 'Desktop'

    def geolocate_ip(ip):
        ip_ranges = {
            '200.81': 'Argentina',
            '190.': 'Chile',
            '181.': 'Chile', 
            '200.1': 'Brasil',
            '186.': 'Colombia',
            '200.32': 'Uruguay',
            '200.3': 'Paraguay'
        }
        for prefix, country in ip_ranges.items():
            if ip.startswith(prefix):
                return country
        return 'Otros Países'

    def preprocess_data(df):
        df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y %I:%M:%S%p', errors='coerce')
        df['navegador'] = df['user_agent'].apply(extract_browser)
        df['sistema_operativo'] = df['user_agent'].apply(extract_os)
        df['dispositivo'] = df['user_agent'].apply(extract_device)
        static_extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.ttf']
        df['es_estatico'] = df['url'].str.contains('|'.join(static_extensions), case=False, na=False)
        df['pais'] = df['IP'].apply(geolocate_ip)
        df['hora'] = df['fecha'].dt.hour
        df['dia_semana'] = df['fecha'].dt.day_name()
        df['mes'] = df['fecha'].dt.month_name()
        return df

    # ==========================================================
    # PREPROCESAMIENTO
    # ==========================================================
    with st.spinner('🔄 Procesando datos y generando visualizaciones...'):
        df_processed = preprocess_data(df.copy())

    st.success(f"✅ **{len(df_processed):,} registros** procesados correctamente")

    # ==========================================================
    # MÉTRICAS CLAVE INTERACTIVAS
    # ==========================================================
    st.markdown("### 📊 Métricas Principales en Tiempo Real")

    # Cálculo de métricas
    features = df_processed.groupby('IP').agg({
        'fecha': 'count',
        'url': 'nunique',
        'hora': 'nunique'
    }).rename(columns={'fecha': 'total_requests', 'url': 'unique_pages', 'hora': 'unique_hours'})

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    iso_forest = IsolationForest(contamination=contamination_rate, random_state=42, n_estimators=100)
    anomalies = iso_forest.fit_predict(features_scaled)
    features['es_anomalia'] = np.where(anomalies == -1, 1, 0)

    metricas = {
        'Usuarios únicos': df_processed['IP'].nunique(),
        'Total de requests': len(df_processed),
        '% Móvil': (df_processed['dispositivo'] == 'Móvil').mean() * 100,
        'Navegador principal': df_processed['navegador'].mode()[0] if len(df_processed['navegador'].mode()) > 0 else 'N/A',
        'País predominante': df_processed['pais'].mode()[0] if len(df_processed['pais'].mode()) > 0 else 'N/A',
        '% Anomalías': features['es_anomalia'].mean() * 100,
        'IPs sospechosas': len(features[features['es_anomalia'] == 1])
    }

    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem; color: #667eea;">👥</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #2c3e50;">Usuarios Únicos</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #667eea;">{metricas['Usuarios únicos']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem; color: #764ba2;">📨</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #2c3e50;">Total Requests</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #764ba2;">{metricas['Total de requests']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem; color: #f093fb;">📱</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #2c3e50;">Tráfico Móvil</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #f093fb;">{metricas['% Móvil']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card anomaly-metric">
            <div style="font-size: 2rem; color: #ff6b6b;">🚨</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: #2c3e50;">Anomalías Detectadas</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: #ff6b6b;">{metricas['% Anomalías']:.2f}%</div>
            <div style="font-size: 0.9rem; color: #666;">{metricas['IPs sospechosas']} IPs</div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================================
    # VISUALIZACIONES INTERACTIVAS CON PLOTLY
    # ==========================================================
    st.markdown("---")
    st.markdown("## 📈 Análisis Visual Interactivo")

    # Fila 1: Tráfico por hora y Distribución geográfica
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 📊 Tráfico por Hora del Día")
        
        # Tráfico por hora
        trafico_por_hora = df_processed.groupby('hora').size().reset_index(name='count')
        
        fig_hora = px.area(
            trafico_por_hora, 
            x='hora', 
            y='count',
            title="Distribución Horaria del Tráfico",
            labels={'hora': 'Hora del Día', 'count': 'Número de Requests'},
            color_discrete_sequence=['#667eea']
        )
        
        fig_hora.update_layout(
            hovermode='x unified',
            showlegend=False,
            height=400,
            xaxis=dict(tickmode='linear', dtick=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        fig_hora.update_traces(
            hovertemplate="<b>Hora %{x}:00</b><br>%{y:,} requests<extra></extra>",
            fill='tozeroy'
        )
        
        st.plotly_chart(fig_hora, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 🌍 Distribución Geográfica")
        
        # Distribución por países
        pais_distribution = df_processed['pais'].value_counts().reset_index()
        pais_distribution.columns = ['pais', 'count']
        
        fig_pie = px.pie(
            pais_distribution,
            values='count',
            names='pais',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
        )
        
        fig_pie.update_traces(
            hovertemplate="<b>%{label}</b><br>%{value:,} requests (%{percent})<extra></extra>",
            textposition='inside',
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Fila 2: Dispositivos y Navegadores
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 📱 Distribución por Dispositivo")
        
        dispositivo_data = df_processed['dispositivo'].value_counts().reset_index()
        dispositivo_data.columns = ['dispositivo', 'count']
        
        fig_dev = px.bar(
            dispositivo_data,
            x='dispositivo',
            y='count',
            color='dispositivo',
            color_discrete_sequence=['#667eea', '#764ba2'],
            text='count'
        )
        
        fig_dev.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Cantidad de Requests",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        fig_dev.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y:,} requests<extra></extra>",
            texttemplate='%{y:,}',
            textposition='outside'
        )
        
        st.plotly_chart(fig_dev, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 🌐 Navegadores Más Utilizados")
        
        navegador_data = df_processed['navegador'].value_counts().reset_index()
        navegador_data.columns = ['navegador', 'count']
        
        fig_nav = px.pie(
            navegador_data,
            values='count',
            names='navegador',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig_nav.update_layout(
            height=400,
            showlegend=True
        )
        
        fig_nav.update_traces(
            hovertemplate="<b>%{label}</b><br>%{value:,} requests (%{percent})<extra></extra>",
            textposition='inside',
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig_nav, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Fila 3: Páginas más visitadas
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.markdown("#### 🔥 Top 10 Páginas Más Visitadas")
    
    paginas_populares = df_processed[~df_processed['es_estatico']]['url'].value_counts().head(10).reset_index()
    paginas_populares.columns = ['url', 'visitas']
    
    # Acortar URLs largas para mejor visualización
    paginas_populares['url_corto'] = paginas_populares['url'].apply(
        lambda x: x[:40] + '...' if len(x) > 40 else x
    )
    
    fig_paginas = px.bar(
        paginas_populares,
        y='url_corto',
        x='visitas',
        orientation='h',
        color='visitas',
        color_continuous_scale='viridis',
        text='visitas'
    )
    
    fig_paginas.update_layout(
        height=500,
        xaxis_title="Número de Visitas",
        yaxis_title="",
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig_paginas.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x:,} visitas<extra></extra>",
        texttemplate='%{x:,}',
        textposition='outside'
    )
    
    st.plotly_chart(fig_paginas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # ANÁLISIS AVANZADO INTERACTIVO
    # ==========================================================
    st.markdown("---")
    st.markdown("## 🧠 Análisis Avanzado - Machine Learning")

    col5, col6 = st.columns(2)

    with col5:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 🚨 Detección de Anomalías y Bots")
        
        # Preparar datos para el scatter plot
        scatter_data = features.reset_index()
        
        fig_anomalies = px.scatter(
            scatter_data,
            x='total_requests',
            y='unique_pages',
            color='es_anomalia',
            color_discrete_map={0: '#2ecc71', 1: '#e74c3c'},
            size='unique_hours',
            hover_data=['IP'],
            labels={
                'total_requests': 'Total de Requests por IP',
                'unique_pages': 'Páginas Únicas Visitadas',
                'es_anomalia': 'Es Anomalía'
            },
            title="Comportamiento de Usuarios vs Anomalías"
        )
        
        fig_anomalies.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig_anomalies.update_traces(
            hovertemplate="<b>IP: %{customdata[0]}</b><br>Requests: %{x}<br>Páginas únicas: %{y}<extra></extra>",
            marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey'))
        )
        
        st.plotly_chart(fig_anomalies, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 👥 Segmentación de Usuarios por Comportamiento")
        
        # K-Means Clustering
        cluster_features = features[['total_requests', 'unique_pages', 'unique_hours']].dropna()
        cluster_scaled = scaler.fit_transform(cluster_features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_features = cluster_features.copy()
        cluster_features['cluster'] = kmeans.fit_predict(cluster_scaled)
        
        fig_clusters = px.scatter(
            cluster_features.reset_index(),
            x='total_requests',
            y='unique_pages',
            color='cluster',
            color_continuous_scale='viridis',
            size='unique_hours',
            hover_data=['IP'],
            labels={
                'total_requests': 'Total de Requests por IP',
                'unique_pages': 'Páginas Únicas Visitadas',
                'cluster': 'Grupo'
            },
            title=f"Segmentación en {n_clusters} Grupos de Comportamiento"
        )
        
        fig_clusters.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        fig_clusters.update_traces(
            hovertemplate="<b>IP: %{customdata[0]}</b><br>Requests: %{x}<br>Páginas únicas: %{y}<br>Grupo: %{marker.color}<extra></extra>",
            marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey'))
        )
        
        st.plotly_chart(fig_clusters, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # ANÁLISIS TEMPORAL AVANZADO
    # ==========================================================
    st.markdown("---")
    st.markdown("## ⏰ Análisis Temporal Detallado")

    col7, col8 = st.columns(2)

    with col7:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 📅 Tráfico por Día de la Semana")
        
        dia_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dia_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        trafico_dia = df_processed['dia_semana'].value_counts().reindex(dia_orden)
        trafico_dia.index = dia_es
        
        fig_dia = px.bar(
            x=trafico_dia.index,
            y=trafico_dia.values,
            color=trafico_dia.values,
            color_continuous_scale='blues',
            text=trafico_dia.values
        )
        
        fig_dia.update_layout(
            height=400,
            xaxis_title="Día de la Semana",
            yaxis_title="Número de Requests",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        fig_dia.update_traces(
            hovertemplate="<b>%{x}</b><br>%{y:,} requests<extra></extra>",
            texttemplate='%{y:,}',
            textposition='outside'
        )
        
        st.plotly_chart(fig_dia, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col8:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.markdown("#### 🌙 Patrón de Actividad por Hora")
        
        # Heatmap de actividad por hora y dispositivo
        heatmap_data = df_processed.groupby(['hora', 'dispositivo']).size().unstack(fill_value=0)
        
        fig_heat = px.imshow(
            heatmap_data.T,
            labels=dict(x="Hora del Día", y="Dispositivo", color="Requests"),
            color_continuous_scale="YlOrRd",
            aspect="auto"
        )
        
        fig_heat.update_layout(
            height=400,
            xaxis=dict(tickmode='linear', dtick=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        fig_heat.update_traces(
            hovertemplate="<b>Hora %{x}:00</b><br>Dispositivo: %{y}<br>Requests: %{z:,}<extra></extra>"
        )
        
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # PANEL DE CONTROL Y DESCARGAS
    # ==========================================================
    st.markdown("---")
    st.markdown("## 🎛️ Panel de Control y Exportación")

    tab1, tab2, tab3 = st.tabs(["📋 Resumen Ejecutivo", "🔧 Recomendaciones", "📥 Exportar Datos"])

    with tab1:
        st.markdown("### Resumen Ejecutivo del Análisis")
        
        col9, col10 = st.columns(2)
        
        with col9:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1.5rem; border-radius: 10px;'>
            <h4 style='color: #1976d2; margin-top: 0;'>📈 Métricas de Tráfico</h4>
            <ul style='color: #37474f;'>
                <li><strong>Período analizado:</strong> {df_processed['fecha'].min().strftime('%d/%m/%Y')} - {df_processed['fecha'].max().strftime('%d/%m/%Y')}</li>
                <li><strong>Usuarios únicos:</strong> {metricas['Usuarios únicos']:,}</li>
                <li><strong>Total de requests:</strong> {metricas['Total de requests']:,}</li>
                <li><strong>Tráfico móvil:</strong> {metricas['% Móvil']:.1f}%</li>
                <li><strong>Hora pico:</strong> {trafico_por_hora.loc[trafico_por_hora['count'].idxmax(), 'hora']}:00 hs</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col10:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 1.5rem; border-radius: 10px;'>
            <h4 style='color: #f57c00; margin-top: 0;'>🛡️ Seguridad y Riesgos</h4>
            <ul style='color: #37474f;'>
                <li><strong>Anomalías detectadas:</strong> {metricas['% Anomalías']:.2f}%</li>
                <li><strong>IPs sospechosas:</strong> {metricas['IPs sospechosas']}</li>
                <li><strong>Navegador principal:</strong> {metricas['Navegador principal']}</li>
                <li><strong>Origen predominante:</strong> {metricas['País predominante']}</li>
                <li><strong>Nivel de riesgo:</strong> {'BAJO' if metricas['% Anomalías'] < 3 else 'MEDIO' if metricas['% Anomalías'] < 8 else 'ALTO'}</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🔧 Recomendaciones Estratégicas")
        
        recommendations = [
            {
                "icon": "🚀",
                "title": "Optimización de Horario Pico",
                "description": f"Escalar recursos entre {trafico_por_hora.loc[trafico_por_hora['count'].idxmax(), 'hora']-1}:00 y {trafico_por_hora.loc[trafico_por_hora['count'].idxmax(), 'hora']+1}:00 horas",
                "priority": "Alta"
            },
            {
                "icon": "🛡️",
                "title": "Mitigación de Bots",
                "description": f"Implementar WAF para {metricas['IPs sospechosas']} IPs sospechosas identificadas",
                "priority": "Alta"
            },
            {
                "icon": "📱",
                "title": "Experiencia Mobile",
                "description": f"Optimizar para {metricas['% Móvil']:.1f}% de usuarios móviles",
                "priority": "Media"
            },
            {
                "icon": "🌍",
                "title": "Contenido Regional",
                "description": f"Adaptar contenido para usuarios de {metricas['País predominante']}",
                "priority": "Media"
            }
        ]
        
        for rec in recommendations:
            with st.container():
                col11, col12 = st.columns([1, 10])
                with col11:
                    st.markdown(f"<div style='font-size: 2rem;'>{rec['icon']}</div>", unsafe_allow_html=True)
                with col12:
                    st.markdown(f"""
                    <div style='padding: 1rem; background: {"#ffebee" if rec['priority'] == 'Alta' else "#fff8e1" if rec['priority'] == 'Media' else "#e8f5e8"}; border-radius: 8px; margin-bottom: 1rem;'>
                        <h4 style='margin: 0; color: #2c3e50;'>{rec['title']}</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #546e7a;'>{rec['description']}</p>
                        <span style='background: {"#e53935" if rec['priority'] == 'Alta' else "#ffb300" if rec['priority'] == 'Media' else "#43a047"}; color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem;'>Prioridad: {rec['priority']}</span>
                    </div>
                    """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📥 Exportar Resultados del Análisis")
        
        col13, col14, col15 = st.columns(3)
        
        with col13:
            st.download_button(
                label="💾 Datos Completos (CSV)",
                data=df_processed.to_csv(index=False).encode('utf-8'),
                file_name=f"dgipse_trafico_completo_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col14:
            st.download_button(
                label="🚨 IPs Sospechosas",
                data=features[features['es_anomalia'] == 1].to_csv().encode('utf-8'),
                file_name=f"dgipse_ips_sospechosas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col15:
            st.download_button(
                label="📊 Reporte Ejecutivo",
                data=generate_executive_report(metricas, features, df_processed),
                file_name=f"dgipse_reporte_ejecutivo_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Vista previa de datos
        with st.expander("👁️ Vista Previa de Datos Procesados"):
            st.dataframe(
                df_processed[['fecha', 'IP', 'url', 'navegador', 'dispositivo', 'pais']].head(10),
                use_container_width=True
            )

else:
    # Pantalla de bienvenida cuando no hay archivo cargado
    st.markdown("---")
    col_welcome1, col_welcome2 = st.columns([2, 1])
    
    with col_welcome1:
        st.markdown("""
        ## 🎯 Bienvenido al Dashboard de Análisis de Tráfico DGIPSE
        
        ### 📋 ¿Qué puedes hacer con esta herramienta?
        
        - **📊 Visualización interactiva** del tráfico web en tiempo real
        - **🚨 Detección automática** de anomalías y comportamientos sospechosos  
        - **👥 Segmentación inteligente** de usuarios por patrones de comportamiento
        - **🌍 Análisis geográfico** del origen del tráfico
        - **📈 Optimización** de recursos basada en patrones de uso
        
        ### 🚀 Comenzar es muy fácil:
        1. **Prepará** tu archivo `datos.json` con los logs de acceso
        2. **Subí** el archivo usando el selector arriba
        3. **Explorá** las visualizaciones interactivas
        4. **Descargá** los reportes y datos procesados
        """)
    
    with col_welcome2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white;'>
        <h3 style='color: white; margin-top: 0;'>📁 Estructura del Archivo</h3>
        <p>Tu archivo JSON debe contener:</p>
        <ul style='color: white;'>
            <li><strong>fecha:</strong> Timestamp</li>
            <li><strong>IP:</strong> Dirección IP</li>
            <li><strong>url:</strong> Página visitada</li>
            <li><strong>user_agent:</strong> Navegador/Dispositivo</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Ejemplo de estructura de datos
    with st.expander("📝 Ver ejemplo de estructura de datos JSON", expanded=True):
        st.json({
            "datos": [
                {
                    "fecha": "25-02-2024 10:30:45AM",
                    "IP": "200.81.123.45", 
                    "url": "/pagina-principal",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                {
                    "fecha": "25-02-2024 10:31:22AM",
                    "IP": "190.123.456.78",
                    "url": "/contacto", 
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
                }
            ]
        })

def generate_executive_report(metricas, features, df_processed):
    """Genera un reporte ejecutivo en texto plano"""
    report = f"""
    REPORTE EJECUTIVO - ANÁLISIS DE TRÁFICO DGIPSE
    Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    ===================================================
    
    RESUMEN EJECUTIVO:
    - Total de requests analizados: {metricas['Total de requests']:,}
    - Usuarios únicos identificados: {metricas['Usuarios únicos']:,}
    - Tráfico móvil: {metricas['% Móvil']:.1f}%
    - Tasa de anomalías: {metricas['% Anomalías']:.2f}%
    
    PRINCIPALES HALLAZGOS:
    1. Seguridad: {metricas['IPs sospechosas']} IPs marcadas como sospechosas
    2. Dispositivos: {metricas['% Móvil']:.1f}% del tráfico desde móviles
    3. Geografía: Tráfico predominante desde {metricas['País predominante']}
    4. Navegadores: {metricas['Navegador principal']} es el más utilizado
    
    RECOMENDACIONES PRIORITARIAS:
    1. Implementar medidas de seguridad para IPs sospechosas
    2. Optimizar experiencia mobile
    3. Monitoreo continuo de patrones anómalos
    4. Escalado de recursos en horarios pico
    
    ---
    Generado automáticamente por el Dashboard de Análisis DGIPSE
    """
    return report.encode('utf-8')