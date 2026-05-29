import streamlit as st
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# 1. MODELO DE DATOS
class AireAcondicionado:
    def __init__(self, sector, marca, modelo, n_serie, tipo, frigorias, refrigerante, cantidad_gas, consumo, fecha):
        self.sector = sector
        self.marca = marca
        self.modelo = modelo
        self.n_serie = n_serie
        self.tipo = tipo
        self.frigorias = frigorias
        self.refrigerante = refrigerante
        self.cantidad_gas = cantidad_gas
        self.consumo = consumo
        self.fecha = fecha
        self.filtros = "OK"
        self.presion = ""
        self.condensadora = "OK"
        self.drenaje = "OK"
        self.observaciones = ""
        self.foto_bytes = None

# 2. LÓGICA DE GENERACIÓN DE PDF
def generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, lista_equipos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, empresa.upper())
    c.setFont("Helvetica", 10)
    c.drawString(450, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "REPORTE TÉCNICO DE MANTENIMIENTO")
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"CLIENTE: {cliente} | SITIO: {sitio}")
    y -= 15
    c.drawString(50, y, f"DIRECCIÓN: {direccion} | TÉCNICO: {tecnico}")
    c.line(50, y-10, 550, y-10)
    y -= 40

    for eq in lista_equipos:
        if y < 250:
            c.showPage()
            y = 750

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"SECTOR: {eq.sector} | TIPO: {eq.tipo}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Marca/Modelo: {eq.marca} {eq.modelo} | S/N: {eq.n_serie}")
        y -= 15
        c.drawString(60, y, f"Frigorías: {eq.frigorias} | Gas: {eq.refrigerante} | Consumo: {eq.consumo}")
        y -= 15
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(60, y, f"ESTADO: Filtros: {eq.filtros} | Presión: {eq.presion} PSI | Drenaje: {eq.drenaje}")
        y -= 15
        c.drawString(60, y, f"OBSERVACIONES: {eq.observaciones}")
        
        if eq.foto_bytes:
            y -= 130
            img = ImageReader(io.BytesIO(eq.foto_bytes))
            c.drawImage(img, 60, y, width=150, height=120, preserveAspectRatio=True)
            y -= 20
        else:
            y -= 20
            
        c.line(50, y, 300, y)
        y -= 30

    c.save()
    buffer.seek(0)
    return buffer

# 3. INTERFAZ STREAMLIT
st.set_page_config(page_title="ANN Mantenimiento", layout="centered")

st.title("❄️ Gestión de Mantenimiento HVAC")

if 'equipos' not in st.session_state:
    st.session_state.equipos = []

# --- PASO 1: DATOS GENERALES ---
with st.expander("1. Datos del Servicio", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        empresa = st.text_input("Empresa Mantenedora", "ANN Multiservicios")
        cliente = st.text_input("Cliente")
    with col2:
        tecnico = st.text_input("Nombre del Técnico")
        sitio = st.text_input("Sitio / Edificio")
    direccion = st.text_input("Dirección Completa")

# --- PASO 2: AGREGAR EQUIPO ---
st.subheader("2. Registro de Equipos")
with st.form("form_equipo", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        sector = st.text_input("Sector (Ej: Oficina 1)")
        tipo = st.selectbox("Tipo de Equipo", ["Split Pared", "Baja Silueta", "Cassette", "Piso-Techo", "Rooftop", "MultiSplit"])
        marca = st.text_input("Marca")
        n_serie = st.text_input("Número de Serie")
    with c2:
        modelo = st.text_input("Modelo")
        frigorias = st.text_input("Frigorías")
        refrigerante = st.text_input("Tipo de Gas")
        consumo = st.text_input("Consumo (Amper)")
    
    st.write("---")
    st.info("Checklist de Mantenimiento")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        filtros = st.radio("Filtros limpios", ["OK", "SUCIOS"], horizontal=True)
        drenaje = st.radio("Drenaje despejado", ["OK", "OBSTRUIDO"], horizontal=True)
    with f_col2:
        presion = st.text_input("Presión (PSI)")
        observaciones = st.text_area("Observaciones adicionales")
    
    foto = st.file_uploader("Adjuntar foto del equipo", type=['jpg', 'png', 'jpeg'])
    
    submitted = st.form_submit_button("Añadir Equipo al Reporte")
    if submitted:
        nuevo_eq = AireAcondicionado(sector, marca, modelo, n_serie, tipo, frigorias, refrigerante, "N/A", consumo, datetime.now().strftime('%d/%m/%Y'))
        nuevo_eq.filtros = filtros
        nuevo_eq.presion = presion
        nuevo_eq.drenaje = drenaje
        nuevo_eq.observaciones = observaciones
        if foto:
            nuevo_eq.foto_bytes = foto.read()
        st.session_state.equipos.append(nuevo_eq)
        st.success(f"Equipo en {sector} añadido.")

# --- PASO 3: REVISIÓN Y DESCARGA ---
if st.session_state.equipos:
    st.subheader(f"3. Resumen ({len(st.session_state.equipos)} equipos)")
    for i, e in enumerate(st.session_state.equipos):
        st.text(f"📍 {e.sector} - {e.marca} ({e.tipo})")
    
    if st.button("Limpiar Lista"):
        st.session_state.equipos = []
        st.rerun()

    pdf_file = generar_pdf_bytes(empresa, cliente, sitio, direccion, tecnico, st.session_state.equipos)
    
    st.download_button(
        label="📥 Descargar Reporte PDF",
        data=pdf_file,
        file_name=f"Reporte_{cliente}_{sitio}.pdf",
        mime="application/pdf"
    )
