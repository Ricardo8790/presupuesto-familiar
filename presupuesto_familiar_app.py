# archivo: presupuesto_familiar_app.py
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import altair as alt
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la página (debe estar al inicio)
st.set_page_config(page_title="Presupuesto Familiar", layout="wide")

# ======= Configuración de la base de datos =======
DATABASE_URL = os.getenv("https://jcbmizozujcmxembdcmw.supabase.co")

# Si estás en Streamlit Cloud, intentar usar secrets
if DATABASE_URL is None:
    try:
        DATABASE_URL = st.secrets["https://jcbmizozujcmxembdcmw.supabase.co"]
    except:
        pass

# Crear conexión a la base de datos
engine = None
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        # Probar conexión
        with engine.connect() as conn:
            st.sidebar.success("🟢 Conectado a PostgreSQL")
    except Exception as e:
        st.sidebar.error(f"❌ Error de conexión: {str(e)}")
        engine = None
else:
    st.sidebar.warning("⚠️ Base de datos no configurada")

# ======= Archivos de almacenamiento =======
# Configuración de la base de datos
try:
    DATABASE_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
    
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        # Probar conexión
        with engine.connect() as conn:
            st.sidebar.success("🟢 Conectado a PostgreSQL")
    else:
        st.error("⚠️ Configuración de base de datos no encontrada")
        engine = None
except Exception as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    engine = None


# Configuración de la página
st.set_page_config(page_title="Presupuesto Familiar", layout="wide")

# ======= Archivos de almacenamiento =======
DATA_FILE = "presupuesto_familiar.json"
BUDGET_FILE = "presupuesto_mensual.json"

# ======= Funciones de carga y guardado =======
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"ingresos": [], "gastos": []}

def guardar_datos(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def cargar_presupuesto():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def guardar_presupuesto(presupuesto):
    with open(BUDGET_FILE, "w") as f:
        json.dump(presupuesto, f, indent=4)

def limpiar_todos_los_registros():
    """Reinicia todos los registros de ingresos, gastos y presupuestos"""
    data = {"ingresos": [], "gastos": []}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    presupuesto = {}
    with open(BUDGET_FILE, "w") as f:
        json.dump(presupuesto, f, indent=4)

    return data, presupuesto

# ======= Datos iniciales =======
data = cargar_datos()
presupuesto = cargar_presupuesto()

categorias = {
    "Alimentación": ["Supermercado", "Restaurantes", "Comida rápida", "Botellón Agua", "Tienda Barrio"],
    "Vivienda": ["Hipoteca/Alquiler", "Servicios básicos", "Mantenimiento"],
    "Transporte": ["Combustible", "Transporte público", "Mantenimiento vehículo", "Seguro Vehicular", "Matricula vehículo"],
    "Salud": ["Medicinas", "Consultas médicas", "Seguros", "Peluquería/Estetica"],
    "Educación": ["Colegiaturas", "Libros", "Cursos y talleres"],
    "Entretenimiento": ["Cine", "Eventos", "Suscripciones", "Paseos Fin de Semana"],
    "Ropa y Calzado": ["Ropa", "Calzado", "Accesorios"],
    "Mascota y plantas": ["Alimentación", "Salud", "Accesorios", "Mantenimiento"],
    "Ahorro e Inversiones": ["Ahorro", "Inversiones", "Fondo emergencias"],
    "Otros": ["Varios", "Donaciones", "Regalos", "Padres"]
}

# ======= Estilo ejecutivo con fondo =======
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1554224154-22dec7ec8818?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80');
    background-size: cover;
    background-attachment: fixed;
    font-family: 'Arial', sans-serif;
}
h1 {color: #003366;}
h2 {color: #004080;}
h3 {color: #0059b3;}
.stButton>button {background-color:#004080; color:white; font-weight:bold;}
.stMetric-value {font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("💼 Dashboard Ejecutivo de Presupuesto Familiar")

# ======= Menu lateral =======
menu = st.sidebar.selectbox("Menú Principal", ["Presupuesto Mensual", "Agregar Ingreso", "Añadir Gasto", "Balance", "Reporte Detallado", "Editar Registro", "Eliminar Registro"])

# ================== PESTAÑA 1: PRESUPUESTO MENSUAL ==================
if menu == "Presupuesto Mensual":
    st.header("📊 Presupuesto Mensual")
    mes = st.selectbox("Seleccione mes y año", pd.date_range("2025-01-01", periods=12, freq="MS").strftime("%Y-%m"), key="pm_mes")

    # Inicializar presupuesto para el mes si no existe
    if mes not in presupuesto:
        presupuesto[mes] = {}
    
    # Asegurar que todas las categorías existen
    for cat in categorias.keys():
        if cat not in presupuesto[mes]:
            presupuesto[mes][cat] = 0.0

    col_left, col_right = st.columns([1,2])

    with col_left:
        st.subheader(f"Definir presupuesto para {mes}")
        for cat in categorias.keys():
            presupuesto[mes][cat] = st.number_input(
                f"{cat}", 
                value=float(presupuesto[mes][cat]), 
                min_value=0.0, 
                format="%.2f", 
                key=f"pm_{cat}"
            )
        
        if st.button("Guardar presupuesto", key="guardar_presupuesto"):
            guardar_presupuesto(presupuesto)
            st.success(f"Presupuesto guardado para {mes}")
            st.rerun()

    with col_right:
        st.subheader("Detalle Presupuesto y Gráfico")
        pres_df = pd.DataFrame(list(presupuesto[mes].items()), columns=["Categoría", "Presupuesto"])
        st.dataframe(pres_df.style.format({"Presupuesto": "${:,.2f}"}))
        pres_df["Presupuesto"] = pres_df["Presupuesto"].astype(float)
        color_scale = alt.Scale(domain=pres_df["Categoría"], scheme='category10')
        chart = alt.Chart(pres_df).mark_bar().encode(
            x=alt.X('Categoría', sort=None),
            y='Presupuesto',
            color=alt.Color('Categoría', scale=color_scale, legend=None)
        )
        st.altair_chart(chart, use_container_width=True)

# ================== PESTAÑA 2: AGREGAR INGRESO ==================
elif menu == "Agregar Ingreso":
    st.header("💰 Agregar Ingreso")
    
    # Mostrar mensaje de éxito si existe
    if "mensaje_ingreso_exitoso" in st.session_state:
        st.success("✅ Información Guardada con éxito")
        st.info(st.session_state["mensaje_ingreso_exitoso"])
        del st.session_state["mensaje_ingreso_exitoso"]
    
    # Valores iniciales para los campos
    monto_inicial = "0.00" if "limpiar_ingreso" in st.session_state else f"{st.session_state.get('ingreso_monto', 0.0):.2f}"
    desc_inicial = "" if "limpiar_ingreso" in st.session_state else st.session_state.get("ingreso_desc", "")
    fecha_inicial = datetime.today() if "limpiar_ingreso" in st.session_state else st.session_state.get("ingreso_fecha", datetime.today())
    
    # Limpiar la bandera si existe
    if "limpiar_ingreso" in st.session_state:
        del st.session_state["limpiar_ingreso"]
    
    # Campo de monto como texto para permitir entrada libre
    monto_texto = st.text_input("Monto del ingreso", value=monto_inicial, key="ingreso_monto_texto", help="Ingrese el monto (ej: 1.01, 150.99)")
    
    # Validar y convertir el monto
    try:
        monto = float(monto_texto.replace(",", "")) if monto_texto.strip() != "" else 0.0
        if monto < 0:
            st.error("❌ El monto no puede ser negativo.")
            monto = 0.0
        elif monto_texto.strip() != "" and monto == 0:
            st.warning("⚠️ Verifique que el monto sea válido.")
    except ValueError:
        st.error("❌ Por favor ingrese un número válido (ej: 1.01, 150.99)")
        monto = 0.0
    
    # Mostrar monto formateado como confirmación
    if monto > 0:
        st.info(f"💰 Monto a registrar: ${monto:,.2f}")
    
    descripcion = st.text_input("Descripción", value=desc_inicial, key="ingreso_desc")
    fecha = st.date_input("Fecha", value=fecha_inicial, key="ingreso_fecha")

    if st.button("Registrar ingreso", key="btn_ingreso"):
        if monto <= 0 or descripcion.strip() == "":
            st.error("❌ Todos los campos son obligatorios y monto debe ser mayor que 0.")
        else:
            data["ingresos"].append({
                "monto": monto,
                "descripcion": descripcion.strip(),
                "fecha": fecha.strftime("%Y-%m-%d")
            })
            guardar_datos(data)
            # Guardar mensaje para mostrar después del rerun
            st.session_state["mensaje_ingreso_exitoso"] = f"💰 Ingreso registrado: ${monto:,.2f} - {descripcion}"
            # Marcar que se debe limpiar el formulario
            st.session_state["limpiar_ingreso"] = True
            st.rerun()

# ================== PESTAÑA 3: AÑADIR GASTO ==================
elif menu == "Añadir Gasto":
    st.header("💸 Gasto de Ingreso Mensual por Categoría")
    
    # Mostrar mensaje de éxito si existe
    if "mensaje_gasto_exitoso" in st.session_state:
        st.success("✅ Información Guardada con éxito")
        st.info(st.session_state["mensaje_gasto_exitoso"])
        del st.session_state["mensaje_gasto_exitoso"]
    
    # Valores iniciales para los campos
    monto_inicial = "0.00" if "limpiar_gasto" in st.session_state else f"{st.session_state.get('gasto_monto', 0.0):.2f}"
    desc_inicial = "" if "limpiar_gasto" in st.session_state else st.session_state.get("gasto_desc", "")
    fecha_inicial = datetime.today() if "limpiar_gasto" in st.session_state else st.session_state.get("gasto_fecha", datetime.today())
    
    # Limpiar la bandera si existe
    if "limpiar_gasto" in st.session_state:
        del st.session_state["limpiar_gasto"]
    
    # Campo de monto como texto para permitir entrada libre
    monto_texto = st.text_input("Monto del gasto", value=monto_inicial, key="gasto_monto_texto", help="Ingrese el monto (ej: 1.01, 150.99)")
    
    # Validar y convertir el monto
    try:
        monto = float(monto_texto.replace(",", "")) if monto_texto.strip() != "" else 0.0
        if monto < 0:
            st.error("❌ El monto no puede ser negativo.")
            monto = 0.0
        elif monto_texto.strip() != "" and monto == 0:
            st.warning("⚠️ Verifique que el monto sea válido.")
    except ValueError:
        st.error("❌ Por favor ingrese un número válido (ej: 1.01, 150.99)")
        monto = 0.0
    
    # Mostrar monto formateado como confirmación
    if monto > 0:
        st.info(f"💸 Monto a registrar: ${monto:,.2f}")
    
    descripcion = st.text_input("Descripción", value=desc_inicial, key="gasto_desc")
    categoria = st.selectbox("Categoría", list(categorias.keys()), key="gasto_cat")
    subcategoria = st.selectbox("Subcategoría", categorias[categoria], key="gasto_subcat")
    medio_pago = st.selectbox("Medio de Pago", ["Efectivo", "Tarjeta de Crédito", "Transferencia"], key="gasto_mediopago")
    fecha = st.date_input("Fecha", value=fecha_inicial, key="gasto_fecha")

    if st.button("Registrar gasto", key="btn_gasto"):
        if monto <= 0 or descripcion.strip() == "":
            st.error("❌ Todos los campos son obligatorios y monto debe ser mayor que 0.")
        else:
            data["gastos"].append({
                "monto": monto,
                "descripcion": descripcion.strip(),
                "categoria": categoria,
                "subcategoria": subcategoria,
                "medio_pago": medio_pago,
                "fecha": fecha.strftime("%Y-%m-%d")
            })
            guardar_datos(data)
            # Guardar mensaje para mostrar después del rerun
            st.session_state["mensaje_gasto_exitoso"] = f"💸 Gasto registrado: ${monto:,.2f} - {descripcion} ({categoria})"
            # Marcar que se debe limpiar el formulario
            st.session_state["limpiar_gasto"] = True
            st.rerun()

# ================== PESTAÑA 4: BALANCE ==================
elif menu == "Balance":
    st.header("📈 Balance de Ingreso Mensual y por Subcategoría")
    ingresos_df = pd.DataFrame(data["ingresos"])
    gastos_df = pd.DataFrame(data["gastos"])

    if ingresos_df.empty and gastos_df.empty:
        st.info("No hay registros de ingresos ni gastos.")
    else:
        # Meses
        if not ingresos_df.empty:
            ingresos_df["mes"] = pd.to_datetime(ingresos_df["fecha"]).dt.to_period("M").astype(str)
        else:
            ingresos_df = pd.DataFrame(columns=["monto","descripcion","fecha","mes"])
        if not gastos_df.empty:
            gastos_df["mes"] = pd.to_datetime(gastos_df["fecha"]).dt.to_period("M").astype(str)
        else:
            gastos_df = pd.DataFrame(columns=["monto","descripcion","categoria","subcategoria","medio_pago","fecha","mes"])
        
        meses_disponibles = sorted(list(set(list(ingresos_df["mes"]) + list(gastos_df["mes"]))))

        if meses_disponibles:
            mes_seleccionado = st.selectbox("Filtrar por mes y año", meses_disponibles, key="balance_mes")
        else:
            mes_seleccionado = None

        if mes_seleccionado:
            ingresos_mes = ingresos_df[ingresos_df["mes"]==mes_seleccionado] if not ingresos_df.empty else pd.DataFrame()
            gastos_mes = gastos_df[gastos_df["mes"]==mes_seleccionado] if not gastos_df.empty else pd.DataFrame()

            total_ingresos = ingresos_mes["monto"].sum() if not ingresos_mes.empty else 0.0
            total_gastos = gastos_mes["monto"].sum() if not gastos_mes.empty else 0.0
            balance = total_ingresos - total_gastos

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
            col2.metric("Total Gastos", f"${total_gastos:,.2f}")
            col3.metric("Balance", f"${balance:,.2f}", delta_color="inverse" if balance<0 else "normal")

            # Gráfico Balance General
            resumen_df = pd.DataFrame({
                "Tipo": ["Ingresos", "Gastos", "Balance"],
                "Monto": [total_ingresos, total_gastos, balance]
            })
            # Definir el orden específico para las categorías
            domain_order = ["Ingresos", "Gastos", "Balance"]
            color_range = ["green", "red", "blue"]
            
            chart_mes = alt.Chart(resumen_df).mark_bar().encode(
                x=alt.X('Tipo', sort=domain_order),  # Orden específico
                y='Monto',
                color=alt.Color('Tipo', 
                    scale=alt.Scale(domain=domain_order, range=color_range),
                    legend=alt.Legend(title="Tipo")
                ),
                tooltip=['Tipo', 'Monto']
            )
            st.altair_chart(chart_mes, use_container_width=True)

            # Gráfico por Subcategoría
            if not gastos_mes.empty:
                st.subheader("Gastos por Subcategoría")
                subcat_list = []
                for cat in categorias.keys():
                    for sub in categorias[cat]:
                        gastado = gastos_mes[(gastos_mes["categoria"]==cat) & (gastos_mes["subcategoria"]==sub)]["monto"].sum()
                        presup = presupuesto.get(mes_seleccionado, {}).get(cat, 0.0)
                        subcat_list.append({"Categoría": cat, "Subcategoría": sub, "Gastado": gastado, "Presupuesto": presup, "Excedido": gastado>presup})
                subcat_df = pd.DataFrame(subcat_list)
                subcat_df["Gastado"] = subcat_df["Gastado"].astype(float)
                subcat_df["Presupuesto"] = subcat_df["Presupuesto"].astype(float)
                color_scale = alt.Scale(domain=subcat_df["Categoría"], scheme='category10')
                chart_sub = alt.Chart(subcat_df).mark_bar().encode(
                    x='Subcategoría',
                    y='Gastado',
                    color=alt.condition(
                        alt.datum.Excedido,
                        alt.value("red"),
                        alt.Color('Categoría', scale=color_scale, legend=None)
                    ),
                    tooltip=['Categoría','Subcategoría','Gastado','Presupuesto']
                )
                st.altair_chart(chart_sub, use_container_width=True)

# ================== PESTAÑA 5: REPORTE DETALLADO ==================
elif menu == "Reporte Detallado":
    st.header("📋 Reporte Detallado de Ingreso Mensual Familiar")
    
    # Convertir datos a DataFrames
    ingresos_df = pd.DataFrame(data["ingresos"])
    gastos_df = pd.DataFrame(data["gastos"])
    
    if ingresos_df.empty and gastos_df.empty:
        st.info("📭 No hay registros disponibles para generar el reporte.")
    else:
        # Filtro por mes
        meses_disponibles = []
        if not ingresos_df.empty:
            ingresos_df["mes"] = pd.to_datetime(ingresos_df["fecha"]).dt.to_period("M").astype(str)
            meses_disponibles.extend(ingresos_df["mes"].unique())
        if not gastos_df.empty:
            gastos_df["mes"] = pd.to_datetime(gastos_df["fecha"]).dt.to_period("M").astype(str)
            meses_disponibles.extend(gastos_df["mes"].unique())
        
        meses_disponibles = sorted(list(set(meses_disponibles)))
        
        if meses_disponibles:
            col1, col2 = st.columns([1, 3])
            with col1:
                mes_filtro = st.selectbox("📅 Filtrar por mes:", ["Todos los meses"] + meses_disponibles, key="reporte_mes")
            with col2:
                formato_reporte = st.selectbox("📊 Formato de reporte:", ["Resumen Ejecutivo", "Detalle Completo"], key="formato")
        
        # ============ SECCIÓN 1: RESUMEN EJECUTIVO ============
        st.subheader("📈 Resumen Ejecutivo")
        
        # Filtrar datos por mes si se seleccionó
        if mes_filtro != "Todos los meses":
            ingresos_filtrados = ingresos_df[ingresos_df["mes"] == mes_filtro] if not ingresos_df.empty else pd.DataFrame()
            gastos_filtrados = gastos_df[gastos_df["mes"] == mes_filtro] if not gastos_df.empty else pd.DataFrame()
            presupuesto_mes = presupuesto.get(mes_filtro, {})
        else:
            ingresos_filtrados = ingresos_df
            gastos_filtrados = gastos_df
            presupuesto_mes = {}
        
        # Métricas principales
        total_ingresos = ingresos_filtrados["monto"].sum() if not ingresos_filtrados.empty else 0.0
        total_gastos = gastos_filtrados["monto"].sum() if not gastos_filtrados.empty else 0.0
        total_presupuesto = sum(presupuesto_mes.values()) if presupuesto_mes else 0.0
        balance_final = total_ingresos - total_gastos
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Ingresos", f"${total_ingresos:,.2f}")
        with col2:
            st.metric("💸 Total Gastos", f"${total_gastos:,.2f}")
        with col3:
            st.metric("📊 Presupuesto", f"${total_presupuesto:,.2f}")
        with col4:
            color = "normal" if balance_final >= 0 else "inverse"
            st.metric("⚖️ Balance Final", f"${balance_final:,.2f}", delta_color=color)
        
        # ============ SECCIÓN 2: ANÁLISIS POR CATEGORÍAS ============
        if not gastos_filtrados.empty and presupuesto_mes:
            st.subheader("🏷️ Análisis por Categorías")
            
            analisis_cat = []
            for categoria in categorias.keys():
                gasto_cat = gastos_filtrados[gastos_filtrados["categoria"] == categoria]["monto"].sum()
                presup_cat = presupuesto_mes.get(categoria, 0.0)
                diferencia = presup_cat - gasto_cat
                porcentaje = (gasto_cat / presup_cat * 100) if presup_cat > 0 else 0
                estado = "🔴 Excedido" if gasto_cat > presup_cat else "🟢 Dentro" if gasto_cat > 0 else "⚪ Sin gastos"
                
                analisis_cat.append({
                    "Categoría": categoria,
                    "Presupuestado": presup_cat,
                    "Gastado": gasto_cat,
                    "Diferencia": diferencia,
                    "% Usado": porcentaje,
                    "Estado": estado
                })
            
            analisis_df = pd.DataFrame(analisis_cat)
            if not analisis_df.empty:
                st.dataframe(
                    analisis_df.style.format({
                        "Presupuestado": "${:,.2f}",
                        "Gastado": "${:,.2f}",
                        "Diferencia": "${:,.2f}",
                        "% Usado": "{:.1f}%"
                    }),
                    use_container_width=True
                )
        
        # ============ SECCIÓN 3: DETALLE COMPLETO (SI SE SELECCIONA) ============
        if formato_reporte == "Detalle Completo":
            
            # Tabla de Ingresos
            if not ingresos_filtrados.empty:
                st.subheader("💰 Detalle de Ingresos")
                ingresos_display = ingresos_filtrados.copy()
                ingresos_display["Monto"] = ingresos_display["monto"].apply(lambda x: f"${x:,.2f}")
                ingresos_display = ingresos_display[["fecha", "Monto", "descripcion"]]
                ingresos_display.columns = ["Fecha", "Monto", "Descripción"]
                st.dataframe(ingresos_display, use_container_width=True)
            
            # Tabla de Gastos
            if not gastos_filtrados.empty:
                st.subheader("💸 Detalle de Gastos")
                gastos_display = gastos_filtrados.copy()
                gastos_display["Monto"] = gastos_display["monto"].apply(lambda x: f"${x:,.2f}")
                gastos_display = gastos_display[["fecha", "categoria", "subcategoria", "Monto", "descripcion", "medio_pago"]]
                gastos_display.columns = ["Fecha", "Categoría", "Subcategoría", "Monto", "Descripción", "Medio de Pago"]
                st.dataframe(gastos_display, use_container_width=True)
            
            # ============ NUEVO: RESUMEN POR SUBCATEGORÍA ============
            if not gastos_filtrados.empty:
                st.subheader("📋 Resumen por Subcategoría")
                
                # Agrupar por subcategoría
                resumen_subcat = gastos_filtrados.groupby("subcategoria")["monto"].sum().reset_index()
                resumen_subcat.columns = ["Subcategoría", "Monto Total"]
                
                # Calcular porcentajes
                total_gastos_subcategoria = resumen_subcat["Monto Total"].sum()
                resumen_subcat["Porcentaje"] = (resumen_subcat["Monto Total"] / total_gastos_subcategoria * 100).round(2)
                
                # Formatear para mostrar
                resumen_subcat_display = resumen_subcat.copy()
                resumen_subcat_display["Monto Total"] = resumen_subcat_display["Monto Total"].apply(lambda x: f"${x:,.2f}")
                resumen_subcat_display["Porcentaje"] = resumen_subcat_display["Porcentaje"].apply(lambda x: f"{x}%")
                
                st.dataframe(resumen_subcat_display, use_container_width=True, hide_index=True)
            
            # ============ NUEVO: RESUMEN POR MEDIO DE PAGO ============
            if not gastos_filtrados.empty:
                st.subheader("💳 Resumen por Medio de Pago")
                
                # Obtener todos los medios de pago únicos que existen en los datos
                medios_pago_existentes = gastos_filtrados['medio_pago'].unique()
                
                if len(medios_pago_existentes) > 0:
                    # Agrupar por medio de pago
                    resumen_medio_pago = gastos_filtrados.groupby("medio_pago")["monto"].sum().reset_index()
                    resumen_medio_pago.columns = ["Medio de Pago", "Monto Total"]
                    
                    # Ordenar por monto total descendente
                    resumen_medio_pago = resumen_medio_pago.sort_values("Monto Total", ascending=False)
                    
                    # Calcular porcentajes
                    total_gastos_medio = resumen_medio_pago["Monto Total"].sum()
                    resumen_medio_pago["Porcentaje"] = (resumen_medio_pago["Monto Total"] / total_gastos_medio * 100).round(2)
                    
                    # Formatear para mostrar
                    resumen_medio_pago_display = resumen_medio_pago.copy()
                    resumen_medio_pago_display["Monto Total"] = resumen_medio_pago_display["Monto Total"].apply(lambda x: f"${x:,.2f}")
                    resumen_medio_pago_display["Porcentaje"] = resumen_medio_pago_display["Porcentaje"].apply(lambda x: f"{x}%")
                    
                    st.dataframe(resumen_medio_pago_display, use_container_width=True, hide_index=True)
                    
                    # Mostrar información adicional sobre los medios de pago
                    st.caption(f"📊 Medios de pago utilizados: {', '.join(medios_pago_existentes)}")
                else:
                    st.info("📭 No hay información de medios de pago disponible.")
            else:
                st.info("📭 No hay gastos para analizar por medio de pago.")
        
        # ============ SECCIÓN 4: GRÁFICOS COMPARATIVOS ============
        st.subheader("📊 Análisis Visual")
        
        if not gastos_filtrados.empty:
            # Gráfico de gastos por categoría
            gastos_por_cat = gastos_filtrados.groupby("categoria")["monto"].sum().reset_index()
            gastos_por_cat.columns = ["Categoría", "Total"]
            
            # Calcular porcentajes
            total_general = gastos_por_cat["Total"].sum()
            gastos_por_cat["Porcentaje"] = (gastos_por_cat["Total"] / total_general * 100).round(1)
            gastos_por_cat["Etiqueta"] = gastos_por_cat.apply(
                lambda row: f"{row['Categoría']}\n{row['Porcentaje']}%\n${row['Total']:,.0f}", 
                axis=1
            )
            
            # Crear gráfico base
            base_chart = alt.Chart(gastos_por_cat).add_selection(
                alt.selection_single()
            )
            
            # Gráfico de pastel con porcentajes
            pie_chart = base_chart.mark_arc(outerRadius=120).encode(
                theta=alt.Theta("Total:Q"),
                color=alt.Color("Categoría:N", 
                    scale=alt.Scale(scheme='category10'),
                    legend=alt.Legend(title="Categorías", orient="right")
                ),
                tooltip=["Categoría:N", 
                        alt.Tooltip("Total:Q", format="$,.0f"),
                        alt.Tooltip("Porcentaje:Q", format=".1f", title="Porcentaje %")]
            )
            
            # Etiquetas con porcentajes
            text_chart = base_chart.mark_text(
                align='center', 
                baseline='middle', 
                fontSize=10, 
                fontWeight='bold'
            ).encode(
                theta=alt.Theta("Total:Q"),
                text=alt.condition(
                    alt.datum.Porcentaje > 5,  # Solo mostrar texto si el porcentaje es > 5%
                    alt.Text("Porcentaje:Q", format=".1f"),
                    alt.value("")
                ),
                color=alt.value("white")
            )
            
            # Combinar gráficos
            final_chart = (pie_chart + text_chart).resolve_scale(
                color="independent"
            )
            
            st.altair_chart(final_chart, use_container_width=True)
            
            # Tabla resumen con porcentajes
            st.subheader("📋 Resumen por Categorías")
            tabla_resumen = gastos_por_cat[["Categoría", "Total", "Porcentaje"]].copy()
            tabla_resumen["Total"] = tabla_resumen["Total"].apply(lambda x: f"${x:,.2f}")
            tabla_resumen["Porcentaje"] = tabla_resumen["Porcentaje"].apply(lambda x: f"{x}%")
            tabla_resumen.columns = ["Categoría", "Monto Total", "Porcentaje"]
            st.dataframe(tabla_resumen, use_container_width=True, hide_index=True)
        
        # ============ SECCIÓN 5: ALERTAS Y RECOMENDACIONES ============
        st.subheader("⚠️ Alertas y Recomendaciones")
        
        alertas = []
        if balance_final < 0:
            alertas.append("🔴 **ALERTA CRÍTICA**: Gastos superan los ingresos")
        
        if presupuesto_mes:
            categorias_excedidas = []
            for categoria in categorias.keys():
                gasto_cat = gastos_filtrados[gastos_filtrados["categoria"] == categoria]["monto"].sum() if not gastos_filtrados.empty else 0
                presup_cat = presupuesto_mes.get(categoria, 0.0)
                if gasto_cat > presup_cat and presup_cat > 0:
                    categorias_excedidas.append(f"{categoria} (${gasto_cat-presup_cat:,.2f} sobre presupuesto)")
            
            if categorias_excedidas:
                alertas.append(f"🟡 **Categorías con presupuesto excedido**: {', '.join(categorias_excedidas)}")
        
        if total_ingresos > 0:
            porcentaje_ahorro = ((total_ingresos - total_gastos) / total_ingresos) * 100
            if porcentaje_ahorro < 10:
                alertas.append("🟡 **Recomendación**: Tasa de ahorro baja, considere reducir gastos opcionales")
            elif porcentaje_ahorro > 20:
                alertas.append("🟢 **Excelente**: Mantiene una buena tasa de ahorro")
        
        if alertas:
            for alerta in alertas:
                st.markdown(alerta)
        else:
            st.success("✅ No hay alertas. Su gestión financiera está en buen estado.")

# ================== PESTAÑA 6: EDITAR REGISTRO ==================
elif menu == "Editar Registro":
    st.header("📝 Editar Registro de Ingreso Mensual")
    
    # Mostrar mensaje de éxito si existe
    if "mensaje_edicion_exitoso" in st.session_state:
        st.success("✅ Registro actualizado con éxito")
        st.info(st.session_state["mensaje_edicion_exitoso"])
        del st.session_state["mensaje_edicion_exitoso"]
    
    # Selector de tipo de registro
    tipo_edicion = st.radio("Seleccione el tipo de registro a editar:", ["Ingreso", "Gasto"], key="tipo_edicion")
    
    # ============ EDICIÓN DE INGRESOS ============
    if tipo_edicion == "Ingreso":
        st.subheader("💰 Editar Ingresos")
        
        if data["ingresos"]:
            # Crear lista de opciones para el selectbox
            opciones_ingresos = []
            for idx, ingreso in enumerate(data["ingresos"]):
                fecha_formateada = pd.to_datetime(ingreso['fecha']).strftime("%d/%m/%Y")
                opciones_ingresos.append(f"[{idx+1}] {fecha_formateada} - ${ingreso['monto']:.2f} - {ingreso['descripcion']}")
            
            # Selector de ingreso a editar
            ingreso_seleccionado = st.selectbox(
                "Seleccione el ingreso a editar:",
                opciones_ingresos,
                key="ingreso_a_editar"
            )
            
            if ingreso_seleccionado:
                # Obtener índice del ingreso seleccionado (restar 1 porque mostramos idx+1)
                idx_ingreso = int(ingreso_seleccionado.split("]")[0].replace("[", "")) - 1
                ingreso_actual = data["ingresos"][idx_ingreso]
                
                st.subheader("✏️ Editar Datos del Ingreso")
                
                # Campos de edición directa
                nuevo_monto_texto = st.text_input(
                    "Monto:", 
                    value=f"{ingreso_actual['monto']:.2f}",
                    key=f"edit_ingreso_monto_{idx_ingreso}",
                    help="Ingrese el nuevo monto (ej: 1.01, 150.99)"
                )
                
                # Validar monto
                try:
                    nuevo_monto = float(nuevo_monto_texto.replace(",", "")) if nuevo_monto_texto.strip() != "" else 0.0
                    if nuevo_monto <= 0:
                        st.error("❌ El monto debe ser mayor que 0.")
                        nuevo_monto = ingreso_actual['monto']  # Mantener valor original
                except ValueError:
                    st.error("❌ Por favor ingrese un número válido")
                    nuevo_monto = ingreso_actual['monto']  # Mantener valor original
                
                nueva_descripcion = st.text_input(
                    "Descripción:",
                    value=ingreso_actual['descripcion'],
                    key=f"edit_ingreso_desc_{idx_ingreso}"
                )
                
                nueva_fecha = st.date_input(
                    "Fecha:",
                    value=pd.to_datetime(ingreso_actual['fecha']).date(),
                    key=f"edit_ingreso_fecha_{idx_ingreso}"
                )
                
                # Botón de actualización
                if st.button("💾 Actualizar Ingreso", key="btn_actualizar_ingreso", type="primary"):
                    if nueva_descripcion.strip() == "":
                        st.error("❌ La descripción no puede estar vacía.")
                    else:
                        # Actualizar el registro
                        data["ingresos"][idx_ingreso] = {
                            "monto": nuevo_monto,
                            "descripcion": nueva_descripcion.strip(),
                            "fecha": nueva_fecha.strftime("%Y-%m-%d")
                        }
                        guardar_datos(data)
                        
                        # Guardar mensaje para mostrar después del rerun
                        st.session_state["mensaje_edicion_exitoso"] = f"💰 Ingreso actualizado: ${nuevo_monto:,.2f} - {nueva_descripcion}"
                        st.rerun()
        else:
            st.info("📭 No hay ingresos registrados para editar.")
    
    # ============ EDICIÓN DE GASTOS ============
    elif tipo_edicion == "Gasto":
        st.subheader("💸 Editar Gastos")
        
        if data["gastos"]:
            # Crear lista de opciones para el selectbox
            opciones_gastos = []
            for idx, gasto in enumerate(data["gastos"]):
                fecha_formateada = pd.to_datetime(gasto['fecha']).strftime("%d/%m/%Y")
                medio_pago = gasto.get('medio_pago', 'N/A')
                opciones_gastos.append(f"[{idx+1}] {fecha_formateada} - ${gasto['monto']:.2f} - {gasto['descripcion']} - {gasto['categoria']} ({gasto['subcategoria']}) - {medio_pago}")
            
            # Selector de gasto a editar
            gasto_seleccionado = st.selectbox(
                "Seleccione el gasto a editar:",
                opciones_gastos,
                key="gasto_a_editar"
            )
            
            if gasto_seleccionado:
                # Obtener índice del gasto seleccionado (restar 1 porque mostramos idx+1)
                idx_gasto = int(gasto_seleccionado.split("]")[0].replace("[", "")) - 1
                gasto_actual = data["gastos"][idx_gasto]
                
                st.subheader("✏️ Editar Datos del Gasto")
                
                # Campos de edición directa
                nuevo_monto_texto = st.text_input(
                    "Monto:", 
                    value=f"{gasto_actual['monto']:.2f}",
                    key=f"edit_gasto_monto_{idx_gasto}",
                    help="Ingrese el nuevo monto (ej: 1.01, 150.99)"
                )
                
                # Validar monto
                try:
                    nuevo_monto = float(nuevo_monto_texto.replace(",", "")) if nuevo_monto_texto.strip() != "" else 0.0
                    if nuevo_monto <= 0:
                        st.error("❌ El monto debe ser mayor que 0.")
                        nuevo_monto = gasto_actual['monto']  # Mantener valor original
                except ValueError:
                    st.error("❌ Por favor ingrese un número válido")
                    nuevo_monto = gasto_actual['monto']  # Mantener valor original
                
                nueva_descripcion = st.text_input(
                    "Descripción:",
                    value=gasto_actual['descripcion'],
                    key=f"edit_gasto_desc_{idx_gasto}"
                )
                
                nueva_categoria = st.selectbox(
                    "Categoría:",
                    list(categorias.keys()),
                    index=list(categorias.keys()).index(gasto_actual['categoria']),
                    key=f"edit_gasto_cat_{idx_gasto}"
                )
                
                nueva_subcategoria = st.selectbox(
                    "Subcategoría:",
                    categorias[nueva_categoria],
                    index=categorias[nueva_categoria].index(gasto_actual['subcategoria']) if gasto_actual['subcategoria'] in categorias[nueva_categoria] else 0,
                    key=f"edit_gasto_subcat_{idx_gasto}"
                )
                
                nuevo_medio_pago = st.selectbox(
                    "Medio de pago:",
                    ["Efectivo", "Tarjeta de Crédito", "Transferencia"],
                    index=["Efectivo", "Tarjeta de Crédito", "Transferencia"].index(gasto_actual.get('medio_pago', 'Efectivo')) if gasto_actual.get('medio_pago', 'Efectivo') in ["Efectivo", "Tarjeta de Crédito", "Transferencia"] else 0,
                    key=f"edit_gasto_mediopago_{idx_gasto}"
                )
                
                nueva_fecha = st.date_input(
                    "Fecha:",
                    value=pd.to_datetime(gasto_actual['fecha']).date(),
                    key=f"edit_gasto_fecha_{idx_gasto}"
                )
                
                # Botón de actualización
                if st.button("💾 Actualizar Gasto", key="btn_actualizar_gasto", type="primary"):
                    if nueva_descripcion.strip() == "":
                        st.error("❌ La descripción no puede estar vacía.")
                    else:
                        # Actualizar el registro
                        data["gastos"][idx_gasto] = {
                            "monto": nuevo_monto,
                            "descripcion": nueva_descripcion.strip(),
                            "categoria": nueva_categoria,
                            "subcategoria": nueva_subcategoria,
                            "medio_pago": nuevo_medio_pago,
                            "fecha": nueva_fecha.strftime("%Y-%m-%d")
                        }
                        guardar_datos(data)
                        
                        # Guardar mensaje para mostrar después del rerun
                        st.session_state["mensaje_edicion_exitoso"] = f"💸 Gasto actualizado: ${nuevo_monto:,.2f} - {nueva_descripcion} ({nueva_categoria})"
                        st.rerun()
        else:
            st.info("📭 No hay gastos registrados para editar.")

# ================== PESTAÑA 7: ELIMINAR REGISTRO ==================
elif menu == "Eliminar Registro":
    st.header("🗑 Eliminación de Registros de Ingreso Mensual")
    
    # Selector de tipo de eliminación
    tipo_eliminacion = st.radio(
        "Seleccione el tipo de eliminación:",
        ["Registro Individual", "Eliminar por Mes", "Reiniciar Sistema Completo"],
        key="tipo_eliminacion"
    )
    
    # ============ ELIMINACIÓN INDIVIDUAL ============
    if tipo_eliminacion == "Registro Individual":
        st.subheader("🔍 Eliminación Individual")
        tipo = st.radio("Seleccione tipo de registro a eliminar", ["Ingreso","Gasto"], key="elim_tipo")

        if tipo == "Ingreso" and data["ingresos"]:
            st.subheader("💰 Ingresos Registrados")
            for idx, row in enumerate(data["ingresos"]):
                col1, col2, col3, col4 = st.columns([3,2,2,1])
                col1.write(row['descripcion'])
                col2.write(f"${row['monto']:.2f}")
                col3.write(row['fecha'])
                if col4.button("Eliminar", key=f"del_ing_{idx}"):
                    data["ingresos"].pop(idx)
                    guardar_datos(data)
                    st.success(f"✅ Ingreso eliminado: {row['descripcion']}")
                    st.rerun()

        elif tipo == "Gasto" and data["gastos"]:
            st.subheader("💸 Gastos Registrados")
            for idx, row in enumerate(data["gastos"]):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,1])
                col1.write(row['categoria'])
                col2.write(row['subcategoria'])
                col3.write(row['descripcion'])
                col4.write(f"${row['monto']:.2f}")
                col5.write(row.get('medio_pago', 'N/A'))
                col6.write(row['fecha'])
                if col7.button("Eliminar", key=f"del_gas_{idx}"):
                    data["gastos"].pop(idx)
                    guardar_datos(data)
                    st.success(f"✅ Gasto eliminado: {row['descripcion']}")
                    st.rerun()

        else:
            st.info(f"No hay registros de {tipo.lower()} para eliminar.")
    
    # ============ ELIMINACIÓN POR MES ============
    elif tipo_eliminacion == "Eliminar por Mes":
        st.subheader("📅 Eliminación por Mes")
        
        # Obtener meses disponibles
        meses_disponibles = []
        ingresos_df = pd.DataFrame(data["ingresos"])
        gastos_df = pd.DataFrame(data["gastos"])
        
        if not ingresos_df.empty:
            ingresos_df["mes"] = pd.to_datetime(ingresos_df["fecha"]).dt.to_period("M").astype(str)
            meses_disponibles.extend(ingresos_df["mes"].unique())
        if not gastos_df.empty:
            gastos_df["mes"] = pd.to_datetime(gastos_df["fecha"]).dt.to_period("M").astype(str)
            meses_disponibles.extend(gastos_df["mes"].unique())
        
        meses_disponibles = sorted(list(set(meses_disponibles)))
        
        if meses_disponibles:
            col1, col2 = st.columns([1, 1])
            with col1:
                mes_seleccionado = st.selectbox("Seleccione el mes a eliminar:", meses_disponibles, key="mes_eliminar")
            with col2:
                tipo_datos = st.selectbox("Tipo de datos:", ["Todos", "Solo Ingresos", "Solo Gastos"], key="tipo_datos_mes")
            
            # Mostrar resumen de lo que se va a eliminar
            if mes_seleccionado:
                st.subheader("📋 Vista previa de eliminación")
                
                # Filtrar datos del mes seleccionado
                ingresos_mes = []
                gastos_mes = []
                
                if not ingresos_df.empty:
                    ingresos_mes = ingresos_df[ingresos_df["mes"] == mes_seleccionado].to_dict('records')
                if not gastos_df.empty:
                    gastos_mes = gastos_df[gastos_df["mes"] == mes_seleccionado].to_dict('records')
                
                # Contar registros
                total_ingresos = len(ingresos_mes)
                total_gastos = len(gastos_mes)
                
                if tipo_datos == "Todos":
                    st.warning(f"⚠️ Se eliminarán **{total_ingresos} ingresos** y **{total_gastos} gastos** del mes {mes_seleccionado}")
                elif tipo_datos == "Solo Ingresos":
                    st.warning(f"⚠️ Se eliminarán **{total_ingresos} ingresos** del mes {mes_seleccionado}")
                elif tipo_datos == "Solo Gastos":
                    st.warning(f"⚠️ Se eliminarán **{total_gastos} gastos** del mes {mes_seleccionado}")
                
                # Mostrar detalle
                col1, col2 = st.columns(2)
                
                if (tipo_datos in ["Todos", "Solo Ingresos"]) and ingresos_mes:
                    with col1:
                        st.markdown("**💰 Ingresos a eliminar:**")
                        for ing in ingresos_mes:
                            st.text(f"• ${ing['monto']:.2f} - {ing['descripcion']} ({ing['fecha']})")
                
                if (tipo_datos in ["Todos", "Solo Gastos"]) and gastos_mes:
                    with col2:
                        st.markdown("**💸 Gastos a eliminar:**")
                        for gas in gastos_mes:
                            st.text(f"• ${gas['monto']:.2f} - {gas['descripcion']} ({gas['fecha']})")
                
                # Sistema de confirmación
                st.subheader("🔒 Confirmación de Eliminación")
                confirmacion = st.checkbox(f"Confirmo que deseo eliminar estos registros del mes {mes_seleccionado}", key="confirm_mes")
                
                if confirmacion:
                    if st.button("🗑️ ELIMINAR REGISTROS DEL MES", key="btn_eliminar_mes", type="primary"):
                        # Realizar eliminación
                        registros_eliminados = {"ingresos": 0, "gastos": 0}
                        
                        # Eliminar ingresos si corresponde
                        if tipo_datos in ["Todos", "Solo Ingresos"] and ingresos_mes:
                            data["ingresos"] = [ing for ing in data["ingresos"] 
                                             if pd.to_datetime(ing["fecha"]).strftime("%Y-%m") != mes_seleccionado]
                            registros_eliminados["ingresos"] = total_ingresos
                        
                        # Eliminar gastos si corresponde
                        if tipo_datos in ["Todos", "Solo Gastos"] and gastos_mes:
                            data["gastos"] = [gas for gas in data["gastos"] 
                                            if pd.to_datetime(gas["fecha"]).strftime("%Y-%m") != mes_seleccionado]
                            registros_eliminados["gastos"] = total_gastos
                        
                        # Guardar cambios
                        guardar_datos(data)
                        
                        # Mensaje de confirmación
                        mensaje = f"✅ **Eliminación completada para {mes_seleccionado}:**\n"
                        if registros_eliminados["ingresos"] > 0:
                            mensaje += f"• {registros_eliminados['ingresos']} ingresos eliminados\n"
                        if registros_eliminados["gastos"] > 0:
                            mensaje += f"• {registros_eliminados['gastos']} gastos eliminados"
                        
                        st.success(mensaje)
                        st.rerun()
        else:
            st.info("📭 No hay registros disponibles para eliminar por mes.")
    
    # ============ REINICIAR SISTEMA COMPLETO ============
    elif tipo_eliminacion == "Reiniciar Sistema Completo":
        st.subheader("⚠️ Reiniciar Todo el Sistema")
        st.error("🚨 **ADVERTENCIA CRÍTICA**: Esta acción eliminará TODOS los datos del sistema")
        
        # Mostrar resumen total
        total_ingresos = len(data["ingresos"])
        total_gastos = len(data["gastos"])
        total_presupuestos = len(presupuesto)
        
        st.markdown(f"""
        **📊 Datos que se eliminarán:**
        - **{total_ingresos}** registros de ingresos
        - **{total_gastos}** registros de gastos  
        - **{total_presupuestos}** presupuestos mensuales
        - **Todos los archivos** de configuración
        """)
        
        # Confirmaciones múltiples
        st.markdown("**🔒 Confirmaciones de Seguridad:**")
        confirm1 = st.checkbox("Entiendo que esta acción NO se puede deshacer", key="confirm1")
        confirm2 = st.checkbox("Confirmo que quiero eliminar TODOS los datos", key="confirm2") 
        confirm3 = st.checkbox("Acepto la responsabilidad total de esta eliminación", key="confirm3")
        
        # Campo de texto de confirmación
        texto_confirmacion = st.text_input("Escriba 'ELIMINAR TODO' para proceder:", key="texto_confirm")
        
        if confirm1 and confirm2 and confirm3 and texto_confirmacion == "ELIMINAR TODO":
            if st.button("🚨 ELIMINAR TODOS LOS REGISTROS", key="btn_reset_all", type="primary"):
                data, presupuesto = limpiar_todos_los_registros()
                st.success("✅ Todos los registros fueron eliminados completamente del sistema.")
                st.balloons()  # Efecto visual
                st.rerun()
        elif texto_confirmacion and texto_confirmacion != "ELIMINAR TODO":
            st.error("❌ Debe escribir exactamente 'ELIMINAR TODO' para proceder.")




