"""
app/models/models.py
Autor: Jhon Alexander Rodriguez Redondo

Modelos de base de datos para el proyecto AutoSeguro360.
Modelo 1: Usuario
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ============================================================
# MODELO USUARIO
# ============================================================

class UsuarioBase(SQLModel):
    """
    Atributos base del Usuario.
    Esta clase NO tiene ID ni relaciones. Sirve como plantilla
    para los modelos de creación y lectura.
    """
    cedula: str = Field(index=True, unique=True, description="Cédula del usuario")
    nombre_completo: str = Field(description="Nombre completo del usuario")
    celular: str = Field(description="Número de contacto")
    email: str = Field(description="Correo electrónico del usuario")
    edad: int = Field(description="Edad del usuario en años")
    categoria_licencia: str = Field(description="Categoría de licencia (A1, B1, C1, etc.)")
    foto_perfil: Optional[str] = Field(default=None, description="Ruta/URL de la foto (opcional)")
    estado: bool = Field(default=True, description="Estado del usuario (activo/inactivo)")


class Usuario(UsuarioBase, table=True):
    """
    Modelo principal de Usuario que se guarda en la base de datos.
    Contiene: ID autoincremental y relaciones.
    """
    id: int = Field(default=None, primary_key=True)

    # Relaciones (se activarán cuando definamos Compra)
    compras: List["Compra"] = Relationship(back_populates="usuario")


class UsuarioCreate(UsuarioBase):
    """
    Modelo para creación de usuarios (POST).
    Hereda todos los atributos base excepto el ID.
    """
    pass


class UsuarioRead(UsuarioBase):
    """
    Modelo para lectura de información (respuesta en API).
    Incluye el ID generado.
    """
    id: int


# ============================================================
# MODELO VEHICULO
# ============================================================

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class VehiculoBase(SQLModel):
    """
    Atributos base del Vehículo.
    Se usa para los modelos de creación y lectura.
    """
    marca: str = Field(description="Marca del vehículo (Ej: Toyota)")
    linea: str = Field(description="Línea o referencia del vehículo (Ej: Corolla)")
    modelo: int = Field(description="Año modelo del vehículo")
    precio: float = Field(description="Precio del vehículo en pesos colombianos")
    nivel_seguridad: str = Field(description="Nivel de seguridad asignado según el análisis del sistema")
    placa: str = Field(index=True, unique=True, description="Placa del vehículo")
    foto: Optional[str] = Field(default=None, description="URL o ruta de la foto del vehículo")
    estado: bool = Field(default=True, description="True=activo, False=inactivo")


class Vehiculo(VehiculoBase, table=True):
    """
    Modelo principal de Vehículo almacenado en la base de datos.
    Contiene ID y relaciones con otros modelos.
    """
    id: int = Field(default=None, primary_key=True)

    # Relación 1:1 con Ficha Técnica
    ficha_tecnica: Optional["FichaTecnica"] = Relationship(
        back_populates="vehiculo",
        sa_relationship_kwargs={"uselist": False}
    )

    # Relación 1:N con Compra
    compras: List["Compra"] = Relationship(back_populates="vehiculo")


class VehiculoCreate(VehiculoBase):
    """
    Modelo para creación de vehículos (POST).
    """
    pass


class VehiculoRead(VehiculoBase):
    """
    Modelo para respuesta de lectura (GET).
    """
    id: int



# ============================================================
# MODELO FICHA TÉCNICA
# ============================================================

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class FichaTecnicaBase(SQLModel):
    """
    Atributos base de la ficha técnica.
    Se usa para creación y lectura.
    """
    marca: str = Field(description="Marca del vehículo")
    linea: str = Field(description="Línea o referencia del vehículo")
    modelo: int = Field(description="Año modelo del vehículo")
    cilindraje: Optional[int] = Field(default=None, description="Cilindraje del motor en cc")
    color: Optional[str] = Field(default=None, description="Color principal del vehículo")
    tipo_servicio: Optional[str] = Field(default=None, description="Tipo de servicio: particular, público, etc.")
    tipo_carroceria: Optional[str] = Field(default=None, description="Carrocería: sedan, hatchback, suv, etc.")
    clase_vehiculo: Optional[str] = Field(default=None, description="Automóvil, camioneta, motocicleta, etc.")
    combustible: Optional[str] = Field(default=None, description="Tipo de combustible: gasolina, diésel, híbrido")
    capacidad: Optional[int] = Field(default=None, description="Número de pasajeros")
    potencia_hp: Optional[int] = Field(default=None, description="Potencia del motor en caballos de fuerza (HP)")


class FichaTecnica(FichaTecnicaBase, table=True):
    """
    Ficha Técnica almacenada en la base de datos.
    Relación 1:1 con Vehículo.
    """
    id: int = Field(default=None, primary_key=True)

    # Relación uno a uno con Vehículo
    vehiculo_id: int = Field(foreign_key="vehiculo.id", unique=True, index=True)
    vehiculo: "Vehiculo" = Relationship(back_populates="ficha_tecnica")


class FichaTecnicaCreate(FichaTecnicaBase):
    """
    Modelo para creación de ficha técnica.
    El vehiculo_id se pasa desde el endpoint.
    """
    vehiculo_id: int


class FichaTecnicaRead(FichaTecnicaBase):
    """
    Modelo para lectura de ficha técnica.
    """
    id: int
    vehiculo_id: int



# ============================================================
# MODELO COMPRA
# ============================================================

from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class CompraBase(SQLModel):
    """
    Campos base para la entidad Compra.
    Representa una transacción entre un usuario y un vehículo.
    """

    precio: float = Field(description="Precio final al momento de la compra")
    tipo_pago: str = Field(description="Método de pago: efectivo, crédito, transferencia, etc.")
    estado: str = Field(
        default="completada",
        description="Estado de la compra: completada, pendiente, cancelada"
    )


class Compra(CompraBase, table=True):
    """
    Modelo principal almacenado en la base de datos.
    Relacionado con Usuario y Vehículo.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_compra: datetime = Field(default_factory=datetime.utcnow)

    # Relación con Usuario
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    usuario: "Usuario" = Relationship(back_populates="compras")

    # Relación con Vehículo
    vehiculo_id: int = Field(foreign_key="vehiculo.id", index=True)
    vehiculo: "Vehiculo" = Relationship(back_populates="compras")


class CompraCreate(CompraBase):
    """
    Modelo para creación de una compra.
    El usuario_id y vehiculo_id se envían en la solicitud.
    """
    usuario_id: int
    vehiculo_id: int


class CompraRead(CompraBase):
    """
    Modelo para lectura de compra (respuesta en endpoints).
    """
    id: int
    fecha_compra: datetime
    usuario_id: int
    vehiculo_id: int
