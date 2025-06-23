# app/routes/socket_events.py

from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.extensions import socketio

socketio_bp = Blueprint("socketio", __name__)

# Diccionario para mapear session_id (de Dialogflow CX) a socket_id
session_to_socket = {}

@socketio.on('connect')
def on_connect():
    print(f"📡 Cliente conectado vía Socket.IO con socket_id: {request.sid}")

@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 Cliente desconectado: socket_id={request.sid}")
    
    # Eliminar session_id vinculado a este socket_id
    session_id_a_eliminar = None
    for sid, sock_id in session_to_socket.items():
        if sock_id == request.sid:
            session_id_a_eliminar = sid
            break
    if session_id_a_eliminar:
        leave_room(session_id_a_eliminar)
        del session_to_socket[session_id_a_eliminar]
        print(f"🗑️ Session eliminada: {session_id_a_eliminar}")

@socketio.on('registrar_socket')
def registrar_socket(data):
    session_id = data.get("session_id")
    if session_id:
        session_to_socket[session_id] = request.sid
        join_room(session_id)
        print(f"✅ Socket registrado para session_id: {session_id} con socket_id: {request.sid}")
    else:
        print("⚠️ No se proporcionó session_id al registrar socket.")

