<<<<<<< HEAD
# PROJECT-1.2---SOFTWARE-DEVELOPMENT-AUTOSEGURO360-
AutoSeguro360 es una aplicación desarrollada con FastAPI y SQLModel que permite gestionar la información de vehículos dentro de un concesionario, enfocándose especialmente en la seguridad vial.
=======
    PROYECTO AUTOSEGURO360 - API de Gestión de Vehículos y Usuarios

    - Descripción detallada del Proyecto.  
- Autor: Jhon Alexander Rodriguez Redondo  
- Institución: Universidad Católica de Colombia  
- Contacto: jarodriguez83@ucatolica.edu.co

**AutoSeguro360** es una API desarrollada con **FastAPI** y **SQLModel (SQLite)** para la gestión y seguimiento de usuarios y vehículos. Este proyecto implementa una arquitectura que usando identificadores únicos del mundo real (Cédula y Placa) y mantiene un **histórico de datos** mediante el uso de la técnica de Soft Delete.

    - Características Principales

**1. Sistema de Identificación Única**
El sistema utiliza identificadores únicos e irrepetibles basados en documentos y matrículas, simplificando la lógica de negocio:
- **Usuarios:** Identificados por su **Cédula**, la cual es la Clave Primaria (PK).
- **Vehículos:** Identificados por su **Placa**, la cual es la Clave Primaria (PK).

**2. Gestión de Licencias de Conducción**
- Al crear un usuario, se solicita la **Categoría de Licencia**.
- Si el usuario no posee licencia, el campo se establece en el valor por defecto `"0"`.

**3. Histórico de Datos (Soft Delete)**
- La eliminación de registros (usuarios o vehículos) no es física, sino lógica.
- El campo **`estado: bool`** se establece en `False`, manteniendo el registro en la base de datos junto con la marca de tiempo.

**4. Funcionalidades de Búsqueda y Filtrado**
La API ofrece *endpoints* especializados para la consulta de datos:
- **Búsqueda por Licencia:** Permite listar usuarios activos que poseen una categoría de licencia específica (ej., buscar todos los usuarios con licencia "B1").
- **Filtro por Atributo:** Permite filtrar vehículos por su año de fabricación.
- **Búsqueda por Modelo:** Permite buscar vehículos por una coincidencia parcial en el nombre del modelo.

    - Diagrama de Clases (Relaciones de la Base de Datos).

El sistema utiliza tres entidades principales que se relacionan de la siguiente manera:

1.  **Relación 1:N (Uno a Muchos):**
    * **`Usuario`** -> **`Vehiculo`**. Un usuario puede ser el propietario de muchos vehículos. La clave foránea es `propietario_cedula` en la tabla `Vehiculo`.

2.  **Relación N:M (Muchos a Muchos):**
    * **`Vehiculo`** <-> **`DetalleSeguroVehiculo`**. Un vehículo puede tener muchos detalles de seguro/documentación (SOAT, TecnoMecánica, etc.), y cada tipo de detalle aplica a muchos vehículos. La tabla **`DetalleSeguroVehiculo`** actúa como enlace.

    - Cómo Ejecutar el Proyecto

1.  **Clonar el repositorio** (o crear los archivos `main.py`, `models.py`, `database.py` en una sola carpeta).
2.  **Instalar dependencias:**
    ```bash
    pip install fastapi "sqlmodel[sqlite]" 
    ```
3.  **Asegurar una base de datos limpia:** 
4.  **Ejecutar el servidor:**

    - Endpoints Clave

La documentación interactiva de todos los *endpoints* está disponible en: `http://127.0.0.1:8000/docs`

| Método | Ruta | Función Principal | ID Utilizado |
| :---: | :--- | :--- | :--- |
| **POST** | `/usuarios/` | Crear Usuario | Cédula (`PK`) |
| **GET** | `/usuarios/{cedula}` | Consultar por Cédula | Cédula (`str`) |
| **GET** | `/usuarios/busqueda/licencia/{categoria}` | Buscar por Categoría de Licencia | Categoría (`str`) |
| **POST** | `/vehiculos/` | Crear Vehículo | Placa (`PK`) |
| **GET** | `/vehiculos/{placa}` | Consultar por Placa | Placa (`str`) |
| **DELETE** | `/vehiculos/{placa}` | Eliminar (Soft Delete) | Placa (`str`) |
<<<<<<< HEAD
>>>>>>> 1b69218 (PROYECT)
=======

>>>>>>> 59e21bf (PROJECT SOFTWARE)
