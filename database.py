from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./flota.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TipoMantenimiento(str, enum.Enum):
    ACEITE = "Cambio de Aceite"
    FILTRO_ACEITE = "Filtro de Aceite"
    FILTRO_AIRE = "Filtro de Aire"
    FILTRO_COMBUSTIBLE = "Filtro de Combustible"
    FILTRO_HIDRAULICO = "Filtro Hidráulico"
    PIEZA = "Cambio de Pieza"
    REVISION = "Revisión General"
    OTRO = "Otro"


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    patente = Column(String(20), unique=True, nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    anio = Column(Integer, nullable=False)
    km_actual = Column(Float, default=0)
    notas = Column(Text, default="")
    tipo_vehiculo = Column(String(20), default="")
    itv_vencimiento = Column(Date, nullable=True)
    tacografo_vencimiento = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mantenimientos = relationship("Mantenimiento", back_populates="vehiculo", cascade="all, delete-orphan")


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    tipo = Column(String(50), nullable=False)
    descripcion = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)
    km_en_servicio = Column(Float, nullable=False)
    proximo_km_intervalo = Column(Float, nullable=True)
    proxima_fecha = Column(Date, nullable=True)
    costo = Column(Float, default=0)
    notas = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    vehiculo = relationship("Vehiculo", back_populates="mantenimientos")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE vehiculos ADD COLUMN tipo_vehiculo VARCHAR(20) DEFAULT ''"))
            conn.commit()
        except Exception:
            pass