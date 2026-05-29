import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# 1. MODELO DE DATOS DETALLADO
class AireAcondicionado:
    def __init__(self, sector, tipo, marca, n_serie, refrigerante):
        self.sector = sector
        self.tipo = tipo
        self.marca = marca
        self.n_serie = n_serie
        self.refrigerante = refrigerante
        # Campos de Mantenimiento
        self.filtros = "Pendiente"
        self.drenaje = "Pendiente"
        self.condensadora = "Pendiente"
        self.psi = ""
        self.consumo = ""
        self.observaciones = ""
        self.foto_bytes = None

# 2. GENERADOR DE PDF PROFESIONAL
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
        canvas_obj.drawString(50, p_y, f"REPORTE TÉCNICO: {cliente}")
        p_y -= 15
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(50, p_y, f"Ubicación: {sitio} - {direccion} | Técnico: {tecnico}")
        canvas_obj.line(50, p_y - 5, 550, p_y - 5)
        return p_y - 35

    y = dibujar_encabezado(c, height - 50)

    for i, eq in enumerate(lista_equipos):
        # Evaluar espacio (Datos + Checklist + Foto ≈ 280 unidades)
        if y < 280:
            c.showPage()
            y = dibujar_encabezado(c, height - 50)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"EQUIPO #{i+1} - {eq.sector} ({eq.tipo})")
        y -= 15
        
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Marca: {eq.marca} | S/N: {eq.n_serie} | Gas: {eq.refrigerante}")
        y -= 18
        
        # Bloque de Mantenimiento
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y, "ESTADO DEL MANTENIMIENTO:")
        y -= 15
        c.setFont("Helvetica", 10)
        check_text = f"• Filtros: {eq.filtros}  |  • Drenaje: {eq.drenaje}  |  • Condensadora: {eq.condensadora}"
        c.drawString(70, y, check_text)
        y -= 15
        mediciones = f"• Presión: {eq.psi} PSI  |  • Consumo: {eq.consumo} A"
        c.drawString(70, y, mediciones)
        y -= 15
        c.drawString(70, y, f"• Notas: {eq.observaciones}")
        y -= 10

        if eq.foto_bytes:
            try:
                img = ImageReader(io.BytesIO(eq.foto_bytes))
                c.drawImage(img, 70, y - 130, width=170, height=120, preserveAspectRatio=True)
                y -= 140
            except: y -= 10
        
        y -= 10
        c.setDash(1, 2)
        c.line(50, y, 550, y)
        c.setDash(1, 0)
        y -= 25

    c.save()
    buffer.seek(0)
    return buffer

# 3. INTERFAZ DE USUARIO
st.set_page_config(page_title="ANN Service App", layout="centered")
st.title("🛠️ Planilla de Mantenimiento ANN")

if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# DATOS DE CABECERA
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        cliente = st.text_input("Cliente / Razón Social")
        sitio = st.text_input("Nombre del Edificio/Sitio")
    with c2:
        tecnico = st.text_input("Técnico")
        direccion = st.text_input("Dirección")

st.divider()

# FORMULARIO DE CARGA
st.subheader(f"Registro de Equipos ({len(st.session_state.equipos)}/20)")

if len(st.session_state.equipos) < 20:
    with st.form("form_tecnico", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sector = st.text_input("Sector del equipo")
            tipo = st.selectbox("Tipo de Aire", ["Split", "Baja Silueta", "Cassette", "Piso-Techo", "Rooftop", "Vrv/Vrf"])
            marca = st.text_input("Marca")
            n_serie = st.text_input("N° de Serie")
        with col2:
            refrigerante = st.text_input("Tipo de Gas (R410/R22)")
            psi = st.text_input("Presión de trabajo (PSI)")
            consumo = st.text_input("Consumo actual (Amper)")
            filtros = st.radio("Limpieza de Filtros", ["OK", "Realizado", "No requiere"], horizontal=True)
        
        col3, col4 = st.columns(2)
        with col3:
            drenaje = st.radio("Drenaje Despejado", ["OK", "Realizado", "Obstruido"], horizontal=True)
        with col4:
            condensadora = st.radio("Limpieza Condensadora", ["OK", "Realizado", "Sucia"], horizontal=True)
            
        notas = st.text_area("Observaciones técnicas / Notas")
        foto = st.file_uploader("Captura de imagen del equipo", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("💾 GUARDAR ESTE EQUIPO"):
            if sector:
                e = AireAcondicionado(sector, tipo, marca, n_serie, refrigerante)
                e.filtros, e.drenaje, e.condensadora = filtros, drenaje, condensadora
                e.psi, e.consumo, e.observaciones = psi, consumo, notas
                if foto: e.foto_bytes = foto.read()
                st.session_state.equipos.append(e)
                st.rerun()
            else: st.warning("Por favor, indicá el Sector.")

# ACCIONES FINALES
if st.session_state.equipos:
    st.divider()
    if st.button("🗑️ Reiniciar todo el reporte"):
        st.session_state.equipos = []
        st.rerun()

    reporte_pdf = generar_pdf_bytes("ANN Multiservicios", cliente, sitio, direccion, tecnico, st.session_state.equipos)
    
    st.download_button(
        label="📄 DESCARGAR REPORTE PARA EL CLIENTE",
        data=reporte_pdf,
        file_name=f"Mantenimiento_{cliente}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
