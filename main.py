from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
import uvicorn
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature

from database import get_db, init_db, Vehiculo, Mantenimiento, TipoMantenimiento

SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
APP_USER = os.environ.get("APP_USER", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "admin")
_signer = URLSafeTimedSerializer(SECRET_KEY)


def get_session(session: Optional[str] = Cookie(default=None)):
    if not session:
        return None
    try:
        return _signer.loads(session, max_age=60 * 60 * 24 * 30)
    except BadSignature:
        return None


def require_auth(session=Depends(get_session)):
    if session is None:
        raise HTTPException(status_code=307, headers={"Location": "/login"})
    return session

app = FastAPI(title="Control de Flota")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def calcular_alertas(vehiculos: list, db: Session):
    alertas = []
    for v in vehiculos:
        ultimos = {}
        for m in sorted(v.mantenimientos, key=lambda x: x.fecha):
            ultimos[m.tipo] = m

        for tipo, m in ultimos.items():
            estado = None
            motivo = ""

            if m.proxima_fecha:
                dias_restantes = (m.proxima_fecha - date.today()).days
                if dias_restantes < 0:
                    estado = "danger"
                    motivo = f"Vencido por fecha ({abs(dias_restantes)} días de atraso)"
                elif dias_restantes <= 15:
                    estado = "warning"
                    motivo = f"Vence en {dias_restantes} días ({m.proxima_fecha})"

            if m.proximo_km_intervalo:
                km_proximo = m.km_en_servicio + m.proximo_km_intervalo
                km_diff = km_proximo - v.km_actual
                if km_diff <= 0:
                    if estado != "danger":
                        estado = "danger"
                        motivo = f"Vencido por km (hace {abs(int(km_diff))} km)"
                elif km_diff <= 500:
                    if estado != "danger":
                        estado = "warning"
                        motivo = f"Próximo en {int(km_diff)} km (a {int(km_proximo)} km)"

            if estado:
                alertas.append({
                    "vehiculo": v,
                    "tipo": tipo,
                    "estado": estado,
                    "motivo": motivo,
                    "ultimo_servicio": m.fecha,
                })
    return alertas


@app.on_event("startup")
def startup():
    init_db()


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, session=Depends(get_session)):
    if session:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == APP_USER and password == APP_PASSWORD:
        token = _signer.dumps(username)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("session", token, httponly=True, max_age=60 * 60 * 24 * 30)
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Usuario o contraseña incorrectos",
    })


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    vehiculos = db.query(Vehiculo).all()
    alertas = calcular_alertas(vehiculos, db)
    alertas_danger = [a for a in alertas if a["estado"] == "danger"]
    alertas_warning = [a for a in alertas if a["estado"] == "warning"]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "vehiculos": vehiculos,
        "alertas_danger": alertas_danger,
        "alertas_warning": alertas_warning,
        "total_vehiculos": len(vehiculos),
    })


# ─── Vehículos ───────────────────────────────────────────────────────────────

@app.get("/vehiculos", response_class=HTMLResponse)
def listar_vehiculos(request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    vehiculos = db.query(Vehiculo).all()
    return templates.TemplateResponse("vehiculos.html", {
        "request": request,
        "vehiculos": vehiculos,
    })


@app.get("/vehiculos/nuevo", response_class=HTMLResponse)
def nuevo_vehiculo_form(request: Request, auth=Depends(require_auth)):
    return templates.TemplateResponse("form_vehiculo.html", {
        "request": request,
        "vehiculo": None,
        "accion": "Agregar",
    })


@app.post("/vehiculos/nuevo")
def crear_vehiculo(
    request: Request,
    patente: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    anio: int = Form(...),
    km_actual: float = Form(...),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    auth=Depends(require_auth),
):
    existente = db.query(Vehiculo).filter(Vehiculo.patente == patente.upper()).first()
    if existente:
        return templates.TemplateResponse("form_vehiculo.html", {
            "request": request,
            "vehiculo": None,
            "accion": "Agregar",
            "error": f"Ya existe un vehículo con la patente {patente.upper()}",
        })
    v = Vehiculo(
        patente=patente.upper(),
        marca=marca,
        modelo=modelo,
        anio=anio,
        km_actual=km_actual,
        notas=notas,
    )
    db.add(v)
    db.commit()
    return RedirectResponse(url="/vehiculos", status_code=303)


@app.get("/vehiculos/{vid}", response_class=HTMLResponse)
def detalle_vehiculo(vid: int, request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    mantenimientos = sorted(v.mantenimientos, key=lambda x: x.fecha, reverse=True)

    ultimos = {}
    for m in sorted(v.mantenimientos, key=lambda x: x.fecha):
        ultimos[m.tipo] = m
    alertas = calcular_alertas([v], db)

    return templates.TemplateResponse("vehiculo_detalle.html", {
        "request": request,
        "vehiculo": v,
        "mantenimientos": mantenimientos,
        "alertas": alertas,
        "tipos": [t.value for t in TipoMantenimiento],
    })


@app.get("/vehiculos/{vid}/editar", response_class=HTMLResponse)
def editar_vehiculo_form(vid: int, request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return templates.TemplateResponse("form_vehiculo.html", {
        "request": request,
        "vehiculo": v,
        "accion": "Editar",
    })


@app.post("/vehiculos/{vid}/editar")
def editar_vehiculo(
    vid: int,
    marca: str = Form(...),
    modelo: str = Form(...),
    anio: int = Form(...),
    km_actual: float = Form(...),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    auth=Depends(require_auth),
):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    v.marca = marca
    v.modelo = modelo
    v.anio = anio
    v.km_actual = km_actual
    v.notas = notas
    db.commit()
    return RedirectResponse(url=f"/vehiculos/{vid}", status_code=303)


@app.post("/vehiculos/{vid}/eliminar")
def eliminar_vehiculo(vid: int, db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    db.delete(v)
    db.commit()
    return RedirectResponse(url="/vehiculos", status_code=303)


# ─── Mantenimientos ──────────────────────────────────────────────────────────

@app.get("/vehiculos/{vid}/mantenimiento/nuevo", response_class=HTMLResponse)
def nuevo_mantenimiento_form(vid: int, request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return templates.TemplateResponse("form_mantenimiento.html", {
        "request": request,
        "vehiculo": v,
        "tipos": [t.value for t in TipoMantenimiento],
        "hoy": date.today().isoformat(),
        "mantenimiento": None,
    })


@app.post("/vehiculos/{vid}/mantenimiento/nuevo")
def crear_mantenimiento(
    vid: int,
    tipo: str = Form(...),
    descripcion: str = Form(...),
    fecha: date = Form(...),
    km_en_servicio: float = Form(...),
    proximo_km_intervalo: Optional[float] = Form(None),
    proxima_fecha: Optional[date] = Form(None),
    costo: float = Form(0),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    auth=Depends(require_auth),
):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    if km_en_servicio > v.km_actual:
        v.km_actual = km_en_servicio

    m = Mantenimiento(
        vehiculo_id=vid,
        tipo=tipo,
        descripcion=descripcion,
        fecha=fecha,
        km_en_servicio=km_en_servicio,
        proximo_km_intervalo=proximo_km_intervalo if proximo_km_intervalo else None,
        proxima_fecha=proxima_fecha,
        costo=costo,
        notas=notas,
    )
    db.add(m)
    db.commit()
    return RedirectResponse(url=f"/vehiculos/{vid}", status_code=303)


@app.get("/vehiculos/{vid}/mantenimiento/{mid}/editar", response_class=HTMLResponse)
def editar_mantenimiento_form(vid: int, mid: int, request: Request, db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mid, Mantenimiento.vehiculo_id == vid).first()
    if not v or not m:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("form_mantenimiento.html", {
        "request": request,
        "vehiculo": v,
        "tipos": [t.value for t in TipoMantenimiento],
        "hoy": date.today().isoformat(),
        "mantenimiento": m,
    })


@app.post("/vehiculos/{vid}/mantenimiento/{mid}/editar")
def editar_mantenimiento(
    vid: int,
    mid: int,
    tipo: str = Form(...),
    descripcion: str = Form(...),
    fecha: date = Form(...),
    km_en_servicio: float = Form(...),
    proximo_km_intervalo: Optional[float] = Form(None),
    proxima_fecha: Optional[date] = Form(None),
    costo: float = Form(0),
    notas: str = Form(""),
    db: Session = Depends(get_db),
    auth=Depends(require_auth),
):
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mid, Mantenimiento.vehiculo_id == vid).first()
    if not m:
        raise HTTPException(status_code=404)
    m.tipo = tipo
    m.descripcion = descripcion
    m.fecha = fecha
    m.km_en_servicio = km_en_servicio
    m.proximo_km_intervalo = proximo_km_intervalo if proximo_km_intervalo else None
    m.proxima_fecha = proxima_fecha
    m.costo = costo
    m.notas = notas
    db.commit()
    return RedirectResponse(url=f"/vehiculos/{vid}", status_code=303)


@app.post("/vehiculos/{vid}/mantenimiento/{mid}/eliminar")
def eliminar_mantenimiento(vid: int, mid: int, db: Session = Depends(get_db), auth=Depends(require_auth)):
    m = db.query(Mantenimiento).filter(Mantenimiento.id == mid, Mantenimiento.vehiculo_id == vid).first()
    if not m:
        raise HTTPException(status_code=404)
    db.delete(m)
    db.commit()
    return RedirectResponse(url=f"/vehiculos/{vid}", status_code=303)


# ─── Actualizar km ────────────────────────────────────────────────────────────

@app.post("/vehiculos/{vid}/actualizar-km")
def actualizar_km(vid: int, km_actual: float = Form(...), db: Session = Depends(get_db), auth=Depends(require_auth)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vid).first()
    if not v:
        raise HTTPException(status_code=404)
    v.km_actual = km_actual
    db.commit()
    return RedirectResponse(url=f"/vehiculos/{vid}", status_code=303)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
