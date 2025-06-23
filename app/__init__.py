# app/__init__.py

from flask import Flask, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config
import os
from .config import Config
from .extensions import db, migrate, login_manager, socketio

# --- Extensiones ---
# Nota: SocketIO ya no se inicializa aquí.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# --- Factory de la Aplicación ---
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Inicializar extensiones con la app ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    # --- Configuraciones y Blueprints ---
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para continuar."
    login_manager.login_message_category = "warning"

    from app.models.usuario import Usuario
    from app.models.vendedor import Vendedor

    @login_manager.user_loader
    def load_user(user_id):
        if ':' in user_id:
            tipo, id_real = user_id.split(':', 1)
            if tipo == 'vendedor':
                return Vendedor.query.get(int(id_real))
        return Usuario.query.get(int(user_id))

    # Ruta para servir archivos subidos
    @app.route('/uploads/<path:filename>')
    def descargar_archivo_uploads(filename):
        uploads_path = os.path.join(current_app.root_path, 'uploads')
        return send_from_directory(uploads_path, filename)

    # Registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.vendedores import vendedores_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.productos import productos_bp
    from app.routes.pedidos import pedidos_bp
    from app.routes.extras import extras_bp
    from app.routes.devoluciones import devoluciones_bp
    from app.routes.ventas import ventas_bp
    from app.routes.despachos import despachos_bp
    from app.routes.reportes import reportes_bp
    from app.routes.festivos import festivos_bp
    from app.routes.liquidaciones import liquidaciones_bp
    from app.routes.cambios import cambios_bp
    from app.routes.reportes_liquidaciones import reportes_liquidaciones_bp
    from app.routes.canastas import bp_canastas
    from app.routes.movimientos import bp_movimientos
    from app.routes.configuracion import config_bp
    from app.routes.dialogflow_webhook import dialogflow_cx_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(vendedores_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(extras_bp)
    app.register_blueprint(devoluciones_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(despachos_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(festivos_bp)
    app.register_blueprint(liquidaciones_bp)
    app.register_blueprint(cambios_bp)
    app.register_blueprint(reportes_liquidaciones_bp, url_prefix='/reportes/liquidaciones')
    app.register_blueprint(bp_canastas)
    app.register_blueprint(bp_movimientos)
    app.register_blueprint(config_bp)
    app.register_blueprint(dialogflow_cx_bp, url_prefix="/")

    # Registrar comandos CLI personalizados
    from app.cli.root import crear_root
    from app.cli.mantenimiento import borrar_movimientos_canastas, borrar_canastas_total
    app.cli.add_command(crear_root)
    app.cli.add_command(borrar_movimientos_canastas)
    app.cli.add_command(borrar_canastas_total)

    return app
