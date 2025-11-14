## **Dashboard de Análisis de Tráfico Web - DGIPSE**
#### **Descripción**
Este proyecto es una aplicación web desarrollada con Streamlit para el **análisis inteligente del tráfico web** del portal institucional del gobierno provincial de Santiago del Estero. Esta herramienta permite monitorear, analizar y visualizar patrones de tráfico web con capacidades avanzadas de machine learning para detección de anomalías y segmentación de usuarios.

### **Características Principales**

#### **Visualizaciones Avanzadas e Interactivas**
• Análisis temporal
• Distribución geográfica
• Segmentación por dispositivos
• Análisis de navegadores
• Elaboración de informes

#### **Integración de Machine Learnning**
• Detencción de anomalías
• Segmentación de usuarios
• Detección de bots

#### **Métricas en Tiempo Real**
• Usuarios únicos y total de requests
• Porcentaje de tráfico movil
• Tasa de anomalías detectadas
• IP's sospechosas identificadas

#### **Detección Inteligente**
• Soporte para JSONs estructurados
• Compatibilidad con logs de Apache/NGINX
• Archivos CSV, TXT, LOG
• Parseo automático de formatos comunes 

#### Tecnologías Utilizadas
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.8+ | Lenguaje principal |
| Streamlit | 1.28+ | Framework web interactivo |
| Pandas | 2.0+ | Procesamiento de datos |
| Plotly | 5.15+ | Visualizaciones interactivas |
| Scikit-learn | 1.3+ | Machine Learning |
| NumPy | 1.24+ | Cálculos numéricos |


## **Uso del Dashboard**

1. **Carga de datos**: 
  • Seleccionar el tipo de archivo que se desea analizar (JSON o Logs)
  • Subir el archivo de datos
  • Configurar el formato específico si es necesario
  
2. **Formatos Soportados**:
  • JSON:
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
  • Logs Apache/NGINX
  • CSV
  
3. **Análisis Disponibles**:
• Usuarios únicos identificados
• Total de requests procesados
• Porcentaje de tráfico móvil
• Anomalías detectadas
• Tráfico por hora: Patrones horarios de acceso
• Distribución geográfica: Origen del tráfico por países
• Dispositivos y navegadores: Tecnologías utilizadas
• Páginas más visitadas: Top 10 de contenido popular
• Detección de anomalías: Comportamientos sospechosos
• Segmentación de usuarios: Grupos por patrones de comportamiento
• Análisis temporal: Patrones por día y hora

#### Configuraciones
• Ajuste de sensibilidad de anomalías
• Número de clusters

Procesamiento: Python 3.8+
