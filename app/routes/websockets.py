# app/routes/websockets.py

def register_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado al WebSocket')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado del WebSocket')