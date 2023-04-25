

from sqlalchemy import create_engine, Column, Integer, \
	Numeric, String, ForeignKey, SmallInteger, \
	CheckConstraint, Date


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref

Base = declarative_base()

class Sociedad(Base):

	__tablename__ = 'empresas'

	id = Column(Integer, primary_key=True)
	razons = Column(String(255), nullable=False)
	nif = Column(String(9), nullable=False)
	codmoneda = Column(String(3), nullable=False)


class Clasificacion(Base):

	__tablename__ = 'clasificaciones'

	id = Column(Integer, primary_key=True)
	desc = Column(String(255), nullable=False)


class FormasPagoCobro(Base):

	__tablename__ = 'formas_pago_cobro'

	id = Column(Integer, primary_key=True)
	desc = Column(String(255), nullable=False)


class CondicionesPagoCobro(Base):

	__tablename__ = 'condiciones_pago_cobro'

	id = Column(Integer, primary_key=True)
	cod = Column(String(64), nullable=False)

class Plazo(Base):

	__tablename__ = 'plazos'

	id = Column(Integer, primary_key=True)
	condiciones_id = Column(Integer, ForeignKey('condiciones_pago_cobro.id'))
	forma_pago_id = Column(Integer, ForeignKey('formas_pago_cobro.id'))

	dias = Column(Integer, nullable=False)
	porc = Column(Numeric(18, 2), nullable=False)

	plazos = relationship('CondicionesPagoCobro', backref=backref('plazos', uselist=True))
	forma_pago = relationship('FormasPagoCobro', uselist=False)


class Cliente(Base):

	__tablename__ = 'clientes'

	id = Column(Integer, primary_key=True)

	condicion_id = Column(Integer, ForeignKey('condiciones_pago_cobro.id'), nullable=True)
	clasificacion_id = Column(Integer, ForeignKey('clasificaciones.id'), nullable=True)
	forma_pago_id = Column(Integer, ForeignKey('formas_pago_cobro.id'), nullable=True)

	nif = Column(String(32), nullable=False)
	razons = Column(String(255), nullable=False)
	condicion = relationship('CondicionesPagoCobro', uselist=False)
	clasificacion = relationship('Clasificacion', uselist=False)
	forma_pago = relationship('FormasPagoCobro', uselist=False)

	sociedad = relationship('Sociedad', backref=backref('clientes', uselist=True))


class Direccion(Base):

	__tablename__ = 'direcciones'

	id = Column(Integer, primary_key=True)
	cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)

	tdireccion = Column(SmallInteger, nullable=False)

	domicilio = Column(String(255), nullable=False)
	ciudad = Column(String(255), nullable=False)
	prov = Column(String(255), nullable=False)
	pais = Column(String(255), nullable=False)

	__table_args__ = (
		CheckConstraint('tdireccion in (0, 1)')
	)


class PartidasAbiertas(Base):

	__tablename__ = 'partidas_abiertas'

	id = Column(Integer, primary_key=True)
	cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)

	numero_documento = Column(String(64), primary_key=True)
	fecha_emision = Column(Date, nullable=False)
	fecha_vencimiento = Column(Date, nullable=False)
	importe = Column(Numeric(18, 2), nullable=False)
	tdoc = Column(String(32), nullable=False)

	cliente = relationship('Cliente', backref=backref('partidas_abiertas', uselist=True))

class PartidasCompensadas(Base):

	__tablename__ = 'partidas_compensadas'

	id = Column(Integer, primary_key=True)
	cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
	forma_pago_id = Column(Integer, ForeignKey('formas_pago_cobro.id'), nullable=False)

	numero_documento = Column(Integer, String(64), nullable=False)
	fecha_emision = Column(Date, nullable=False)
	fecha_vencimiento = Column(Date, nullable=False)
	fecha_compensacion = Column(Date, nullable=False)
	importe = Column(Numeric(18, 2), nullable=False)
	tdoc = Column(String(32), nullable=False)

	cliente = relationship('Cliente', backref=backref('partidas_abiertas', uselist=True))
	forma_pago = relationship('FormasPagoCobro', uselist=False)


class PartidasCompensadasAnuladas(Base):

	__tablename__ = 'partidas_compensadas_anuladas'

	id = Column(Integer, primary_key=True)
	partida_compensada_id = Column(Integer, ForeignKey('partidas_compensadas.id'), nullable=False)

	fecha_inv = Column(Date, nullable=False)
	fecha_creacion = Column(Date, nullable=False)

	partida_compensada = Column('PartidasCompensadas', backref=backref('partidas_compensadas_anuladas', uselist=True))


class ResumenVentas(Base):

	__tablename__ = 'resumen_ventas'

	id = Column(Integer, primary_key=True)

	cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
	anio = Column(Integer, nullable=False)
	mes = Column(Integer, nullable=False)
	importe = Column(Numeric(18, 2), nullable=False)

	cliente = relationship('Cliente', uselist=False)


engine = create_engine('sqlite:///atlax inicial.db')
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()


