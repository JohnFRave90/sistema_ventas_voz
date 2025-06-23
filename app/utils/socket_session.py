# app/utils/socket_session.py

# Diccionario en memoria: { session_id_dialogflow: socket_id_flask }
socket_mapping = {}

def registrar_socket(session_id, socket_id):
    print(f"[🧠 Asociación] Guardando socket_id {socket_id} para sesión {session_id}")
    socket_mapping[session_id] = socket_id

def obtener_socket(session_id):
    return socket_mapping.get(session_id)
