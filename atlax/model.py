

from sqlalchemy import create_engine, Column, Integer, \
	Numeric, String, ForeignKey, SmallInteger, \
	CheckConstraint, Date


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref

Base = declarative_base()


engine = create_engine('sqlite:///atlax/atlax inicial.db')

Session = sessionmaker(bind=engine)
session = Session()

class Sociedad(Base):

	__tablename__ = 'sociedades'

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
	desc = Column(String(64), nullable=False)

class Plazo(Base):

	__tablename__ = 'plazos'

	id = Column(Integer, primary_key=True)
	condicion_id = Column(Integer, ForeignKey('condiciones_pago_cobro.id'))
	forma_pago_id = Column(Integer, ForeignKey('formas_pago_cobro.id'))

	dias = Column(Integer, nullable=False)
	porc = Column(Numeric(18, 2), nullable=False)

	forma_pago = relationship('FormasPagoCobro', uselist=False)
	condicion = relationship('CondicionesPagoCobro', backref=backref('plazos', uselist=True))


class Cliente(Base):

	__tablename__ = 'clientes'

	id = Column(Integer, primary_key=True)
	sociedad_id = Column(Integer, ForeignKey('sociedades.id'), nullable=False)
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

	cliente = relationship('Cliente', backref=backref('direcciones', uselist=True))

	def __init__(self, tdireccion, domicilio, ciudad, prov, pais):
		super().__init__()
		self.tdireccion = tdireccion
		self.domicilio = domicilio
		self.ciudad = ciudad
		self.prov = prov
		self.pais = pais

	__table_args__ = (
		CheckConstraint('tdireccion in (0, 1)'),
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

	numero_documento = Column(String(64), nullable=False)
	fecha_emision = Column(Date, nullable=False)
	fecha_vencimiento = Column(Date, nullable=False)
	fecha_compensacion = Column(Date, nullable=False)
	importe = Column(Numeric(18, 2), nullable=False)
	tdoc = Column(String(32), nullable=False)

	cliente = relationship('Cliente', backref=backref('partidas_compensadas', uselist=True))
	forma_pago = relationship('FormasPagoCobro', uselist=False)


class PartidasCompensadasAnuladas(Base):

	__tablename__ = 'partidas_compensadas_anuladas'

	id = Column(Integer, primary_key=True)
	partida_compensada_id = Column(Integer, ForeignKey('partidas_compensadas.id'), nullable=False)

	fecha_inv = Column(Date, nullable=False)
	fecha_creacion = Column(Date, nullable=False)

	partida_compensada = relationship('PartidasCompensadas', backref=backref('anulaciones', uselist=True))


class ResumenVentas(Base):

	__tablename__ = 'resumen_ventas'

	id = Column(Integer, primary_key=True)

	cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
	anio = Column(Integer, nullable=False)
	mes = Column(Integer, nullable=False)
	importe = Column(Numeric(18, 2), nullable=False)

	cliente = relationship('Cliente', uselist=False)


''' Function that generates random strings of lenght 9. First is letter, then digits'''
def generate_random_nif():
	import random, string
	return random.choice(string.ascii_letters) + ''.join(random.choice(string.digits) for _ in range(8))



''' Function that creates sample data for these relations using Faker library. Also links the relationships '''
def create_sample_data():

	from faker import Faker
	fake = Faker()
	sociedad = Sociedad()
	sociedad.razons = 'Sociedad de Prueba'
	sociedad.nif = '12345678A'
	sociedad.codmoneda = 'EUR'

	session.add(sociedad)

	clasificacion = Clasificacion()
	clasificacion.desc = 'Criterio Unico'

	session.add(clasificacion)

	forma_pago = FormasPagoCobro()
	forma_pago.desc = 'Transferencia'

	session.add(forma_pago)

	condicion = CondicionesPagoCobro()
	condicion.desc = 'Contado'

	session.add(condicion)

	plazo = Plazo()

	plazo.condicion = condicion
	plazo.forma_pago = forma_pago
	plazo.dias = 0
	plazo.porc = 100

	session.add(plazo)

	clients = []
	for i in range(10):
		c = Cliente()
		c.razons = fake.company()
		c.nif = generate_random_nif()
		c.sociedad = sociedad
		c.clasificacion = clasificacion
		c.condicion = condicion
		c.forma_pago = forma_pago

		session.add(c)
		clients.append(c)

	for c in clients:
		c.direcciones.extend(
			[
				Direccion(
					tdireccion=0,
					domicilio=fake.street_address(),
					ciudad=fake.city(),
					prov=fake.state(),
					pais=fake.country(),
				),
				Direccion(
					tdireccion=1,
					domicilio=fake.street_address(),
					ciudad=fake.city(),
					prov=fake.state(),
					pais=fake.country(),
				)
			]
		)


if __name__ == '__main__':
	Base.metadata.create_all(engine)
	create_sample_data()
	session.commit()




