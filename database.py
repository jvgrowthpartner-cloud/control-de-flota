from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

_db_path = os.environ.get("DATA_DIR", ".") + "/flota.db"
DATABASE_URL = f"sqlite:///{_db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
        for col_def in ["itv_vencimiento DATE", "tacografo_vencimiento DATE"]:
            try:
                conn.execute(text(f"ALTER TABLE vehiculos ADD COLUMN {col_def}"))
                conn.commit()
            except Exception:
                pass
