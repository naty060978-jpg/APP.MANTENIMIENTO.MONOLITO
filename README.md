Documentación Técnica: Sistema de Gestión de Mantenimiento HVAC (Monolito)

Materia: Programación Avanzada

Nivel: 3º Cuatrimestre

Desarrollador/es: Natalia Espinosa

Tecnologías: Python 3.x, Programación Orientada a Objetos (POO), JSON, ReportLab (PDF).
1. Descripción del Proyecto

El sistema es una herramienta técnica desarrollada para automatizar el registro de mantenimientos preventivos y correctivos de equipos de aire acondicionado. Permite la carga de datos técnicos, la persistencia en archivos JSON para evitar la pérdida de información y la generación automática de un reporte profesional en PDF que incluye el checklist técnico y evidencias fotográficas.
2. Gestión de Requerimientos
Requerimientos Funcionales (RF)

    RF1 - Registro de Clientes y Sitios: Capacidad de organizar equipos por Cliente, Edificio/Sitio y Dirección específica.

    RF2 - Gestión de Inventario: Registro de atributos técnicos del equipo (S/N, Frigorías, Tipo de Gas, Consumo).

    RF3 - Checklist Técnico: Formulario interactivo para estado de filtros, presión, drenaje y observaciones.

    RF4 - Adjunto de Imágenes: Integración de fotografías pre-cargadas para evidenciar el estado del equipo.

    RF5 - Persistencia de Datos: Almacenamiento automático en clientes_mantenimiento.json.

    RF6 - Generación de Reporte: Exportación de un archivo PDF con formato profesional y descarga automática.

Requerimientos No Funcionales (RNF)

    RNF1 - Portabilidad: Diseñado para ejecutarse en entornos Google Colab.

    RNF2 - Integridad: Validación de existencia de archivos para evitar errores de ejecución (uso de os.path.exists).

    RNF3 - Modularidad: Código organizado bajo el paradigma POO (Clases y Métodos).

3. Arquitectura de Software
Diagrama de Casos de Uso

    Actor: Técnico de Mantenimiento.

    Acción Principal: Iniciar mantenimiento, completar checklist, adjuntar evidencia y generar reporte PDF.

4. Diseño del Sistema (POO)
Clases Principales

    Clase AireAcondicionado (Modelo de Datos):

        Propósito: Representa la entidad física del equipo.

        Atributos: Almacena tanto datos estáticos (Marca, Serie) como dinámicos (Filtros, Presión, Observaciones).

    Clase SistemaGestionMantenimiento (Lógica de Negocio):

        Propósito: Orquestador del sistema. Controla la interfaz de consola, la lectura/escritura de archivos y la construcción del PDF.

        Métodos Clave:

            cargar_datos() / guardar_datos(): Manejo de persistencia JSON.

            generar_pdf(): Construcción visual del reporte utilizando la librería reportlab.

            completar_mantenimiento(): Interfaz de usuario para el ingreso de datos técnicos.

Diagrama de Clases UML
5. Persistencia y Diccionario de Datos

Los datos se almacenan en un diccionario anidado en el archivo clientes_mantenimiento.json:
Campo	Tipo	Descripción
Cliente	String	Llave principal (Nombre del cliente/empresa).
Direcciones	Objeto	Contenedor de diferentes sedes del mismo cliente.
Equipos	Lista	Conjunto de objetos AireAcondicionado con sus datos técnicos.
6. Manual de Instalación y Uso
Requisitos Previos

Es necesario instalar las librerías de generación de PDF y manejo de imágenes:
Bash

!pip install reportlab pillow

Pasos para Ejecutar:

    Carga del Entorno: Ejecutar el script en una celda de Google Colab.

    Identificación: Ingresar los datos de la empresa, técnico y cliente.

    Pre-carga de Imágenes: Si se desea adjuntar fotos, seleccionar los archivos desde la computadora al inicio del programa.

    Carga de Equipos: El sistema preguntará si se desea usar equipos existentes para ese cliente o cargar nuevos sectores.

    Checklist: Responder a las preguntas de mantenimiento por cada equipo.

    Descarga: Al finalizar, el sistema generará y descargará automáticamente el archivo Reporte_Nombre_Sitio.pdf.

7. Conclusión

Este proyecto demuestra la aplicación práctica de la Programación Orientada a Objetos para resolver un problema real de gestión técnica. Se logra la separación de responsabilidades entre la entidad de datos y la lógica del sistema, garantizando un código escalable y mantenible.
