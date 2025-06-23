# app/routes/dialogflow_webhook_cx.py

from flask import Blueprint, request, jsonify, session
from app.extensions import db, socketio
from app.models.usuario import Usuario
from app.models.pedidos import BDPedido
from app.models.extras import BDExtra
from app.models.producto import Producto
from app.models.despachos import BDDespacho
from datetime import datetime

dialogflow_cx_bp = Blueprint("dialogflow_cx", __name__)

# Memoria temporal por sesión
session_data = {}

@dialogflow_cx_bp.route("/webhook", methods=["POST"])
def webhook_cx():
    req = request.get_json()
    tag = req.get("fulfillmentInfo", {}).get("tag", "")
    session_id = req.get("sessionInfo", {}).get("session", "").split("/")[-1]
    params = req.get("sessionInfo", {}).get("parameters", {})

    print(f"🎯 Tag recibido: {tag}")
    print("[📦 Parámetros crudos recibidos]", params)


    # 🟢 INICIAR SESIÓN
    if tag == "iniciar_sesion":
        usuario_param = params.get("usuarios", "")
        pin_param = params.get("pin", "")

        # Extraer nombre desde string o diccionario de Dialogflow CX
        nombre = ""
        if isinstance(usuario_param, dict):
            nombre = usuario_param.get("original", "")
        else:
            nombre = usuario_param

        nombre = str(nombre).strip().lower()
        pin = str(int(pin_param)) if isinstance(pin_param, (int, float)) else str(pin_param).strip()

        print(f"[🔐 Login attempt] nombre_usuario='{nombre}', pin='{pin}'")

        usuario = Usuario.query.filter(db.func.lower(Usuario.nombre_usuario) == nombre).first()

        if not usuario:
            return responder(f"No encontré ningún usuario llamado {nombre}. ¿Lo puedes repetir?")

        if not usuario.check_pin(pin):
            return responder(f"El PIN ingresado no es correcto para {nombre}. Intenta nuevamente.")

        # Guardar datos de sesión
        session_data[session_id] = {
            "usuario_id": usuario.id,
            "nombre": usuario.nombre_usuario,
            "productos": [],
            "timestamp": datetime.utcnow()
        }

        return responder(f"Hola {usuario.nombre_usuario}, ya puedes comenzar a dictar tu pedido.")

    # 🟢 CREAR DESPACHO
    if tag == "crear_despacho":
        tipo = params.get("tipo_documento", "").lower()
        numero = params.get("numero")

        if tipo not in ["pedido", "extra"] or not numero:
            return responder("Faltan datos. ¿Es un pedido o un extra, y qué número tiene?")

        prefix = "PD-" if tipo == "pedido" else "EX-"
        consecutivo = f"{prefix}{int(numero):05d}"

        documento = BDPedido.query.filter_by(consecutivo=consecutivo).first() if tipo == "pedido" else BDExtra.query.filter_by(consecutivo=consecutivo).first()
        if not documento:
            return responder(f"No encontré el {tipo} con número {numero}.")

        despacho_existente = BDDespacho.query.filter_by(codigo_origen=consecutivo).first()
        if despacho_existente:
            url = f"/despachos/editar/{despacho_existente.id}"
            socketio.emit("abrir_pagina", {"url": url}, room=session_id)
            return responder(f"Ya existe un despacho para el {tipo} {consecutivo}. Abriendo edición.")

        url = f"/despachos/crear/{consecutivo}"
        socketio.emit("abrir_pagina", {"url": url}, room=session_id)
        return responder(f"Preparando despacho para el {tipo} {consecutivo}.")

    # 🟢 DICTAR PRODUCTO
    if tag == "dictar_producto":
        nombre_prod = params.get("producto", "").strip()
        cantidad = params.get("cantidad", 0)
        lote = str(params.get("lote", "")).strip()

        producto = Producto.query.filter(
            (Producto.nombre.ilike(nombre_prod)) | (Producto.codigo.ilike(nombre_prod))
        ).first()

        if not producto:
            return responder(f"No encontré el producto {nombre_prod}. Intenta de nuevo.")

        # Asegura estructura válida de sesión
        if session_id not in session_data:
            session_data[session_id] = {
                "productos": [],
                "timestamp": datetime.utcnow()
            }
        elif "productos" not in session_data[session_id]:
            session_data[session_id]["productos"] = []

        nuevo = {
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "cantidad": cantidad,
            "lote": lote
        }

        # Agregar y emitir al frontend
        session_data[session_id]["productos"].append(nuevo)
        socketio.emit("producto_dictado", {"producto": nuevo}, room=session_id)

        return responder(f"Agregado {cantidad} unidades de {producto.nombre} del lote {lote}.")

    # 🟢 CONFIRMAR DESPACHO
    if tag == "confirmar_despacho":
        if session_id not in session_data or not session_data[session_id].get("productos"):
            return responder("No hay productos para guardar. Dicta al menos uno.")

        resumen = "\n".join([
            f"- {p['cantidad']} de {p['nombre']} (lote {p['lote']})"
            for p in session_data[session_id]["productos"]
        ])

        return responder(f"¿Confirmas guardar este despacho con:\n{resumen}?")

    # 🟢 CERRAR SESIÓN
    if tag == "cerrar_sesion":
        session_data.pop(session_id, None)
        return responder("Sesión finalizada. Hasta luego.")

    # ❓ DESCONOCIDO
    return responder("No entendí la instrucción.")

# 🟢 FUNCION UTILITARIA DE RESPUESTA
def responder(mensaje):
    return jsonify({
        "fulfillment_response": {
            "messages": [{"text": {"text": [mensaje]}}]
        }
    })
