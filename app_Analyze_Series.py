import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def crear_grafico(df):
    
    df_total = df.copy()
    
    # Suponemos que la primera columna es la fecha
    fecha_columna = df_total.columns[0]
    
    # Selección dinámica de columnas (excluyendo la columna de fecha)
    columnas_disponibles = df_total.columns[1:].tolist()
    columnas_seleccionadas = st.multiselect("Selecciona las columnas a graficar", 
                                            columnas_disponibles, 
                                            default=columnas_disponibles[:min(3, len(columnas_disponibles))])
    if not columnas_seleccionadas:
        st.warning("Selecciona al menos una columna para graficar.")
        return None

    fig = go.Figure()
    for col in columnas_seleccionadas:
        fig.add_trace(go.Scatter(
            x=df_total[fecha_columna],
            y=df_total[col],
            mode='lines',
            name=col
        ))

    fig.update_layout(
        title='Series Temporales',
        xaxis_title='Fecha y Hora',
        yaxis_title='Valor',
        legend=dict(
            orientation="v",
            x=1.02,
            y=1.02,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=150, t=50, b=50)
    )
    
    st.plotly_chart(fig)


st.title("Visualización de Series Temporales")

archivo = st.file_uploader("Sube un archivo (.parquet o .txt)", type=["txt", "parquet"])

if archivo is not None:
    file_name = archivo.name.lower()
    
    if file_name.endswith('.txt'):
        # Lectura del archivo TXT
        try:
            df = pd.read_csv(archivo, delimiter=';', encoding='UTF-8-SIG', encoding_errors='ignore')
        except Exception as e:
            st.error(f"Error al leer el archivo TXT: {e}")
            st.stop()
            
        # Convertir la columna "Fecha/hora" a datetime y reordenar columnas
        if "Fecha/hora" in df.columns:
            try:
                df['Fecha/hora'] = df['Fecha/hora'].astype(str)
                df['Fecha/hora'] = pd.to_datetime(
                    df['Fecha/hora'],
                    format='%d/%m/%y %H:%M:%S',
                    errors='coerce'
                )
                
            except Exception as e:
                st.error(f"Error al convertir 'Fecha/hora' a datetime: {e}")
                st.stop()
            # Reordenar para que "Fecha/hora" sea la primera columna
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index("Fecha/hora")))
            df = df[cols]
        else:
            st.error("La columna 'Fecha/hora' no se encontró en el archivo TXT.")
            st.stop()
            
    elif file_name.endswith('.parquet'):
        # Lectura del archivo Parquet
        try:
            df = pd.read_parquet(archivo)
        except Exception as e:
            st.error(f"Error al leer el archivo Parquet: {e}")
            st.stop()
            
        # Verificar que la columna "Hora [UTC]" exista y reordenarla
        if "Hora [UTC]" in df.columns:
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index("Hora [UTC]")))
            df = df[cols]
        else:
            st.error("La columna 'Hora [UTC]' no se encontró en el archivo Parquet.")
            st.stop()
    else:
        st.error("Tipo de archivo no soportado.")
        st.stop()

    # Mostrar el contenido de la tabla
    st.subheader("Contenido de la Tabla")
    st.dataframe(df)

    # Mostrar el gráfico interactivo
    st.subheader("Gráfico Interactivo")
    crear_grafico(df)
