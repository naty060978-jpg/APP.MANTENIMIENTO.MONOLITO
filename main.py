import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# 1. MODELO DE DATOS MEJORADO
class AireAcondicionado:
    def __init__(self, sector, tipo, marca, n_serie, refrigerante):
        self.sector = sector
        self.tipo = tipo
        self.marca = marca
        self.n_serie = n_serie
        self.refrigerante = refrigerante
        self.filtros = "OK"
        self.drenaje = "OK"
        self.condensadora = "OK"
        self.psi = ""
        self.consumo = ""
        self.observaciones = ""
        self.foto_bytes = None

# 2. GENERADOR DE PDF PROFESIONAL (Soporta múltiples páginas y fotos)
def generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, lista_equipos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    def dibujar_encabezado(canvas_obj, p_y):
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(50, p_y, empresa.upper())
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(480, p_y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        p_y -= 20
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(50, p_y, f"REPORTE DE MANTENIMIENTO: {cliente}")
        p_y -= 15
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(50, p_y, f"Sitio: {sitio} | Técnico: {tecnico}")
        canvas_obj.line(50, p_y - 5, 550, p_y - 5)
        return p_y - 35

    y = dibujar_encabezado(c, height - 50)

    for i, eq in enumerate(lista_equipos):
        # Control de espacio para datos + foto
        if y < 280:
            c.showPage()
            y = dibujar_encabezado(c, height - 50)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"UNIDAD #{i+1} - SECTOR: {eq.sector}")
        y -= 15
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Equipo: {eq.tipo} {eq.marca} | S/N: {eq.n_serie} | Gas: {eq.refrigerante}")
        y -= 18
        
        # Tabla de Mantenimiento Realizado
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "TAREAS REALIZADAS:")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(70, y, f"• Limpieza Filtros: {eq.filtros} | • Drenaje: {eq.drenaje} | • Condensadora: {eq.condensadora}")
        y -= 15
        c.drawString(70, y, f"• Presión Gas: {eq.psi} PSI | • Consumo Eléctrico: {eq.consumo} A")
        y -= 15
        c.drawString(70, y, f"• Notas Técnicas: {eq.observaciones}")
        y -= 10

        if eq.foto_bytes:
            try:
                img = ImageReader(io.BytesIO(eq.foto_bytes))
                c.drawImage(img, 70, y - 130, width=180, height=120, preserveAspectRatio=True)
                y -= 145
            except: y -= 10
        
        y -= 5
        c.setDash(1, 2)
        c.line(50, y, 550, y)
        c.setDash(1, 0)
        y -= 25

    c.save()
    buffer.seek(0)
    return buffer

# 3. INTERFAZ STREAMLIT
st.set_page_config(page_title="ANN Service App", layout="centered")
st.title("❄️ Gestión de Mantenimiento ANN")

if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# DATOS DEL CLIENTE
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Cliente / Empresa")
        sitio = st.text_input("Edificio / Piso")
    with c2:
        tecnico = st.text_input("Técnico Responsable")
        direccion = st.text_input("Dirección del Sitio")

st.divider()

# FORMULARIO TÉCNICO
st.subheader(f"Carga de Equipos ({len(st.session_state.equipos)}/20)")

if len(st.session_state.equipos) < 20:
    with st.form("form_mantenimiento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sector = st.text_input("Ubicación (Ej: Gerencia)")
            tipo = st.selectbox("Tipo de Unidad", ["Split", "Baja Silueta", "Cassette", "Piso-Techo", "Rooftop", "VRV/VRF"])
            marca = st.text_input("Marca del Equipo")
            n_serie = st.text_input("Número de Serie")
        with col2:
            refrigerante = st.text_input("Gas Refrigerante")
            psi = st.text_input("Presión (PSI)")
            consumo = st.text_input("Amperaje (A)")
            filtros = st.radio("Filtros de Aire", ["OK", "Limpiados", "Cambiados"], horizontal=True)
        
        col3, col4 = st.columns(2)
        with col3:
            drenaje = st.radio("Sistema Drenaje", ["OK", "Destapado", "Corregido"], horizontal=True)
        with col4:
            condensadora = st.radio("Unidad Exterior", ["OK", "Limpieza Realizada", "Reparada"], horizontal=True)
            
        notas = st.text_area("Observaciones Finales")
        foto = st.file_uploader("Adjuntar Foto del Equipo", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("💾 REGISTRAR EQUIPO"):
            if sector:
                e = AireAcondicionado(sector, tipo, marca, n_serie, refrigerante)
                e.filtros, e.drenaje, e.condensadora = filtros, drenaje, condensadora
                e.psi, e.consumo, e.observaciones = psi, consumo, notas
                if foto: e.foto_bytes = foto.read()
                st.session_state.equipos.append(e)
                st.rerun()
            else: st.error("Debes indicar el Sector.")

# DESCARGA
if st.session_state.equipos:
    st.divider()
    if st.button("🗑️ Borrar Reporte Actual"):
        st.session_state.equipos = []
        st.rerun()

    pdf_final = generar_pdf_bytes("ANN Multiservicios", cliente, sitio, direccion, tecnico, st.session_state.equipos)
    
    st.download_button(
        label="📥 DESCARGAR REPORTE PDF (20 EQUIPOS)",
        data=pdf_final,
        file_name=f"Mantenimiento_{cliente}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
