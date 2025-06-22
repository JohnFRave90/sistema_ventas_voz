from app import db

class BDPedido(db.Model):
    __tablename__ = 'bd_pedidos'

    id               = db.Column(db.Integer, primary_key=True)
    consecutivo      = db.Column(db.String(20), unique=True, nullable=False)
    codigo_vendedor  = db.Column(db.String(20), nullable=False)
    fecha            = db.Column(db.Date, nullable=False)
    comentarios      = db.Column(db.Text)
    usado            = db.Column(db.Boolean, default=False)

    # No hace falta renombrar; back_populates aquí es 'pedido'
    items            = db.relationship(
                          'BDPedidoItem',
                          back_populates='pedido',
                          cascade='all, delete-orphan'
                       )

