PROYECTO AUTOSEGURO360 - API Avanzada de Gestión y Multimedia

Resumen del Proyecto

AutoSeguro360 es una aplicación web de gestión de vehículos y usuarios construida sobre una arquitectura moderna y escalable. Utiliza FastAPI como backend asíncrono y SQLModel para la persistencia de datos, demostrando la integración de servicios en la nube (Supabase Storage) para el manejo de archivos multimedia y el despliegue de un frontend completo con Jinja2.

El sistema prioriza la viabilidad comercial al implementar un catálogo de vehículos filtrable y formularios de transacciones que garantizan la integridad de los datos.

- Arquitectura y Stack Tecnológico

Componente

Herramienta/Tecnología

Propósito en el Proyecto

Backend (API)

FastAPI (Python)

Manejo asíncrono de peticiones HTTP, validación y lógica de negocio.

Bases de Datos

SQLModel / SQLite

Persistencia de datos relacionales y gestión de los 4 modelos de negocio.

Multimedia (Nube)

Supabase Storage

Almacenamiento de archivos binarios (fotos de perfil y vehículos).

Frontend

HTML5 / CSS3 / Jinja2

Creación de una interfaz web con estilos avanzados (Punto I, K).

Manejo de Formularios

Form() & UploadFile

Procesamiento robusto de datos (texto y archivos multimedia) desde el frontend.

- Modelos de Negocio (4 Entidades + Relaciones)

El proyecto utiliza 4 modelos principales, todos con operaciones CRUD (Crear, Leer, Actualizar, Eliminar) implementadas y con la función de eliminación suave (Soft Delete) para el histórico de datos.

Usuario (PK: Cédula, str): Datos personales, incluyendo categoria_licencia y la URL de la foto_perfil_url.

Vehiculo (PK: Placa, str): Datos comerciales y URL de foto_url.

FichaTecnica: Especificaciones detalladas del vehículo (cilindraje, color, potencia, etc.).

Compra: Registro de transacciones históricas de compra/venta.

Relaciones (Punto A, G)

Relación

Entidades

Clave

Cumplimiento

1:1

Vehiculo $\leftrightarrow$ FichaTecnica

vehiculo_placa (PK/FK)

Cada vehículo tiene una sola ficha técnica.

1:N

Usuario $\rightarrow$ Vehiculo

propietario_cedula (FK)

Un usuario puede ser propietario de N vehículos.

N:M

Usuario $\leftrightarrow$ Vehiculo

Vía Compra

Un vehículo puede ser vendido/comprado por muchos usuarios a lo largo del tiempo.

- Funcionalidades Avanzadas Implementadas

1. Gestión de Multimedia en la Nube (Punto H)

Integración directa con Supabase Storage.

Los formularios de registro de Usuario y Vehículo reciben un archivo (UploadFile).

El backend sube el archivo al bucket configurado de Supabase y guarda la URL pública resultante en la base de datos (campo foto_perfil_url o foto_url).

2. Navegación y Usabilidad (Punto D, I, J, N)

Inicio HTML: La aplicación arranca directamente sirviendo el index.html vía Jinja2 Templates (Punto D).

Formularios Funcionales: Los registros de Usuario y Vehículo utilizan formularios HTML (method="POST", enctype="multipart/form-data") para el ingreso de datos (Punto J).

Respuestas HTML: Las confirmaciones de registro son páginas HTML con estilos consistentes (registro_exitoso.html), no solo respuestas JSON (Punto I).

Catálogo Dinámico: La página principal muestra un catálogo generado dinámicamente ({% for vehiculo in vehicles %}) con datos obtenidos de la base de datos.

Buscador Avanzado (Punto N): La ruta raíz (/) acepta parámetros de búsqueda GET para filtrar el catálogo por:

Entrada de texto libre (busqueda_texto en Marca o Línea).

Año de modelo (anio_filtro).

Nivel de Seguridad NCAP mínimo (ncap_filtro).

Precio máximo (precio_max).

3. Viabilidad y Persistencia

Eliminación Segura: El Soft Delete (estado: bool) permite el control de registros para fines de auditoría e histórico.

Integridad de Transacción: El registro de Compra valida que tanto la Cédula del comprador como la Placa del vehículo existan y estén activos antes de registrar la transacción, garantizando la lógica de negocio.

- Configuración y Ejecución

Requisitos

fastapi
sqlmodel
uvicorn
jinja2
python-multipart
supabase


Setup Inicial

Estructura: Asegúrese de tener la siguiente estructura de carpetas:

.
├── main.py
├── models.py
├── database.py
├── templates/
│   ├── index.html
│   ├── registro_usuario.html
│   └── ... (otros templates)
└── static/
    └── style.css


Base de Datos/Supabase:

Reemplace SUPABASE_URL y SUPABASE_ANON_KEY en main.py con sus credenciales reales.

Configure la política de Storage (Almacenamiento) de Supabase para permitir la subida (INSERT) a la clave anónima (anon) para el bucket llamado perfiles.

Ejecución

Ejecute la aplicación desde la carpeta raíz:

uvicorn main:app --reload


Acceda a la aplicación en el navegador: http://127.0.0.1:8000/