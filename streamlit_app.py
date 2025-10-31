# ==========================================================
# DASHBOARD DE ANÁLISIS DE TRÁFICO WEB - DGIPSE
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
    page_icon="📊"
)

# Configuración de estilos
plt.style.use('default')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .anomaly-metric {
        background-color: #fff5f5;
        border-left: 4px solid #ff6b6b;
    }
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER PRINCIPAL
# ==========================================================
st.markdown('<p class="main-header">📊 Análisis y Monitoreo del Tráfico Web - DGIPSE</p>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    Este dashboard analiza el tráfico web del sitio <strong>dgipse.gob.ar</strong> para identificar 
    patrones de acceso, detectar anomalías y optimizar el rendimiento.
</div>
""", unsafe_allow_html=True)

# ==========================================================
# CARGA DE DATOS
# ==========================================================
with st.container():
    st.markdown("### 📁 Carga de Datos")
    uploaded_file = st.file_uploader("Subí el archivo `datos.json`", type=["json"], help="Archivo JSON con los logs de acceso web")

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
        return 'Other'

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
        return 'Other'

    def extract_device(user_agent):
        mobile_indicators = ['Mobile', 'Android', 'iPhone', 'iPad']
        if any(indicator in user_agent for indicator in mobile_indicators):
            return 'Mobile'
        return 'Desktop'

    def geolocate_ip(ip):
        ip_ranges = {
            '200.81': 'Argentina',
            '190.': 'Chile',
            '181.': 'Chile', 
            '200.1': 'Brasil',
            '186.': 'Colombia',
            '200.32': 'Uruguay'
        }
        for prefix, country in ip_ranges.items():
            if ip.startswith(prefix):
                return country
        return 'Otros'

    def preprocess_data(df):
        df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%Y %I:%M:%S%p', errors='coerce')
        df['navegador'] = df['user_agent'].apply(extract_browser)
        df['sistema_operativo'] = df['user_agent'].apply(extract_os)
        df['dispositivo'] = df['user_agent'].apply(extract_device)
        static_extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.ttf']
        df['es_estatico'] = df['url'].str.contains('|'.join(static_extensions), case=False, na=False)
        df['pais'] = df['IP'].apply(geolocate_ip)
        return df

    # ==========================================================
    # PREPROCESAMIENTO
    # ==========================================================
    with st.spinner('Procesando datos...'):
        df_processed = preprocess_data(df.copy())
        df_processed['hora'] = df_processed['fecha'].dt.hour
        df_processed['dia_semana'] = df_processed['fecha'].dt.day_name()

    st.success("✅ Datos cargados y preprocesados correctamente")

    # ==========================================================
    # MÉTRICAS CLAVE
    # ==========================================================
    features = df_processed.groupby('IP').agg({
        'fecha': 'count',
        'url': 'nunique',
        'hora': 'nunique'
    }).rename(columns={'fecha': 'total_requests', 'url': 'unique_pages', 'hora': 'unique_hours'})

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    iso_forest = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    anomalies = iso_forest.fit_predict(features_scaled)
    features['es_anomalia'] = np.where(anomalies == -1, 1, 0)

    metricas = {
        'Usuarios únicos': df_processed['IP'].nunique(),
        'Total de requests': len(df_processed),
        '% Mobile': (df_processed['dispositivo'] == 'Mobile').mean() * 100,
        'Navegador principal': df_processed['navegador'].mode()[0] if len(df_processed['navegador'].mode()) > 0 else 'N/A',
        'País predominante': df_processed['pais'].mode()[0] if len(df_processed['pais'].mode()) > 0 else 'N/A',
        '% Anomalías': features['es_anomalia'].mean() * 100
    }

    # Mostrar métricas con mejor diseño
    st.markdown("### 📈 Métricas Clave del Tráfico")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("👥 Usuarios Únicos", f"{metricas['Usuarios únicos']:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📨 Total Requests", f"{metricas['Total de requests']:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📱 % Mobile", f"{metricas['% Mobile']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card anomaly-metric">', unsafe_allow_html=True)
        st.metric("🚨 % Anomalías", f"{metricas['% Anomalías']:.2f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🌐 Navegador Principal", metricas['Navegador principal'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📍 País Predominante", metricas['País predominante'])
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # VISUALIZACIONES MEJORADAS
    # ==========================================================
    st.markdown("---")
    st.markdown("### 📊 Visualizaciones del Tráfico")

    # Primera fila de gráficos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # Tráfico por hora - Mejorado
        trafico_por_hora = df_processed.groupby('hora').size()
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Crear gradiente de colores
        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(trafico_por_hora)))
        
        bars = ax.bar(trafico_por_hora.index, trafico_por_hora.values, color=colors, alpha=0.8, edgecolor='darkblue', linewidth=0.5)
        
        # Mejorar el diseño
        ax.set_title('📈 Tráfico por Hora del Día', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Hora del Día', fontweight='bold')
        ax.set_ylabel('Número de Requests', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Añadir valor en cada barra
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(trafico_por_hora.values)*0.01,
                   f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # Distribución geográfica mejorada
        pais_distribution = df_processed['pais'].value_counts()
        
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        
        # Paleta de colores atractiva
        colors = plt.cm.Set3(np.linspace(0, 1, len(pais_distribution)))
        
        wedges, texts, autotexts = ax2.pie(pais_distribution.values, 
                                          labels=pais_distribution.index,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90,
                                          textprops={'fontsize': 10})
        
        # Mejorar los textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax2.set_title('🌍 Distribución Geográfica', fontsize=12, fontweight='bold', pad=20)
        plt.tight_layout()
        st.pyplot(fig2)
        st.markdown('</div>', unsafe_allow_html=True)

    # Segunda fila de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # Dispositivos
        dispositivo_data = df_processed['dispositivo'].value_counts()
        
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        colors = ['#ff9999', '#66b3ff']
        bars = ax3.bar(dispositivo_data.index, dispositivo_data.values, color=colors, alpha=0.8)
        
        ax3.set_title('📱 Distribución por Dispositivo', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Cantidad de Requests', fontweight='bold')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(dispositivo_data.values)*0.01,
                    f'{int(height):,}', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig3)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # Navegadores
        navegador_data = df_processed['navegador'].value_counts()
        
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Pastel1(range(len(navegador_data)))
        bars = ax4.bar(navegador_data.index, navegador_data.values, color=colors, alpha=0.8)
        
        ax4.set_title('🌐 Distribución por Navegador', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Cantidad de Requests', fontweight='bold')
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + max(navegador_data.values)*0.01,
                    f'{int(height):,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig4)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tercera fila - Páginas más visitadas
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    paginas_populares = df_processed[~df_processed['es_estatico']]['url'].value_counts().head(10)
    
    fig5, ax5 = plt.subplots(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(paginas_populares)))
    
    bars = ax5.barh(range(len(paginas_populares)), paginas_populares.values, color=colors, alpha=0.8)
    ax5.set_yticks(range(len(paginas_populares)))
    
    # Acortar URLs largas para mejor visualización
    shortened_labels = [label[:50] + '...' if len(label) > 50 else label for label in paginas_populares.index]
    ax5.set_yticklabels(shortened_labels, fontsize=10)
    
    ax5.set_title('🔥 Top 10 Páginas Más Visitadas', fontsize=14, fontweight='bold', pad=20)
    ax5.set_xlabel('Número de Visitas', fontweight='bold')
    
    # Añadir valores en las barras
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax5.text(width + max(paginas_populares.values)*0.01, bar.get_y() + bar.get_height()/2.,
                f'{int(width):,}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig5)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # DETECCIÓN DE ANOMALÍAS Y CLUSTERING
    # ==========================================================
    st.markdown("---")
    st.markdown("### 🧠 Análisis Avanzado - Detección de Anomalías")

    col7, col8 = st.columns(2)
    
    with col7:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # Detección de anomalías
        fig6, ax6 = plt.subplots(figsize=(10, 8))
        
        # Separar puntos normales y anomalías
        normal_points = features[features['es_anomalia'] == 0]
        anomaly_points = features[features['es_anomalia'] == 1]
        
        ax6.scatter(normal_points['total_requests'], normal_points['unique_pages'],
                   c='green', alpha=0.6, s=50, label='Normal', edgecolors='black', linewidth=0.5)
        ax6.scatter(anomaly_points['total_requests'], anomaly_points['unique_pages'],
                   c='red', alpha=0.8, s=80, label='Anomalía', edgecolors='darkred', linewidth=0.8, marker='X')
        
        ax6.set_title('🚨 Detección de Anomalías / Bots', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Total de Requests por IP', fontweight='bold')
        ax6.set_ylabel('Páginas Únicas Visitadas', fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig6)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col8:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        # K-Means Clustering
        cluster_features = features[['total_requests', 'unique_pages', 'unique_hours']].dropna()
        cluster_scaled = scaler.fit_transform(cluster_features)
        kmeans = KMeans(n_clusters=3, random_state=42)
        cluster_features['cluster'] = kmeans.fit_predict(cluster_scaled)
        
        fig7, ax7 = plt.subplots(figsize=(10, 8))
        
        scatter = ax7.scatter(cluster_features['total_requests'], cluster_features['unique_pages'],
                             c=cluster_features['cluster'], cmap='tab10', alpha=0.7, s=60, edgecolors='black', linewidth=0.5)
        
        ax7.set_title('👥 Segmentación de Usuarios por Comportamiento', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Total de Requests por IP', fontweight='bold')
        ax7.set_ylabel('Páginas Únicas Visitadas', fontweight='bold')
        plt.colorbar(scatter, ax=ax7, label='Cluster')
        ax7.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig7)
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # INSIGHTS Y DESCARGAS
    # ==========================================================
    st.markdown("---")
    
    col9, col10 = st.columns(2)
    
    with col9:
        st.markdown("### 💡 Insights Principales")
        st.markdown("""
        <div style='background-color: #e8f4fd; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1f77b4;'>
        <ul style='margin: 0; padding-left: 1.2rem;'>
            <li><strong>Horas pico:</strong> Identificar horas con mayor tráfico para optimización</li>
            <li><strong>Origen geográfico:</strong> Principalmente {}</li>
            <li><strong>Bots/Anomalías:</strong> {}% del tráfico total requiere atención</li>
            <li><strong>Dispositivos:</strong> {}% del tráfico proviene de móviles</li>
            <li><strong>Navegador predominante:</strong> {}</li>
        </ul>
        </div>
        """.format(metricas['País predominante'], f"{metricas['% Anomalías']:.1f}", f"{metricas['% Mobile']:.1f}", metricas['Navegador principal']), 
        unsafe_allow_html=True)
    
    with col10:
        st.markdown("### 🔧 Recomendaciones")
        st.markdown("""
        <div style='background-color: #fff0f0; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #ff6b6b;'>
        <ol style='margin: 0; padding-left: 1.2rem;'>
            <li>Optimizar servidores para horas pico identificadas</li>
            <li>Implementar WAF para bloquear bots maliciosos</li>
            <li>Mejorar experiencia mobile ({}% del tráfico)</li>
            <li>Regionalizar contenido para {}</li>
            <li>Monitoreo continuo de IPs sospechosas</li>
        </ol>
        </div>
        """.format(f"{metricas['% Mobile']:.1f}", metricas['País predominante']), 
        unsafe_allow_html=True)

    # ==========================================================
    # DESCARGAS
    # ==========================================================
    st.markdown("---")
    st.markdown("### 📥 Exportar Resultados")
    
    col11, col12 = st.columns(2)
    
    with col11:
        st.download_button(
            label="⬇️ Descargar Datos Procesados (CSV)",
            data=df_processed.to_csv(index=False).encode('utf-8'),
            file_name="accesos_procesados.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col12:
        st.download_button(
            label="⬇️ Descargar IPs Sospechosas",
            data=features[features['es_anomalia']==1].to_csv().encode('utf-8'),
            file_name="ips_sospechosas.csv",
            mime="text/csv",
            use_container_width=True
        )

    # ==========================================================
    # RESUMEN EJECUTIVO
    # ==========================================================
    with st.expander("📋 Resumen Ejecutivo", expanded=False):
        st.markdown(f"""
        ### Resumen de Análisis - {datetime.now().strftime('%d/%m/%Y')}
        
        **📊 Métricas Generales:**
        - **Usuarios únicos analizados:** {metricas['Usuarios únicos']:,}
        - **Total de requests procesados:** {metricas['Total de requests']:,}
        - **Tráfico móvil:** {metricas['% Mobile']:.1f}%
        - **Anomalías detectadas:** {metricas['% Anomalías']:.2f}%
        
        **🎯 Perfil de Tráfico:**
        - **Navegador principal:** {metricas['Navegador principal']}
        - **Origen predominante:** {metricas['País predominante']}
        - **Horario de mayor actividad:** {trafico_por_hora.idxmax()}:00 hs
        
        **🛡️ Seguridad:**
        - **IPs sospechosas identificadas:** {len(features[features['es_anomalia']==1])}
        - **Recomendación prioritaria:** Implementar sistema de mitigación de bots
        """)

else:
    st.info("👆 Subí tu archivo `datos.json` para comenzar el análisis.")
    
    # Mostrar ejemplo de estructura de datos
    with st.expander("📝 Ver estructura de datos esperada"):
        st.markdown("""
        ### Estructura esperada del archivo JSON:
        ```json
        [
            {
                "fecha": "25-02-2024 10:30:45AM",
                "IP": "200.81.123.45",
                "url": "/pagina-ejemplo",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            {
                "fecha": "25-02-2024 10:31:22AM", 
                "IP": "190.123.456.78",
                "url": "/otra-pagina",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
            }
        ]
        ```
        """)