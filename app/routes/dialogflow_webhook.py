# app/routes/dialogflow_webhook.py

from flask import Blueprint, request, jsonify
from app.extensions import socketio, db # <--- IMPORTAMOS DESDE extensions.py
from app.models.pedidos import BDPedido
from app.models.extras import BDExtra
from app.models.vendedor import Vendedor
from app.models.producto import Producto
import locale
import json

dialogflow_bp = Blueprint("dialogflow", __name__)

def buscar_documento(tipo_doc, consecutivo):
    if not tipo_doc or not consecutivo: return None
    if tipo_doc.lower() == 'pedido':
        return BDPedido.query.filter_by(consecutivo=consecutivo).first()
    elif tipo_doc.lower() == 'extra':
        return BDExtra.query.filter_by(consecutivo=consecutivo).first()
    return None

@dialogflow_bp.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("--- EJECUTANDO VERSIÓN DE CÓDIGO FINAL ---")
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except locale.Error:
            try: locale.setlocale(locale.LC_TIME, 'Spanish')
            except locale.Error: print("ADVERTENCIA: No se pudo establecer el locale a español.")

        req = request.get_json(silent=True, force=True)
        
        # Limpiamos y normalizamos el nombre del intent
        intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "").strip().lower()
        
        print(f"🎯 Intent detectado (limpio): '{intent_name}'")
        
        if intent_name == "creardespacho":
            print("✅ Lógica para 'creardespacho' iniciada.")
            params = req.get("queryResult", {}).get("parameters", {})
            tipo_doc = params.get("tipo_documento")
            numero_doc = params.get("number")

            if not tipo_doc or numero_doc is None:
                return jsonify({"fulfillmentText": "No entendí bien. Por favor, dime si es un pedido o un extra y qué número tiene."})

            prefix = "PD-" if tipo_doc.lower() == 'pedido' else "EX-"
            consecutivo = f"{prefix}{int(numero_doc):05d}"
            
            documento = buscar_documento(tipo_doc, consecutivo)
            vendedor = Vendedor.query.filter_by(codigo_vendedor=documento.codigo_vendedor).first()
            nombre_vendedor = vendedor.nombre if vendedor else f"código {documento.codigo_vendedor}"
            fecha_formateada = documento.fecha.strftime('%d de %B de %Y')

            if documento:
                url_despacho = f"/despachos/crear/{consecutivo}"
                socketio.emit('abrir_pagina', {'url': url_despacho})
                mensaje_respuesta = f"Entendido, preparando el despacho para el {tipo_doc}  {consecutivo} del vendedor {nombre_vendedor} del día {fecha_formateada}."
                return jsonify({"fulfillmentText": mensaje_respuesta})
            else:
                mensaje_respuesta = f"No pude encontrar el {tipo_doc} con el número {int(numero_doc)}."
                return jsonify({"fulfillmentText": mensaje_respuesta})

        elif intent_name == "dictarproducto":
            # ... (la lógica para este intent se mantiene) ...
            return jsonify({"fulfillmentText": "Lógica de dictado pendiente."})

        else:
            print(f"❓ Intent no manejado: '{intent_name}'")
            return jsonify({"fulfillmentText": "No he entendido esa orden, por favor, prueba de nuevo."})

    except Exception as e:
        print(f"❌ Error fatal en webhook: {e}")
        return jsonify({"fulfillmentText": "Lo siento, ocurrió un error interno en el servidor."})