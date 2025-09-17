from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Schemas.Activos.consultar_activo import ConsultarActivo
from Schemas.Activos.retirar_activo import RetirarActivo
from Schemas.Activos.guardar_activo import GuardarActivo
from Schemas.Activos.actualizar_activo import ActualizarActivo
from Schemas.Activos.consultar_historial import ConsultarHistorial
from Schemas.Activos.activos_x_tercero import ActivosXtercero
from Class.Pedidos import Pedidos
from Utils.decorator import http_decorator
from Config.db import get_db

pedidos_router = APIRouter()

@pedidos_router.post('/consultar_pedido', tags=["Pedidos"], response_model=dict)
@http_decorator
def consultar_pedido(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).consultar_pedido(data)
    return response

@pedidos_router.post('/actualizar_registros', tags=["Pedidos"], response_model=dict)
@http_decorator
def actualizar_registros(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).actualizar_registros(data)
    return response

@pedidos_router.post('/actualizar_registro_individual', tags=["Pedidos"], response_model=dict)
@http_decorator
def actualizar_registro_individual(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).actualizar_registro_individual(data)
    return response

@pedidos_router.post('/consultar_pedido_cabecera', tags=["Pedidos"], response_model=dict)
@http_decorator
def consultar_pedido_cabecera(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).consultar_pedido_cabecera(data)
    return response

@pedidos_router.post('/actualizar_documento', tags=["Pedidos"], response_model=dict)
@http_decorator
def actualizar_documento(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).actualizar_documento(data)
    return response

@pedidos_router.post('/consultar_remision_factura', tags=["Pedidos"], response_model=dict)
@http_decorator
def consultar_remision_factura(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).consultar_remision_factura(data)
    return response

@pedidos_router.post('/adicionar_pedido_oc', tags=["Pedidos"], response_model=dict)
@http_decorator
def adicionar_pedido_oc(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Pedidos(db).adicionar_pedido_oc(data)
    return response
