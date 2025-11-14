# 📊 Dashboard de Análisis de Tráfico Web - DGIPSE

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-FF6B35?style=for-the-badge&logo=scikitlearn&logoColor=white)

*Una solución inteligente para el análisis de tráfico web institucional*

## 👥 **Equipo de Desarrollo**

| Integrante | Rol |
|------------|-----|
| **Gabriela Argañaráz** | Visualización de Datos |
| **Nelson Ramiro Castillo** | Testing y Documentación |
| **Mariam Rocio Marcos** | Desarrollo y Análisis |
| **Mara Jorgelina Santillán** | Desarrollo y Machine Learning |
| **Ivana Rocio Velázquez** | Desarrollo y Procesamiento de Datos |

---

## 📋 **Descripción del Proyecto**

Este proyecto es una aplicación web desarrollada con **Streamlit** para el **análisis inteligente del tráfico web** del portal institucional del gobierno provincial de Santiago del Estero. 

La herramienta permite **monitorear, analizar y visualizar** patrones de tráfico web con capacidades avanzadas de **machine learning** para detección de anomalías y segmentación de usuarios.

---

## ✨ **Características Principales**

### 📈 **Visualizaciones Avanzadas e Interactivas**
- 🕒 **Análisis temporal** - Patrones horarios y estacionales
- 🌍 **Distribución geográfica** - Origen del tráfico por países
- 📱 **Segmentación por dispositivos** - Desktop vs Móvil
- 🌐 **Análisis de navegadores** - Tecnologías utilizadas
- 📊 **Elaboración de informes** - Reportes ejecutivos automáticos

### 🤖 **Integración de Machine Learning**
- 🚨 **Detección de anomalías** - Comportamientos sospechosos
- 👥 **Segmentación de usuarios** - Clustering por patrones
- 🤖 **Detección de bots** - Tráfico automatizado

### 📊 **Métricas en Tiempo Real**
- 👤 Usuarios únicos y total de requests
- 📱 Porcentaje de tráfico móvil
- ⚠️ Tasa de anomalías detectadas
- 🕵️ IP's sospechosas identificadas

### 🔧 **Detección Inteligente**
- 📄 Soporte para **JSON** estructurados
- 📝 Compatibilidad con **logs de Apache/NGINX**
- 📋 Archivos **CSV, TXT, LOG**
- 🔄 Parseo automático de formatos comunes

---

## 🛠 **Tecnologías Utilizadas**

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.8+ | Lenguaje principal |
| Streamlit | 1.28+ | Framework web interactivo |
| Pandas | 2.0+ | Procesamiento de datos |
| Plotly | 5.15+ | Visualizaciones interactivas |
| Scikit-learn | 1.3+ | Machine Learning |
| NumPy | 1.24+ | Cálculos numéricos |

---

## 🚀 **Uso del Dashboard**

### 1. **Carga de Datos**
- **Seleccionar** el tipo de archivo (JSON o Logs)
- **Subir** el archivo de datos
- **Configurar** el formato específico si es necesario

### 2. **Formatos Soportados**

#### 📄 **JSON**
```json
[
  {
    "fecha": "25-02-2024 10:30:45AM",
    "IP": "200.81.123.45",
    "url": "/pagina-principal",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
]
```

#### 📝 **Logs Apache/NGINX**
```apache
192.168.1.100 - - [15/Oct/2023:10:23:45 -0500] "GET /index.html HTTP/1.1" 200 1234 "https://www.google.com" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

#### 📊 **CSV**
```csv
fecha,IP,url,user_agent
25-02-2024 10:30:45AM,200.81.123.45,/pagina-principal,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### 3. **Análisis Disponibles**

#### 📈 **Métricas Principales**
- 👤 Usuarios únicos identificados
- 📨 Total de requests procesados
- 📱 Porcentaje de tráfico móvil
- ⚠️ Anomalías detectadas

#### 📊 **Visualizaciones**
- 🕒 **Tráfico por hora** - Patrones horarios de acceso
- 🌍 **Distribución geográfica** - Origen del tráfico por países
- 💻 **Dispositivos y navegadores** - Tecnologías utilizadas
- 🔥 **Páginas más visitadas** - Top 10 de contenido popular

#### 🧠 **Análisis Avanzado**
- 🚨 **Detección de anomalías** - Comportamientos sospechosos
- 👥 **Segmentación de usuarios** - Grupos por patrones de comportamiento
- 📅 **Análisis temporal** - Patrones por día y hora

### 4. **Elaboración de Informes**

#### 📋 **Informe de Resultados (CSV)**
```csv
IP,http,host,url,dia,fecha,previo,user_agent,navegador,sistema_operativo,dispositivo,es_estatico,pais,hora,dia_semana,mes
```

#### 🕵️ **IP's Sospechosas (CSV)**
```csv
IP,total_requests,unique_pages,unique_hours,es_anomalia
```

#### 📄 **Reportes Ejecutivos**
```
REPORTE EJECUTIVO - ANÁLISIS DE TRÁFICO DGIPSE
Fecha de generación: 14/11/2025 11:30
===================================================

RESUMEN EJECUTIVO:
- Total de requests analizados: 3,398
- Usuarios únicos identificados: 626
- Tráfico móvil: 19.8%
- Tasa de anomalías: 5.11%

PRINCIPALES HALLAZGOS:
1. Seguridad: 32 IPs marcadas como sospechosas
2. Dispositivos: 19.8% del tráfico desde móviles
3. Geografía: Tráfico predominante desde Chile
4. Navegadores: Otros es el más utilizado

RECOMENDACIONES PRIORITARIAS:
1. Implementar medidas de seguridad para IPs sospechosas
2. Optimizar experiencia mobile
3. Monitoreo continuo de patrones anómalos
4. Escalado de recursos en horarios pico

---
Generado automáticamente por el Dashboard de Análisis DGIPSE
```

### ⚙️ **Configuraciones**
- 🎚️ **Umbral de sensibilidad** de anomalías
- 🔢 **Número de clusters** para segmentación

---

## 🐛 **Solución de Problemas**

### ❌ **Error: "Missing required columns"**
**Causa**: Falta alguna columna requerida  
**Solución**: Asegurar que el archivo tenga: `fecha`, `IP`, `url`, `user_agent`

### ⚠️ **Error: "attempt to get argmax of an empty sequence"**
**Causa**: Formato de fecha incorrecto en los logs  
**Solución**: Verificar que el formato de fecha coincida con el esperado. Usar el selector correcto de formato de log

### 🐢 **Rendimiento lento con archivos grandes**
**Solución**: Dividir archivos muy grandes en lotes. Usar muestreo para análisis exploratorio

---

## 🙏 **Agradecimientos**

| Persona/Organización | Contribución |
|---------------------|--------------|
| **Fernando Elías Mubarqui** | Data Scientist y Profesor |
| **Equipo de DGIPSE** | Dirección General de Informática y Procesamiento de Santiago del Estero |
| **Comunidad de Streamlit** | Excelente framework para aplicaciones web |
| **Plotly** | Visualizaciones interactivas de alta calidad |

---


**🔧 Procesamiento: Python 3.8+**

---
*Desarrollado con ❤️ para el Gobierno de Santiago del Estero*

</div>
