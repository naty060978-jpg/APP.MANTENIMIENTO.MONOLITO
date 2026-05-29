import streamlit as st
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# 1. MODELO DE DATOS
class AireAcondicionado:
    def __init__(self, sector, marca, modelo, n_serie, tipo, frigorias, refrigerante, consumo):
        self.sector = sector
        self.marca = marca
        self.modelo = modelo
        self.n_serie = n_serie
        self.tipo = tipo
        self.frigorias = frigorias
        self.refrigerante = refrigerante
        self.consumo = consumo
        self.filtros = "OK"
        self.presion = ""
        self.drenaje = "OK"
        self.observaciones = ""
        self.foto_bytes = None

# 2. LÓGICA DE GENERACIÓN DE PDF (CON SALTO DE PÁGINA AUTOMÁTICO)
def generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, lista_equipos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50 # Posición inicial (cerca del tope)

    def encabezado(canvas_obj, pos_y):
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(50, pos_y, empresa.upper())
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(480, pos_y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        pos_y -= 20
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(50, pos_y, f"REPORTE: {cliente} - {sitio}")
        pos_y -= 15
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(50, pos_y, f"Dirección: {direccion} | Técnico: {tecnico}")
        canvas_obj.line(50, pos_y - 5, 550, pos_y - 5)
        return pos_y - 30

    y = encabezado(c, y)

    for i, eq in enumerate(lista_equipos):
        # Verificar si hay espacio para el siguiente bloque (datos + imagen necesita ~250 unidades)
        espacio_necesario = 250 if eq.foto_bytes else 120
        if y < espacio_necesario:
            c.showPage()
            y = height - 50
            y = encabezado(c, y)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"EQUIPO #{i+1} - SECTOR: {eq.sector}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Tipo: {eq.tipo} | Marca: {eq.marca} | S/N: {eq.n_serie}")
        y -= 15
        c.drawString(60, y, f"Gas: {eq.refrigerante} | Presión: {eq.presion} PSI | Consumo: {eq.consumo} A")
        y -= 15
        c.drawString(60, y, f"Estado: Filtros {eq.filtros} / Drenaje {eq.drenaje}")
        y -= 15
        c.drawString(60, y, f"Observaciones: {eq.observaciones}")
        y -= 10

        if eq.foto_bytes:
            try:
                img_data = io.BytesIO(eq.foto_bytes)
                img = ImageReader(img_data)
                # Dibujar imagen (centrada y con tamaño controlado)
                c.drawImage(img, 70, y - 140, width=180, height=130, preserveAspectRatio=True)
                y -= 150
            except:
                y -= 10
        
        c.line(50, y, 300, y)
        y -= 25 # Espacio entre equipos

    c.save()
    buffer.seek(0)
    return buffer

# 3. INTERFAZ STREAMLIT
st.set_page_config(page_title="ANN Mantenimiento v2", layout="wide")

st.title("❄️ Sistema de Mantenimiento ANN")
st.write("Carga hasta 20 equipos por cliente con fotos individuales.")

if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# COLUMNA DE DATOS GENERALES
with st.container():
    col_a, col_b = st.columns(2)
    with col_a:
        empresa = st.text_input("Tu Empresa", "ANN Multiservicios")
        cliente = st.text_input("Nombre del Cliente")
    with col_b:
        tecnico = st.text_input("Técnico a cargo")
        sitio = st.text_input("Edificio/Sitio")
    direccion = st.text_input("Dirección del servicio")

st.divider()

# CARGA DE EQUIPOS
st.subheader(f"Equipos Cargados: {len(st.session_state.equipos)} / 20")

if len(st.session_state.equipos) < 20:
    with st.expander("➕ Click aquí para agregar un nuevo equipo"):
        with st.form("form_nuevo_equipo", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                sector = st.text_input("Sector")
                marca = st.text_input("Marca")
            with c2:
                tipo = st.selectbox("Tipo", ["Split", "Baja Silueta", "Cassette", "Piso-Techo", "Rooftop"])
                n_serie = st.text_input("N° Serie")
            with c3:
                refrigerante = st.text_input("Gas")
                consumo = st.text_input("Amperaje")
            
            obs = st.text_area("Observaciones técnicas")
            foto = st.file_uploader("Foto de este equipo", type=['jpg', 'jpeg', 'png'])
            
            btn_add = st.form_submit_button("Guardar Equipo")
            if btn_add:
                if sector:
                    nuevo = AireAcondicionado(sector, marca, "Modelo", n_serie, tipo, "0", refrigerante, consumo)
                    nuevo.observaciones = obs
                    if foto:
                        nuevo.foto_bytes = foto.read()
                    st.session_state.equipos.append(nuevo)
                    st.rerun()
                else:
                    st.error("Poné al menos el sector para identificar el aire.")
else:
    st.warning("Llegaste al límite de 20 equipos por reporte.")

# LISTADO Y DESCARGA
if st.session_state.equipos:
    st.divider()
    if st.button("🗑️ Borrar todo y empezar de nuevo"):
        st.session_state.equipos = []
        st.rerun()

    pdf_result = generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, st.session_state.equipos)
    
    st.download_button(
        label="✅ GENERAR Y DESCARGAR PDF FINAL",
        data=pdf_result,
        file_name=f"Reporte_{cliente}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
