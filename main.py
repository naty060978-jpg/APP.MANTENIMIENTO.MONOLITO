import streamlit as st
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# ==========================================
# 1. BASE DE DATOS LOCAL (SQLite)
# ==========================================
DB_NAME = "mantenimiento_ann.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de equipos registrados por dirección
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            direccion TEXT NOT NULL,
            cliente TEXT,
            sitio TEXT,
            sector TEXT NOT NULL,
            tipo TEXT,
            marca TEXT,
            modelo TEXT,
            frigorias INTEGER,
            potencia_kw REAL,
            refrigerante TEXT
        )
    ''')
    
    # Tabla de intervenciones/historial de mantenimientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intervenciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_id INTEGER,
            fecha TEXT,
            tecnico TEXT,
            tipo_trabajo TEXT,
            filtros TEXT,
            drenaje TEXT,
            condensadora TEXT,
            psi TEXT,
            observaciones TEXT,
            foto_bytes BLOB,
            FOREIGN KEY (equipo_id) REFERENCES equipos (id)
        )
    ''')
    conn.commit()
    conn.close()

def obtener_direcciones_guardadas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT direccion FROM equipos ORDER BY direccion ASC")
    filas = cursor.fetchall()
    conn.close()
    return [f[0] for f in filas]

def obtener_equipos_por_direccion(direccion):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, sector, tipo, marca, modelo, frigorias, potencia_kw, refrigerante, cliente, sitio
        FROM equipos 
        WHERE LOWER(direccion) = LOWER(?)
    ''', (direccion.strip(),))
    equipos = cursor.fetchall()
    conn.close()
    return equipos

def guardar_nuevo_equipo(direccion, cliente, sitio, sector, tipo, marca, modelo, frigorias, potencia_kw, refrigerante):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO equipos (direccion, cliente, sitio, sector, tipo, marca, modelo, frigorias, potencia_kw, refrigerante)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (direccion.strip(), cliente, sitio, sector, tipo, marca, modelo, frigorias, potencia_kw, refrigerante))
    conn.commit()
    conn.close()

# Inicializar BD al arrancar
init_db()

# ==========================================
# 2. GENERADOR DE PDF (ReportLab)
# ==========================================
def generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, intervenciones_registro):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    def dibujar_encabezado(canvas_obj, p_y):
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(50, p_y, empresa.upper())
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(450, p_y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        
        p_y -= 20
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(50, p_y, f"REPORTE TÉCNICO DE MANTENIMIENTO Y SERVICE")
        
        p_y -= 15
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(50, p_y, f"Cliente: {cliente} | Sitio/Piso: {sitio}")
        p_y -= 14
        canvas_obj.drawString(50, p_y, f"Dirección: {direccion} | Técnico: {tecnico}")
        
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, p_y - 8, 550, p_y - 8)
        return p_y - 28

    y = dibujar_encabezado(c, height - 50)

    for i, item in enumerate(intervenciones_registro):
        eq = item['equipo']
        data = item['datos']
        
        # Evaluar espacio necesario (datos + foto)
        if y < 270:
            c.showPage()
            y = dibujar_encabezado(c, height - 50)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"UNIDAD #{i+1} - SECTOR: {eq['sector'].upper()} [{data['tipo_trabajo'].upper()}]")
        y -= 15
        
        c.setFont("Helvetica", 9)
        info_equipo = f"Equipo: {eq['tipo']} {eq['marca']} | Mod: {eq['modelo']} | Frigorías: {eq['frigorias']} Frig/h | Potencia: {eq['potencia_kw']} kW | Gas: {eq['refrigerante']}"
        c.drawString(60, y, info_equipo)
        y -= 18
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "DETALLE DE LA INTERVENCIÓN:")
        y -= 14
        
        c.setFont("Helvetica", 9)
        
        if data['tipo_trabajo'] == "Mantenimiento Preventivo":
            c.drawString(70, y, f"• Filtros: {data['filtros']} | • Drenaje: {data['drenaje']} | • Condensadora: {data['condensadora']}")
            y -= 14
            c.drawString(70, y, f"• Presión Gas: {data['psi']} PSI")
            y -= 14
            c.drawString(70, y, f"• Observaciones: {data['observaciones']}")
            y -= 12
        else:
            # Formato simplificado para SERVICE / AVERÍA
            c.drawString(70, y, f"• Descripción de Avería: {data['descripcion_averia']}")
            y -= 14
            c.drawString(70, y, f"• Tareas a Realizar / Realizadas: {data['tareas_servicio']}")
            y -= 14
            c.drawString(70, y, f"• Materiales Necesarios: {data['materiales_necesarios']}")
            y -= 12

        # Adjuntar imagen
        if data['foto_bytes']:
            try:
                img = ImageReader(io.BytesIO(data['foto_bytes']))
                c.drawImage(img, 70, y - 120, width=160, height=110, preserveAspectRatio=True)
                y -= 130
            except Exception:
                y -= 10
        else:
            y -= 5

        # Línea divisoria
        c.setDash(1, 2)
        c.line(50, y, 550, y)
        c.setDash(1, 0)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 3. INTERFAZ STREAMLIT
# ==========================================
st.set_page_config(page_title="ANN Multiservicios - HVAC", layout="centered")
st.title("❄️ Gestión de Mantenimiento y Service")

if 'intervenciones_actuales' not in st.session_state:
    st.session_state.intervenciones_actuales = {}

# DIRECCIÓN Y DATOS DEL CLIENTE
st.subheader("1. Ubicación del Trabajo")

direcciones_existentes = obtener_direcciones_guardadas()
opcion_dir = st.radio("Seleccione el origen de la dirección:", ["Dirección Existente", "Nueva Dirección"], horizontal=True)

if opcion_dir == "Dirección Existente" and direcciones_existentes:
    direccion = st.selectbox("Seleccione Dirección Guardada", direcciones_existentes)
else:
    direccion = st.text_input("Ingrese Nueva Dirección Exacta (Ej: Av. Colon 1234)")

c1, c2 = st.columns(2)
with c1:
    cliente = st.text_input("Cliente / Empresa", value="")
with c2:
    sitio = st.text_input("Edificio / Piso / Sucursal", value="")

tecnico = st.text_input("Técnico Responsable", value="")

st.divider()

# CARGA / SELECCIÓN DE EQUIPOS
if direccion:
    equipos_guardados = obtener_equipos_por_direccion(direccion)
    
    st.subheader(f"2. Equipos en: {direccion}")
    if equipos_guardados:
        st.success(f"Se encontraron {len(equipos_guardados)} equipos registrados en esta dirección.")
    else:
        st.info("No hay equipos registrados aún para esta dirección. Cargue el primer equipo a continuación.")

    # Pestañas: Seleccionar Equipos Guardados vs Agregar Nuevo Equipo
    tab1, tab2 = st.tabs(["📋 Mantenimiento / Service a Equipos", "➕ Registrar Nuevo Equipo en este Sitio"])

    with tab2:
        st.markdown("#### Datos del Nuevo Equipo de Aire Acondicionado")
        with st.form("form_nuevo_equipo", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                sector_n = st.text_input("Ubicación / Sector (Ej: Gerencia, Oficina 2)")
                tipo_n = st.selectbox("Tipo de Unidad", ["Split", "Baja Silueta", "Cassette", "Piso-Techo", "Rooftop", "VRV/VRF", "MultiSplit"])
                marca_n = st.text_input("Marca del Equipo")
                modelo_n = st.text_input("Modelo del Equipo")
            with col_b:
                frigorias_n = st.number_input("Frigorías (Frig/h)", min_value=1000, max_value=60000, value=3000, step=500)
                potencia_kw_n = st.number_input("Potencia Eléctrica (kW)", min_value=0.1, max_value=50.0, value=1.5, step=0.1)
                refrigerante_n = st.selectbox("Gas Refrigerante", ["R410A", "R22", "R32", "R407C", "R134a"])

            if st.form_submit_button("💾 GUARDAR EQUIPO EN BASE DE DATOS"):
                if sector_n and marca_n:
                    guardar_nuevo_equipo(direccion, cliente, sitio, sector_n, tipo_n, marca_n, modelo_n, frigorias_n, potencia_kw_n, refrigerante_n)
                    st.success(f"Equipo cargado correctamente para {direccion}.")
                    st.rerun()
                else:
                    st.error("Por favor complete al menos el Sector y la Marca.")

    with tab1:
        if equipos_guardados:
            st.markdown("#### Seleccione el equipo a intervenir:")
            
            # Formato desplegable para seleccionar equipo
            opciones_dict = {
                eq[0]: f"ID {eq[0]} | {eq[1]} - {eq[2]} {eq[3]} (Mod: {eq[4]} | {eq[5]} Frig/h)" 
                for eq in equipos_guardados
            }
            equipo_sel_id = st.selectbox("Seleccionar Equipo", options=list(opciones_dict.keys()), format_func=lambda x: opciones_dict[x])
            
            # Obtener datos del equipo seleccionado
            eq_datos = next(eq for eq in equipos_guardados if eq[0] == equipo_sel_id)
            eq_dict = {
                'id': eq_datos[0], 'sector': eq_datos[1], 'tipo': eq_datos[2], 
                'marca': eq_datos[3], 'modelo': eq_datos[4], 'frigorias': eq_datos[5], 
                'potencia_kw': eq_datos[6], 'refrigerante': eq_datos[7]
            }

            st.info(f"**Ubicación:** {eq_dict['sector']} | **Marca/Modelo:** {eq_dict['marca']} {eq_dict['modelo']} | **Capacidad:** {eq_dict['frigorias']} Frig/h ({eq_dict['potencia_kw']} kW)")

            # Selector de tipo de trabajo (fuera del formulario para refrescar dinámicamente la UI)
            tipo_trabajo = st.radio("Tipo de Intervención", ["Mantenimiento Preventivo", "Service / Reparación de Avería"], horizontal=True)

            with st.form("form_intervencion", clear_on_submit=False):
                
                if tipo_trabajo == "Mantenimiento Preventivo":
                    c_i1, c_i2 = st.columns(2)
                    with c_i1:
                        psi = st.text_input("Presión de Gas (PSI)", value="65")
                        filtros = st.radio("Filtros de Aire", ["OK", "Limpiados", "Reemplazados"], horizontal=True)
                    with c_i2:
                        drenaje = st.radio("Sistema Drenaje", ["OK", "Destapado", "Corregido"], horizontal=True)
                        condensadora = st.radio("Unidad Exterior", ["OK", "Limpiada", "Reparada"], horizontal=True)

                    observaciones = st.text_area("Observaciones Finales / Recomendaciones", placeholder="Notas de mantenimiento...")
                    
                    descripcion_averia = ""
                    tareas_servicio = ""
                    materiales_necesarios = ""
                else:
                    # Campos específicos para SERVICE / AVERÍA
                    descripcion_averia = st.text_area("Descripción de la Avería", placeholder="Ej: Fuga de gas, falla en placa electrónica, el compresor no arranca...")
                    tareas_servicio = st.text_area("Tareas Realizadas / A Realizar", placeholder="Ej: Detección de fuga, reparación de soldadura, presurización con nitrógeno...")
                    materiales_necesarios = st.text_area("Materiales / Repuestos Necesarios", placeholder="Ej: Capacitor 35uF, garrafa R410A, varilla de plata...")
                    
                    psi = ""
                    filtros = ""
                    drenaje = ""
                    condensadora = ""
                    observaciones = ""

                foto = st.file_uploader("📷 Adjuntar Foto del Equipo / Trabajo Terminado", type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("📌 REGISTRAR TRABAJO EN ESTE EQUIPO"):
                    foto_b = foto.read() if foto else None
                    st.session_state.intervenciones_actuales[eq_dict['id']] = {
                        'equipo': eq_dict,
                        'datos': {
                            'tipo_trabajo': tipo_trabajo,
                            'psi': psi,
                            'filtros': filtros,
                            'drenaje': drenaje,
                            'condensadora': condensadora,
                            'observaciones': observaciones,
                            'descripcion_averia': descripcion_averia,
                            'tareas_servicio': tareas_servicio,
                            'materiales_necesarios': materiales_necesarios,
                            'foto_bytes': foto_b
                        }
                    }
                    st.success(f"Intervención registrada para el equipo en {eq_dict['sector']}.")

# MOSTRAR RESUMEN Y GENERAR PDF
if st.session_state.intervenciones_actuales:
    st.divider()
    st.subheader(f"3. Resumen del Reporte ({len(st.session_state.intervenciones_actuales)} equipos intervenidos)")

    for k, item in st.session_state.intervenciones_actuales.items():
        st.text(f"• {item['equipo']['sector']} | {item['equipo']['marca']} | {item['datos']['tipo_trabajo']}")

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("🗑️ Vaciar Lista del Reporte"):
            st.session_state.intervenciones_actuales = {}
            st.rerun()

    pdf_final = generar_pdf_bytes(
        "ANN Multiservicios", 
        cliente if cliente else "Sin Especificar", 
        sitio if sitio else "Sin Especificar", 
        direccion, 
        tecnico if tecnico else "Sin Especificar", 
        list(st.session_state.intervenciones_actuales.values())
    )

    st.download_button(
        label="📥 DESCARGAR REPORTE PDF COMPLETO",
        data=pdf_final,
        file_name=f"Reporte_Mantenimiento_{direccion.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
