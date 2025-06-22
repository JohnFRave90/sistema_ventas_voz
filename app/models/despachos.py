from app import db

# Modelo principal del despacho
class BDDespacho(db.Model):
    __tablename__ = 'BD_DESPACHOS'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    vendedor_cod = db.Column(db.String(20), nullable=False)
    codigo_origen = db.Column(db.String(20), nullable=False)  # PD-xxxxx o EX-xxxxx
    tipo_origen = db.Column(db.String(10), nullable=False)    # "pedido" o "extra"
    despachado = db.Column(db.Boolean, default=False)
    comentarios = db.Column(db.Text)

    items = db.relationship(
        'BDDespachoItem',
        back_populates='despacho',
        cascade='all, delete-orphan'
    )


# Modelo por producto despachado
class BDDespachoItem(db.Model):
    __tablename__ = 'BD_DESPACHO_ITEMS'

    id = db.Column(db.Integer, primary_key=True)
    despacho_id = db.Column(db.Integer, db.ForeignKey('BD_DESPACHOS.id'), nullable=False)
    producto_cod = db.Column(db.String(20), nullable=False)
    cantidad_pedida = db.Column(db.Integer, default=0)
    cantidad = db.Column(db.Integer, nullable=False)
    lote = db.Column(db.String(20), nullable=True)
    precio_unitario = db.Column(db.Numeric(10,2), nullable=False)
    subtotal = db.Column(db.Numeric(12,2), nullable=False)

    pedido_id = db.Column(db.Integer, db.ForeignKey('bd_pedidos.id'), nullable=True)
    extra_id = db.Column(db.Integer, db.ForeignKey('BD_EXTRAS.id'), nullable=True)

    despacho = db.relationship('BDDespacho', back_populates='items')
