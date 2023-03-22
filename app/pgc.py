import sys

from db import session, Account

ACCOUNTS = {
	1: {
		'name': 'Financiación Básica',
		'children': {
			10: {
				'name': 'Capital',
				'children': {
					100: {'name': 'Capital Social'},
					101: {'name': 'Fondo Social'},
					102: {'name': 'Capital'},
					103: {
						'name': 'Socios por desembolsos no exigidos',
						'children': {
							1030: {'name': 'Socios por desembolsos no exigidos, capital social'},
							1034: {'name': 'Socios por desembolsos no exigidos, capital pendiente de inscripción'}
						}
					},
					104: {
						'name': 'Socios por aportaciones no dinerarias pendientes',
						'children': {
							1040: {'name': 'Socios por aportaciones no dinerarias pendientes, capital social'},
							1044: {
								'name': 'Socios por aportaciones no dinerarias pendientes, capital pendiente de inscripción'}
						}
					},
					108: {'name': 'Acciones o participaciones propias en situaciones especiales'},
					109: {'name': 'Acciones o participaciones propias para reducción de capital'},
				}
			},

			11: {
				'name': 'Reservas',
				'children': {

				}
			},

			12: {
				'name': 'Resultados Pendientes De Aplicación',
				'children': {
					120: {'name': 'Remanente'},
					121: {'name': 'Resultados negativos de ejercicios anteriores'},
					129: {'name': 'Resultado del Ejercicio'}
				}
			},
			13: {
				'name': 'Subvenciones, Donaciones, Legados y otros ajustes del patrimonio neto',
				'children': {
					130: {'name': 'Subvenciones oficiales de Capital'},
					131: {'name': 'Donaciones y legados de Capital'},
					132: {'name': 'Otras subvenciones, donaciones y legados'},
					137: {
						'name': 'Ingresos fiscales a distribuir en otros ejercicios',
						'children': {
							1370: {
								'name': 'Ingresos fiscales por diferencias permanentes a distribuir en varios ejercicios'},
							1371: {
								'name': 'Ingresos fiscales por deducciones y bonificaciones a distribuir en varios ejercicios'}
						}
					}
				}
			},
			14: {
				'name': 'Provisiones',
				'children': {
					141: {'name': 'Provision para Impuestos'},
					142: {'name': 'Provision para otras responsabilidades'},
					143: {'name': 'Provision para desmantelamiento, retiro o rehabilitación de inmovilizado'},
					145: {'name': 'Provision para actuaciones medio ambientales'}
				}
			},
			15: {
				'name': 'Deudas LP con características especiales',
				'children': {
					150: {'name': 'Acciones o participaciones a largo plazo considerados como pasivos financieros'},
					153: {
						'name': 'Desembolsos no exigidos por acciones o participaciones considerados como pasivos financieros',
						'children': {
							1533: {'name': 'Desembolsos no exigidos, empresas del grupo'},
							1534: {'name': 'Desembolsos no exigidos, empresas asociadas'},
							1535: {'name': 'Desembolsos no exigidos, con otras partes vinculadas'},
							1536: {'name': 'Otros desembolsos no exigidos'}
						}
					},
					154: {
						'name': 'Aportaciones no dinerarias pendientes por acciones o '
						        'participaciones considerados como pasivos financieros',
						'children': {
							1543: {'name': 'Aportaciones no dinerarias pendientes, empresas del grupo'},
							1544: {'name': 'Aportaciones no dinerarias pendientes, empresas asociadas'},
							1545: {'name': 'Aportaciones no dinerarias pendientes, otras partes vinculadas'},
							1546: {'name': 'Otras aportaciones no dinerarias pendientes'}
						}
					}
				}
			},
			16: {
				'name': 'Deudas a largo plazo con partes vinculadas',
				'children': {
					160: {
						'name': 'Deudas LP con entidades de crédito vinculadas',
						'children': {
							1603: {'name': 'Deudas LP con entidades de crédito vinculadas, empresas del grupo'},
							1604: {'name': 'Deudas LP con entidades de crédito vinculadas, empresas asociadas'},
							1605: {'name': 'Deudas LP con entidades de crédito vinculadas, otras partes vinculadas'},
						}
					},
					161: {
						'name': 'Proveedores de Inmovilizado LP, partes vinculadas',
						'children': {
							1613: {'name': 'Proveedores de Inmovilizado LP, partes vinculadas, empresas del grupo'},
							1614: {'name': 'Proveedores de Inmovilizado LP, partes vinculadas, empresas asociadas'},
							1615: {
								'name': 'Proveedores de Inmovilizado LP, partes vinculadas, otras partes vinculadas'},

						}
					},
					162: {
						'name': 'Acreedores por arrendamiento financiero LP , partes vinculadas',
						'children': {
							1623: {'name': 'Acreedores por arrendamiento financiero LP, empresas del grupo'},
							1624: {'name': 'Acreedores por arrendamiento financiero LP, empresas asociadas'},
							1625: {'name': 'Acreedores por arrendamiento financiero LP, otras partes vinculadas'},
						}
					},
					163: {
						'name': 'Otras deudas LP con partes vinculadas',
						'children': {
							1633: {'name': 'Otras deudas LP,  empresas del grupo'},
							1634: {'name': 'Otras deudas LP,  empresas asociadas'},
							1635: {'name': 'Otras deudas LP,  otras partes vinculadas'},
						}
					},
				}
			},
			17: {
				'name': 'Deudas LP por préstamos, empréstitos y otros conceptos',
				'children': {
					170: {'name': 'Deudas LP con entidades de crédito'},
					171: {'name': 'Deudas LP'},
					172: {'name': 'Deudas LP transformables en donaciones, subvenciones o legados'},
					173: {'name': 'Proveedores de Inmovilizado LP'},
					174: {'name': 'Acreedores por arrendamiento financiero LP'},
					175: {'name': 'Efectos a pagar LP'},
					176: {'name': 'Pasivos por derivados financieros a largo plazo'},
					177: {'name': 'Obligaciones y Bonos'},
					179: {'name': 'Deudas representadas en valores negociables'}
				}
			},
			18: {
				'name': 'Pasivos por fianzas, garantías y otros conceptos a largo plazo',
				'children': {
					180: {'name': 'Fianzas recibidas LP'},
					181: {'name': 'Anticipos Recibidos por ventas o prestaciones de servicios LP'},
					185: {'name': 'Depósitos recibidos LP'}
				}
			},
			19: {
				'name': 'Situaciones Transitorias de Financiación',
				'children': {
					190: {'name': 'Acciones o participaciones emitidas'},
					192: {'name': 'Suscriptores de acciones'},
					194: {'name': 'Capital Emitido pendiente de inscripción'},
					195: {'name': 'Acciones o participaciones emitidas consideradas como pasivos financieros'},
					197: {'name': 'Suscriptores de acciones consideradas como pasivos financieros'},
					199: {'name': 'Acciones o participaciones emitidas consideradas '
					              'como pasivos financieros pendientes de inscripción'}
				}
			}
		}
	}, 2: {
		'name': 'Activo No Corriente',
		'children': {
			20: {
				'name': 'Inmovilizaciones Intangibles',
				'children': {
					200: {'name': 'Investigación'},
					201: {'name': 'Desarrollo'},
					202: {'name': 'Concesiones administrativas'},
					203: {'name': 'Propiedad Industrial'},
					205: {'name': 'Derechos de Traspaso'},
					206: {'name': 'Aplicaciones Informáticas'},
					209: {'name': 'Anticipos para Inmovilizaciones Intangibles'}
				}
			},
			21: {
				'name': 'Inmovilizaciones Materiales',
				'children': {
					210: {'name': 'Terrenos y Bienes Naturales'},
					211: {'name': 'Construcciones'},
					212: {'name': 'Instalaciones Técnicas'},
					213: {'name': 'Maquinaria'},
					214: {'name': 'Utillaje'},
					215: {'name': 'Otras Instalaciones'},
					216: {'name': 'Mobiliario'},
					217: {'name': 'Equipos para Proceso de Información'},
					218: {'name': 'Elementos de Transporte'},
					219: {'name': 'Otro Inmovilizado Material'}
				}
			},
			22: {
				'name': 'Inversiones Inmobiliarias',
				'children': {
					220: {'name': 'Inversiones en Terrenos y bienes naturales'},
					221: {'name': 'Inversiones en Construcciones'},
				}
			},
			23: {
				'name': 'Inmovilizaciones materiales en curso',
				'children': {
					230: {'name': 'Adaptación de terrenos y bienes naturales'},
					231: {'name': 'Construcciones en curso'},
					232: {'name': 'Instalaciones técnicas en montaje'},
					233: {'name': 'Maquinaria en montaje'},
					237: {'name': 'Equipos para procesos de información en montaje'},
					239: {'name': 'Anticipos para inmovilizaciones materiales'},
				}
			},
			24: {
				'name': 'Inversiones Financieras LP en Partes Vinculadas ',
				'children': {
					240: {
						'name': 'Participaciones a LP en partes vinculadas',
						'children': {
							2403: {'name': 'Participaciones a LP en empresas del grupo'},
							2404: {'name': 'Participaciones a LP en empresas asociadas'},
							2405: {'name': 'Participaciones a LP en otras partes vinculadas'},
						}
					},
					241: {
						'name': 'Valores Representativos de Deuda LP en partes vinculadas',
						'children': {
							2413: {'name': 'Valores Representativos de Deuda LP en empresas del grupo'},
							2414: {'name': 'Valores Representativos de Deuda LP en empresas asociadas'},
							2415: {'name': 'Valores Representativos de Deuda LP en otras partes vinculadas'},
						}
					},
					242: {
						'name': 'Créditos a LP en partes vinculadas',
						'children': {
							2423: {'name': 'Créditos LP en empresas del grupo'},
							2424: {'name': 'Créditos LP en empresas asociadas'},
							2425: {'name': 'Créditos LP en otras partes vinculadas'},
						}
					},
					249: {
						'name': 'Desembolsos pendientes sobre participaciones LP de partes vinculadas',
						'children': {
							2493: {'name': 'Desembolsos pendientes sobre participaciones LP de empresas del grupo'},
							2494: {'name': 'Desembolsos pendientes sobre participaciones LP de empresas asociadas'},
							2495: {'name': 'Desembolsos pendientes sobre participaciones LP de otras partes vinculadas'}
						}
					}
				}
			},
			25: {
				'name': 'Otras Inversiones Financieras LP',
				'children': {
					250: {'name': 'Inversiones Financieras LP en Instrumentos de Patrimonio'},
					251: {'name': 'Valores representativos de deuda LP'},
					252: {'name': 'Créditos a LP'},
					253: {'name': 'Créditos LP por enajenación de Inmovilizado'},
					254: {'name': 'Créditos LP al personal'},
					255: {
						'name': '',
						'children': {
							2550: {'name': 'Activos por Derivados financieros LP, cartera de negociación'},
							2553: {'name': 'Activos por Derivados financieros LP, instrumentos de cobertura'},
						}
					},
					257: {
						'name': 'Derechos de reembolso derivados de contratos de seguro relativos a retribuciones LP del personal'},
					258: {'name': 'Imposiciones a LP'},
					259: {'name': 'Desembolsos pendientes sobre participaciones en el Patrimonio Neto LP'},
				}
			},
			26: {
				'name': 'Fianzas y Depósitos constituidos LP ',
				'children': {
					260: {'name': 'Fianzas constituidas LP'},
					265: {'name': 'Depósitos constituidos LP'}
				}
			},
			28: {
				'name': 'Amortización acumulada del Inmovilizado Intangible',
				'children': {
					280: {
						'name': 'Amortización acumulada del Inmovilizado Intangible',
						'children': {
							2800: {'name': 'Amortización acumulada de Investigación'},
							2801: {'name': 'Amortización acumulada de Desarrollo'},
							2802: {'name': 'Amortización acumulada de Concesiones administrativas'},
							2803: {'name': 'Amortización acumulada de Propiedad industrial'},
							2804: {'name': 'Amortización acumulada de Fondo de Comercio'},
							2805: {'name': 'Amortización acumulada de Derechos de Traspaso'},
							2806: {'name': 'Amortización acumulada de Otros Aplicaciones Informáticas'},
						}
					},
					281: {
						'name': 'Amortización acumulada del Inmovilizado Material',
						'children': {
							2811: 'Amortización acumulada de Construcciones',
							2812: 'Amortización acumulada de Instalaciones Técnicas',
							2813: 'Amortización acumulada de Maquinaria',
							2814: 'Amortización acumulada de Utillaje',
							2815: 'Amortización acumulada de Otras Instalaciones',
							2816: 'Amortización acumulada de Mobiliario',
							2817: 'Amortización acumulada de Equipos para procesos de información',
							2818: 'Amortización acumulada de Elementos De Transporte',
							2819: 'Amortización acumulada de otro Inmovilizado Material',
						}
					},
					282: {'name': 'Amortización acumulada de Inversiones Inmobiliarias'}
				}
			},
			29: {
				'name': 'Inversiones en Instrumentos de Patrimonio',
				'children': {
					290: {
						'name': 'Deterioro de valor del Inmovilizado Intangible',
						'children': {
							2900: {'name': 'Deterioro de valor de Investigación'},
							2901: {'name': 'Deterioro de valor de Desarrollo'},
							2902: {'name': 'Deterioro de valor de Concesiones administrativas'},
							2903: {'name': 'Deterioro de valor de Propiedad industrial'},
							2905: {'name': 'Deterioro de valor de Derechos De Traspaso'},
							2906: {'name': 'Deterioro de valor de Otros Aplicaciones Informáticas'}
						}
					},

					291: {
						'name': 'Deterioro del Valor de Inmovilizado Material',
						'children': {
							2910: {'name': 'Deterioro de valor de Terrenos y Bienes Naturales'},
							2911: {'name': 'Deterioro de valor de Construcciones'},
							2912: {'name': 'Deterioro de valor de Instalaciones Técnicas'},
							2913: {'name': 'Deterioro de valor de Maquinaria'},
							2914: {'name': 'Deterioro de valor de Utillaje'},
							2915: {'name': 'Deterioro de valor de Otras Instalaciones'},
							2916: {'name': 'Deterioro de valor de Mobiliario'},
							2917: {'name': 'Deterioro de valor de Equipos para procesos de información'},
							2918: {'name': 'Deterioro de valor de Elementos De Transporte'},
							2919: {'name': 'Deterioro de valor de otro Inmovilizado Material'},
						}
					},
					292: {
						'name': 'Deterioro de Valor de Inversiones Inmobiliarias',
						'children': {
							2920: {'name': 'Deterioro de valor de Terrenos y Bienes Naturales'},
							2921: {'Deterioro de valor de Construcciones'}
						}
					},
					293: {
						'name': 'Deterioro de valor de Participaciones LP',
						'children': {
							2933: {'name': 'Deterioro de valor de Participaciones LP en empresas del grupo'},
							2934: {'name': 'Deterioro de valor de Participaciones LP en empresas asociadas'},
							2935: {'name': 'Deterioro de valor de Participaciones LP en otras Partes vinculadas'},
							2936: {'name': 'Deterioro de valor de Participaciones LP en otras empresas'},
						}
					},
					294: {
						'name': 'Deterioro de valor de de valores representativos de deuda de partes vinculadas',
						'children': {
							2943: {'name': 'Deterioro de valor de de valores representativos de deuda LP de empresas del grupo'},
							2944: {'name': 'Deterioro de valor de de valores representativos de deuda LP de empresas asociadas'},
							2945: {'name': 'Deterioro de valor de de valores representativos de deuda LP de otras Partes vinculadas'},
						}
					},
					295: {
						'name': 'Deterioro de valor de Créditos LP a partes vinculadas',
						'children': {
							2953: {'name': 'Deterioro de valor de Créditos LP a empresas del grupo'},
							2954: {'name': 'Deterioro de valor de Créditos LP a empresas asociadas'},
							2955: {'name': 'Deterioro de valor de Créditos LP a otras Partes vinculadas'},
						}
					},
					297: {'name': 'Deterioro de valor de valores representativos de deuda LP'},
					298: {'name': 'Deterioro de valor de Créditos LP'}
				}
			}
		}
	},
	3: {
		'name': 'Existencias',
		'children': {
			30: {
				'name': 'Comerciales',
				'children': {
					300: {'name': 'Mercaderías A'},
					301: {'name': 'Mercaderías B'}
				}
			},
			31: {
				'name': 'Materias Primas',
				'children': {
					310: {'name': 'Materias Primas A'},
					311: {'name': 'Materias Primas B'}
				}
			},
			32: {
				'name': 'Otros Aprovisionamientos',
				'children': {
					320: {'name': 'Elementos y conjuntos incorporables'},
					321: {'name': 'Combustibles'},
					322: {'name': 'Repuestos'},
					325: {'name': 'Materiales Diversos'},
					326: {'name': 'Embalajes'},
					327: {'name': 'Envases'},
					328: {'name': 'Material de oficina'}
				}
			},
			33: {
				'name': 'Productos en Curso',
				'children': {
					330: {'name': 'Productos en Curso A'},
					331: {'name': 'Productos en Curso B'}
				}
			},
			34: {
				'name': 'Productos Semiterminados',
				'children': {
					340: {'name': 'Productos Semiterminados A'},
					341: {'name': 'Productos Semiterminados B'}
				}
			},
			35: {
				'name': 'Productos Terminados',
				'children': {
					350: {'name': 'Productos Terminados A'},
					351: {'name': 'Productos Terminados B'}
				}
			},
			36: {
				'name': 'Subproductos, residuos y materiales recuperados',
				'children': {
					360: {'name': 'Subproductos A'},
					361: {'name': 'Subproductos B'},
					365: {'name': 'Residuos A'},
					366: {'name': 'Residuos B'},
					367: {'name': 'Materiales recuperados A'},
					368: {'name': 'Materiales recuperados B'}
				}
			},
			39: {
				'name': 'Deterioro de valor de existencias',
				'children': {
					390: {'name': 'Deterioro de valor de mercaderías'},
					391: {'name': 'Deterioro de valor de materias primas'},
					392: {'name': 'Deterioro de valor de otros aprovisionamientos'},
					393: {'name': 'Deterioro de valor de productos en curso'},
					394: {'name': 'Deterioro de valor de productos semiterminados'},
					395: {'name': 'Deterioro de valor de productos terminados'},
					396: {'name': 'Deterioro de valor de subproductos, residuos y materiales recuperados'}
				}
			}
		}
	},
	4: {
		'name': 'Acreedores y Deudores Por Operaciones Comerciales',
		'children': {
			40: {
				'name': 'Proveedores',
				'children': {
					400: {
						'name': 'Proveedores',
						'children': {
							4000: {'name': 'Proveedores (Euros)'},
							4004: {'name': 'Proveedores (Moneda Extranjera)'},
							4009: {'name': 'Proveedores, facturas pendientes de recibir o de formalizar'}
						},
					},
					401: {'name': 'Proveedores, efectos comerciales a pagar'},
					403: {
						'name': 'Proveedores, empresas del grupo',
						'children': {
							4030: {'name': 'Proveedores, empresas del grupo (Euros)'},
							4031: {'name': 'Efectos comerciales a pagar, empresas del grupo'},
							4034: {'name': 'Proveedores, empresas del grupo (Moneda Extranjera)'},
							4039: {'name': 'Proveedores, empresas del grupo, facturas pendientes de recibir o de formalizar'}
						}
					},
					404: {'name': 'Proveedores, empresas asociadas'},
					405: {'name': 'Proveedores, otras partes vinculadas'},
					406: {'name': 'Envases y embalajes a devolver'},
					407: {'name': 'Anticipos a proveedores'}
				}
			},
			41: {
				'name': 'Acreedores Varios',
				'children': {
					410: {
						'name': 'Acreedores por prestación de servicios',
						'children': {
							4100: {'name': 'Acreedores por prestación de servicios (Euros)'},
							4104: {'name': 'Acreedores por prestación de servicios (Moneda Extranjera)'},
							4109: {'name': 'Acreedores por prestación de servicios, facturas pendientes de recibir o de formalizar'}
						}
					},
					411: {'name': 'Acreedores, efectos comerciales a pagar'},
					419: {'name': 'Acreedores por operaciones en comumn'}
				}
			},
			43: {
				'name': 'Clientes',
				'children': {
					430: {
						'name': 'Clientes',
						'children': {
							4300: {'name': 'Clientes (Euros)'},
							4304: {'name': 'Clientes (Moneda Extranjera)'},
							4309: {'name': 'Clientes, facturas pendientes de formalizar'}
						}
					},
					431: {
						'name': 'Clientes, efectos comerciales a cobrar',
						'children': {
							4310: {'name': 'Efectos comerciales en cartera'},
							4311: {'name': 'Efectos comerciales descontados'},
							4312: {'name': 'Efectos comerciales en gestion de cobro'},
							4315: {'name': 'Efectos comerciales impagados'}
						}
					},
					432: {'name': 'Clientes, operaciones de Factoring'},
					433: {
						'name': 'Clientes, empresas del grupo',
						'children': {
							4330: {'name': 'Clientes, empresas del grupo (Euros)'},
							4331: {'name': 'Efectos comerciales a cobrar, empresas del grupo'},
							4332: {'name': 'Clientes empresas del grupo, operaciones de Factoring'},
							4334: {'name': 'Clientes empresas del grupo (Moneda Extranjera)'},
							4336: {'name': 'Clientes empresas del grupo de dudosos cobro'},
							4337: {'name': 'Envases y embalajes a devolver a clientes, empresas del grupo'},
							4339: {'name': 'Clientes, empresas del grupo, facturas pendientes de formalizar'}
						}
					},
					434: {'name': 'Clientes, empresas asociadas'},
					435: {'name': 'Clientes, otras partes vinculadas'},
					436: {'name': 'Clientes de dudosos cobro'},
					437: {'name': 'Envases y embalajes a devolver por clientes'},
					438: {'name': 'Anticipos de clientes'}
				}
			},
			44: {
				'name': 'Deudores Varios',
				'children': {
					440: {
						'name': 'Deudores',
						'children': {
							4400: {'name': 'Deudores (Euros)'},
							4404: {'name': 'Deudores (Moneda Extranjera)'},
							4409: {'name': 'Deudores, facturas pendientes de formalizar'}
						}
					},
					441: {
						'name': 'Deudores, efectos comerciales a cobrar',
						'children': {
							4410: {'name': 'Deudores, Efectos comerciales en cartera'},
							4411: {'name': 'Deudores, Efectos comerciales descontados'},
							4412: {'name': 'Deudores, Efectos comerciales en gestion de cobro'},
							4415: {'name': 'Deudores, Efectos comerciales impagados'}
							}
					},
					446: {'name': 'Deudores de dudosos cobro'},
					449: {'name': 'Deudores por operaciones en común'}
				}
			},
			46: {
				'name': 'Personal',
				'children': {
					460: {'name': 'Anticipos de remuneraciones'},
					465: {'name': 'Remuneraciones pendientes de pago'},
					466: {'name': 'Remuneraciones mediante sistemas de aportación definida pendientes de pago'}
				}
			},
			47: {
				'name': 'Administraciones Públicas',
				'children': {
					470: {
						'name': 'Hacienda Publica, deudora por diversos conceptos',
						'children': {
							4700: {'name': 'Hacienda Pública, deudora por IVA'},
							4708: {'name': 'Hacienda Pública, deudora por subvenciones concedidas'},
							4709: {'name': 'Hacienda Pública, deudora por devolución de impuestos'},
						}
					},
					471: {'name': 'Organismos de la Seguridad Social, deudores'},
					472: {'name': 'Hacienda Publica, IVA Soportado'},
					473: {'name': 'Hacienda Pública, retenciones  y pagos a cuenta'},
					474: {
						'name': 'Activos por Impuesto Diferido',
						'children': {
							4740: {'name': 'Activos por diferencias temporarias deducibles'},
							4742: {'name': 'Derechos por deducciones y bonificaciones pendientes de aplicar'},
							4745: {'name': 'Créditos por perdidas a compensar en el ejercicio'}
						}
					},
					475: {
						'name': 'Hacienda Pública, Acreedora por conceptos fiscales',
						'children': {
							4750: {'name': 'Hacienda Pública, acreedora por IVA'},
							4751: {'name': 'Hacienda Pública, acreedora por retenciones practicadas'},
							4752: {'name': 'Hacienda Pública, acreedora por impuesto sobre sociedades'},
							4758: {'name': 'Hacienda Pública, acreedora por subvenciones a integrar'},
						}
					},
					476: {'name': 'Organismos de la Seguridad Social, acreedores'},
					477: {'name': 'Hacienda Pública, IVA Repercutido'},
					479: {'name': 'Pasivo por diferencias temporarias imponibles'}
				}
			},
			48: {
				'name': 'Ajustes por Periodificación',
				'children': {
					480: {'name': 'Gastos anticipados'},
					485: {'name': 'Ingresos anticipados'},
				}
			},
			49: {
				'name': 'Deterioro de valor de créditos comerciales y provisiones CP',
				'children': {
					490: {'name': 'Deterioro de valor de créditos por operaciones comerciales'},
					493: {
						'name': 'Deterioro de valor de créditos por operaciones con partes vinculadas',
						'children': {
							4933: {'name': 'Deterioro de valor de créditos por operaciones comerciales con empresas del grupo'},
							4934: {'name': 'Deterioro de valor de créditos por operaciones comerciales con empresas asociadas'},
							4935: {'name': 'Deterioro de valor de créditos por operaciones comerciales con otras partes vinculadas'},
						}
					},
					499: {
						'name': 'Provisiones por operaciones comerciales',
						'children': {
							4994: {'name': 'Provision por contratos onerosos'},
							4999: {'name': 'Provision para otras operaciones comerciales'}
						}
					}
				}
			},
		}
	},
	5: {
		'name': 'Cuentas Financieras',
		'children': {
			50: {
				'name': 'Empréstitos, Deudas con características especiales y otras emisiones análogas CP',
				'children': {
					500: {'name': 'Obligaciones y bonos CP'},
					501: {'name': 'Obligaciones y bonos convertibles CP'},
					502: {'name': 'Acciones o participaciones CP consideradas como pasivo financiero'},
					505: {'name': 'Deudas representadas en otros valores negociables CP'},
					506: {'name': 'Intereses CP de empréstitos y obligaciones análogas'},
					507: {'name': 'Dividendos de acciones o participaciones consideradas como pasivos financieros'},
					509: {
						'name': 'Valores negociables amortizados',
						'children': {
							5090: {'name': 'Obligaciones y bonos amortizados'},
							5091: {'name': 'Obligaciones y bonos convertibles amortizados'},
							5095: {'name': 'Otros valores negociables amortizados'}
						}
					}
				}
			},
			51: {
				'name': 'Deudas CP con partes vinculadas',
				'children': {
					510: {
						'name': 'Deudas CP con entidades de créditos vinculadas',
						'children': {
							5103: {'name': 'Deudas CP con entidades de crédito, empresas del grupo'},
							5104: {'name': 'Deudas CP con entidades de crédito, empresas asociadas'},
							5105: {'name': 'Deudas CP con entidades de crédito vinculadas'},
						}
					},
					511: {
						'name': 'Proveedores de Inmovilizado CP, partes vinculadas',
						'children': {
							5113: {'name': 'Proveedores de Inmovilizado CP, empresas del grupo'},
							5114: {'name': 'Proveedores de Inmovilizado CP, empresas asociadas'},
							5115: {'name': 'Proveedores de Inmovilizado CP, otras partes vinculadas'},
						}
					},
					512: {
						'name': 'Acreedores por arrendamiento financiero CP, partes vinculadas',
						'children': {
							5123: {'name': 'Acreedores por arrendamiento financiero CP, empresas del grupo'},
							5124: {'name': 'Acreedores por arrendamiento financiero CP, empresas asociadas'},
							5125: {'name': 'Acreedores por arrendamiento financiero CP, otras partes vinculadas'},
						}
					},
					513: {
						'name': 'Otras deudas CP con partes vinculadas',
						'children': {
							5133: {'name': 'Otras deudas CP con empresas del grupo'},
							5134: {'name': 'Otras deudas CP con empresas asociadas'},
							5135: {'name': 'Otras deudas CP con otras partes vinculadas'},
						}
					},
					514: {
						'name': 'Intereses CP de deudas con partes vinculadas',
						'children': {
							5143: {'name': 'Intereses CP de deudas, empresas del grupo'},
							5144: {'name': 'Intereses CP de deudas, empresas asociadas'},
							5145: {'name': 'Intereses CP de deudas, otras partes vinculadas'},
						}
					}
				}
			},
			52: {
				'name': 'Deudas CP por préstamos recibidos y otros conceptos',
				'children': {
					520: {
						'name': 'Deudas CP con entidades de crédito',
						'children': {
							5200: {'name': 'Prestamos CP con entidades de crédito'},
							5201: {'name': 'Deudas CP por crédito dispuesto'},
							5208: {'name': 'Deudas por efectos descontados'},
							5309: {'name': 'Deudas por operaciones de Factoring'}
						}

					},
					521: {'name': 'Deudas CP'},
					522: {'name': 'Deudas CP transformables en subvenciones, donaciones y legados'},
					523: {'name': 'Proveedores de inmovilizado CP'},
					524: {'name': 'Acreedores por Arrendamiento Financiero CP'},
					525: {'name': 'Efectos a pagar CP'},
					526: {'name': 'Dividendo activo a pagar'},
					527: {'name': 'Intereses CP de deudas con entidades de crédito'},
					528: {'name': 'Intereses CP deudas'},
					529: {
						'name': 'Provisiones CP',
						'children': {
							5290: {'name': 'Provision CP por retribuciones al personal'},
							5291: {'name': 'Provision CP para impuestos'},
							5292: {'name': 'Provision CP por otras responsabilidades'},
							5293: {'name': 'Provision CP por desmantelamiento, retiro y rehabilitación del inmovilizado'},
							5295: {'name': 'Provision CP para actuaciones medioambientales'},
							5296: {'name': 'Provision CP para reestructuraciones'},
							5297: {'name': 'Provision CP por transacciones con pagos basados en instrumentos de patrimonio'},

						}
					}
				}
			},
			53: {
				'name': 'Inversiones financieras CP en partes vinculadas',
				'children': {
					530: {
						'name': 'Participaciones CP en partes vinculadas',
						'children': {
							5303: {'name': 'Participaciones CP en empresas del grupo'},
							5304: {'name': 'Participaciones CP en empresas asociadas'},
							5305: {'name': 'Participaciones CP en otras partes vinculadas'},
						}
					},
					531: {
						'name': 'Valores representativos de deuda CP de partes vinculadas',
						'children': {
							5313: {'name': 'Valores representativos de deuda CP de empresas del grupo'},
							5314: {'name': 'Valores representativos de deuda CP de empresas asociadas'},
							5315: {'name': 'Valores representativos de deuda CP de otras partes vinculadas'},
						}
					},
					532: {
						'name': 'Créditos CP a partes vinculadas',
						'children': {
							5323: {'name': 'Créditos CP a empresas del grupo'},
							5324: {'name': 'Créditos CP a empresas asociadas'},
							5325: {'name': 'Créditos CP a otras partes vinculadas'},
						}
					},
					533: {
						'name': 'Intereses CP de valores representativos de deuda de partes vinculadas',
						'children': {
							5333: {'name': 'Intereses CP de valores representativos de deuda de empresas del grupo'},
							5334: {'name': 'Intereses CP de valores representativos de deuda de empresas asociadas'},
							5335: {'name': 'Intereses CP de valores representativos de deuda de otras partes vinculadas'},
						}
					},
					534: {
						'name': 'Intereses CP de créditos a partes vinculadas',
						'children': {
							5343: {'name': 'Intereses CP de créditos a empresas del grupo'},
							5344: {'name': 'Intereses CP de créditos a empresas asociadas'},
							5345: {'name': 'Intereses CP de créditos a otras partes vinculadas'},
						}
					},
					535: {
						'name': 'Dividendo a cobrar de inversiones financieras en partes vinculadas',
						'children': {
							5353: {'name': 'Dividendo a cobrar de empresas del grupo'},
							5354: {'name': 'Dividendo a cobrar de empresas asociadas'},
							5355: {'name': 'Dividendo a cobrar de otras partes vinculadas'},
						}
					},
					539: {
						'name': 'Desembolsos pendientes sobre participaciones CP en partes vinculadas',
						'children': {
							5393: {'name': 'Desembolsos pendientes sobre participaciones CP en empresas del grupo'},
							5394: {'name': 'Desembolsos pendientes sobre participaciones CP en empresas asociadas'},
							5395: {'name': 'Desembolsos pendientes sobre participaciones CP en otras partes vinculadas'},
						}
					}
				}
			},
			54: {
				'name': 'Otras inversiones financieras CP',
				'children': {
					540: {'name': 'Inversiones financieras CP en instrumentos de patrimonio'},
					541: {'name': 'Valores representativos de deuda CP'},
					542: {'name': 'Créditos CP'},
					543: {'name': 'Créditos CP por enajenación de Inmovilizado'},
					544: {'name': 'Créditos CP al personal'},
					545: {'name': 'Dividendo a cobrar'},
					546: {'name': 'Intereses CP de valores representativos de deuda'},
					547: {'name': 'Intereses CP de créditos'},
					548: {'name': 'Imposiciones CP'},
					549: {'name': 'Desembolsos pendientes sobre participaciones en patrimonio neto a corto plazo'}
				}
			},
			55: {
				'name': 'Otras cuentas no bancarias',
				'children': {
					550: {'name': 'Titular de explotación'},
					551: {'name': 'Cuenta corriente con socios y administradores'},
					552: {
						'name': 'Cuenta corriente con otras personas y entidades vinculadas',
						'children': {
							5523: {'name': 'Cuenta corriente con empresas del grupo'},
							5524: {'name': 'Cuenta corriente con empresas asociadas'},
							5525: {'name': 'Cuenta corriente con otras partes vinculadas'},
						}
					},
					553: {
						'name': 'Cuentas corrientes en fusiones y escisiones',
						'children': {
							5530: {'name': 'Socios de sociedad disuelta'},
							5531: {'name': 'Socios de fusion'},
							5532: {'name': 'Socios de sociedad escindida'},
							5533: {'name': 'Socios, cuenta de escisión'}
						}
					},
					554: {'name': 'Cuenta corriente con uniones temporales de empresas y comunidades de bienes'},
					555: {'name': 'Partidas pendientes de aplicación'},
					556: {
						'name': 'Desembolsos exigidos sobre participaciones del Neto',
						'children': {
							5563: {'name': 'Desembolsos exigidos sobre participaciones del Neto de empresas del grupo'},
							5564: {'name': 'Desembolsos exigidos sobre participaciones del Neto de empresas asociadas'},
							5565: {'name': 'Desembolsos exigidos sobre participaciones del Neto de otras partes vinculadas'},
						}
					},
					557: {'name': 'Dividendo activo a cuenta'},
					558: {
						'name': 'Socios por desembolsos exigidos',
						'children': {
							5580: {'name': 'Socios por desembolsos exigidos sobre acciones o participaciones ordinarias'},
							5585: {'name': 'Socios por desembolsos exigidos sobre acciones o participaciones '
							               'considerados como pasivo financiero.'}
						}
					},
					559: {
						'name': 'Socios financieros a corto plazo',
						'children': {
							5590: {'name': 'Activos por derivados financieros CP, cartera de negociación'},
							5593: {'name': 'Activos por derivados financiers CP, instrumentos de cobertura'},
							5595: {'name': 'Pasivos por derivados financieros CP, cartera de negociación'},
							5598: {'name': 'Pasivos por derivados financieros CP, instrumentos de cobertura'}
						}
					}
				}
			},
			56: {
				'name': 'Fianzas y depósitos recibidos y constituidos a corto plazo y ajustes por periodificación',
				'children': {
					560: {'name': 'Fianzas recibidas a CP'},
					561: {'name': 'Depósitos recibidos a CP'},
					565: {'name': 'Fianzas constituidas a CP'},
					566: {'name': 'Depósitos constituidos a CP'},
					567: {'name': 'Intereses pagados por anticipado'},
					568: {'name': 'Intereses cobrados por anticipado'},
					569: {'name': 'Garantias financieras CP'}
				}
			},
			57: {
				'name': 'Tesorería',
				'children': {
					570: {'name': 'Caja, Euros'},
					571: {'name': 'Caja, Moneda extranjera'},
					572: {'name': 'Bancos e instituciones de crédito c/c ,vista, euros'},
					573: {'name': 'Bancos e instituciones de crédito c/c, vista, moneda extranjera'},
					574: {'name': 'Bancos e instituciones de crédito, cuentas de ahorro, euros'},
					575: {'name': 'Bancos e instituciones de crédito, cuentas de ahorro, moneda extranjera'},
					576: {'name': 'Inversiones a corto plazo de gran liquidez'},
				}
			},
			58: {
				'name': 'Activos no corrienets mantenidos para la venta y activos y pasivos asociados',
				'children': {
					580: {'name': 'Inmovilizado'},
					581: {'name': 'Inversiones con personas y entidades vinculadas'},
					582: {'name': 'Inversiones financieras'},
					583: {'name': 'Existencias, deudores comerciales y otras cuentas a cobrar'},
					584: {'name': 'Otros activos'},
					585: {'name': 'Provisiones'},
					586: {'name': 'Deudas con características especiales'},
					587: {'name': 'Deudas con personas y entidades vinculadas'},
					588: {'name': 'Acreedores comerciales y otras cuentas a pagar'},
					589: {'name': 'Otros pasivos'}
				}
			},
			59: {
				'name': 'Deterioro del valor de inversiones financieras a corto plazo y de activos no corrientes '
				        'mantenidos para la venta',
				'children': {
					593: {
						'name': 'Deterioro de valor de participaciones CP',
						'children': {
							5933: {'name': 'Deterioro de valor de participaciones CP de empresas del grupo'},
							5934: {'name': 'Deterioro de valor de participaciones CP de empresas asociadas'},
							5935: {'name': 'Deterioro de valor de participaciones CP de otras partes vinculadas'},
						}
					},
					594: {
						'name': 'Deterioro de valor de valores representativos de deuda CP de partes vinculadas',
						'children': {
							5943: {'name': 'Deterioro de valor de valores representativos de deuda CP de empresas del grupo'},
							5944: {'name': 'Deterioro de valor de valores representativos de deuda CP de empresas asociadas'},
							5945: {'name': 'Deterioro de valor de valores representativos de deuda CP de otras partes vinculadas'},
						}
					},
					595: {
						'name': 'Deterioro de valor de creditos CP a partes vinculadas',
						'children': {
							5953: {'name': 'Deterioro de valor de créditos CP a empresas del grupo'},
							5954: {'name': 'Deterioro de valor de créditos CP a empresas asociadas'},
							5955: {'name': 'Deterioro de valor de créditos CP a otras partes vinculadas'},
						}
					},
					597: {'name': 'Deterioro de valor de valores representativos de deuda CP'},
					598: {'name': 'Deterioro de valor de créditos CP'},
					599: {
						'name': 'Deterioro de valor de activos no corrientes mantenidos para la venta',
						'children': {
							5990: {'name': 'Deterioro de valor de inmovilizado no corriente mantenido para la venta'},
							5591: {'name': 'Deterioro de valor de inversiones con personas y entidades vinculadas no '
							               'corrientes mantenidas para la venta'},
							5592: {'name': 'Deterioro de valor de inversiones financieras no corrientes mantenidas '
							               'para la venta'},
							5593: {'name': 'Deterioro de valor de existencias, deudores comerciales y otras cuentas '
							               'a cobrar no corrientes mantenidas para la venta'},
							5594: {'name': 'Deterioro de valor de otros activos mantenidos para la venta'},
						}
					}
				}
			}
		}
	},
	6: {
		'name': 'Compras y gastos',
		'children': {
			60: {
				'name': 'Compras',
				'children': {
					600: {'name': 'Compra de mercaderías'},
					601: {'name': 'Compra de materias primas'},
					602: {'name': 'Compra de otros aprovisionamientos'},
					606: {
						'name': 'Descuentos sobre compras por pronto pago de mercaderías',
						'children': {
							6060: {'name': 'Descuentos sobre compras por pronto pago de mercaderías'},
							6061: {'name': 'Descuentos sobre compras por pronto pago de materias primas'},
							6062: {'name': 'Descuentos sobre compras por pronto pago de otros aprovisionamientos'},
						}
					},
					607: {'name': 'Trabajos realizados por otras empresas '},
					608: {
						'name': 'Devoluciones de compras y operaciones similares',
						'children': {
							6080: {'name': 'Devoluciones por compras de mercaderías'},
							6081: {'name': 'Devoluciones por compras de materias primas'},
							6082: {'name': 'Devoluciones por compras de otros aprovisionamientos'},
						}
					},
					609: {
						'name': 'Rappels por compras',
						'children': {
							'6090': {'name': 'Rappels por compras de mercaderías'},
							'6091': {'name': 'Rappels por compras de materias primas'},
							'6092': {'name': 'Rappels por compras de otros aprovisionamientos'},
						}
					},
				}
			},
			61: {
				'name': 'Variación de existencias',
				'children': {
					610: {'name': 'Variación de existencias de mercaderías'},
					611: {'name': 'Variación de materias primas'},
					612: {'name': 'Variación de existencias de otros aprovisionamientos'},
				}
			},
			62: {
				'name': '',
				'children': {
					620: {'name': 'Gastos en Investigación y desarollo'},
					621: {'name': 'Arrendamientos y cánones'},
					622: {'name': 'Reparaciones y conservación'},
					623: {'name': 'Servicios profesionales independientes'},
					624: {'name': 'Transporte'},
					625: {'name': 'Primas de seguro'},
					626: {'name': 'Servicios bancarios y similares'},
					627: {'name': 'Publicidad, propaganda y relaciones publicas.'},
					628: {'name': 'Suministros'},
					629: {'name': 'Otros servicios'}
				}
			},
			63: {
				'name': 'Tributos',
				'children': {
					630: {
						'name': 'Impuestos sobre beneficios',
						'children': {
							6300: {'name': 'Impuesto corriente'},
							6301: {'name': 'Impuesto diferido'},
						}

					},
					631: {'name': 'Otros tributos'},
					634: {
						'name': 'Ajustes negativos en la imposición indirecta',
						'children': {
							6341: {'name': 'Ajustes negativos de IVA de activo corriente'},
							6342: {'name': 'Ajustes negativos en IVA de inversiones'}
						}
					},
					636: {'name': 'Devolucion de impuestos'},
					638: {'name': 'Ajustes positivos en la imposición sobre beneficios'},
					639: {
						'name': 'Ajustes positivos en la imposición indirecta',
						'children': {
							6391: {'name': 'Ajustes positivos de IVA de activo corriente'},
							6392: {'name': 'Ajustes positivos en IVA de inversiones'}
						}
					}
				}
			},
			64: {
				'name': 'Gastos de personal',
				'children': {
					640: {'name': 'Sueldos y salarios'},
					641: {'name': 'Indemnizaciones'},
					642: {'name': 'Seguridad social a cargo de la empresa'},
					643: {'name': 'Retribuciones a largo plazo mediante sistemas de aportación definida'},
					644: {
						'name': 'Retribucion a largo plazo mediante sistemas de prestacion definida',
						'children': {
							6440: {'name': 'Contribuciones anuales'},
							6457: {'name': 'Otros costes'}
						}
					},
					645: {
						'name': 'Retribuciones al personal mediante instrumentos de patrimonio',
						'children': {
							6450: {'name': 'Retribuciones al personal liquidados con instrumentos de patrimonio'},
							6457: {'name': 'Retribuciones al personal liquidados en efectivo basados en instrumentos de patrimonio'}
						}
					},
					649: {'name': 'Otros gastos sociales'}
				}

			},
			65: {
				'name': 'Otros gastos de gestion',
				'children': {
					650: {'name': 'Perdidas de creditos comerciales incobrables'},
					651: {
						'name': 'Resultados de operaciones en comun',
						'children': {
							6510: {'name': 'Beneficio transferido (gestor)'},
							6511: {'name': 'Beneficio transferido (partícipe o asociado no gestor)'}
						}
					},
					659: {'name': 'Otras perdidas de gestion corriente'}
				}
			},
			66: {
				'name': 'Gastos financieros',
				'children': {
					660: {'name': 'Gastos financieros por actualización de provisiones'},
					661: {
						'name': 'Intereses de obligaciones y bonos',
						'children': {
							6610: {'name': 'Intereses de obligaciones y bonos LP, empresas del grupo'},
							6611: {'name': 'Intereses de obligaciones y bonos LP, empresas asociadas'},
							6612: {'name': 'Intereses de obligaciones y bonos LP, otras partes vinculadas'},
							6613: {'name': 'Intereses de obligaciones y bonos LP, otras empresas'},
							6615: {'name': 'Intereses de obligaciones y bonos CP, otras empresas'},
							6616: {'name': 'Intereses de obligaciones y bonos CP, empresas asociadas'},
							6617: {'name': 'Intereses de obligaciones y bonos CP, otras partes vinculadas'},
							6618: {'name': 'Intereses de obligaciones y bonos CP, otras empresas'},
						}
					},
					662: {
						'name': 'Intereses de deudas',
						'children': {
							6620: {'name': 'Intereses de deudas, empresas del grupo'},
							6621: {'name': 'Intereses de deudas, empresas asociadas'},
							6622: {'name': 'Intereses de deudas, otras partes vinculadas'},
							6624: {'name': 'Intereses de deudas, otras empresas'},

						}
					},
					663: {
						'name': 'Perdidas por valoracion de instrumentos financieros por su valor razonable',
						'children': {
							6630: {'name': 'Perdidas de carteras de negociación'},
							6631: {'name': 'Perdidas de designados por la empresa'},
							6632: {'name': 'Perdidas de activos financieros a valor razonable con cambios en el patrimonio neto'},
							6633: {'name': 'Perdidas dde instrumentos de cobertura'},
							6643: {'name': 'Perdidas de otros instrumentos financieros'}
						}
					},
					664: {
						'name': 'Gastos por dividendos de acciones o participaciones consideradas como pasivos financieros',
						'children': {
							6640: {'name': 'Dividendos de pasivos, empresas del grupo'},
							6641: {'name': 'Dividendos de pasivos, empresas asociadas'},
							6642: {'name': 'Dividendos de pasivos, otras partes vinculadas'},
							6643: {'name': 'Dividendos de pasivos, otras empresas'}
						}
					},
					665: {
						'name': 'Intereses por descuento de efectos y operaciones de factoring',
						'children': {
							6650: {'name': 'Intereses por descuento de efectos en entidades de crédito del grupo'},
							6651: {'name': 'Intereses por descuento de efectos en entidades de crédito asociadas'},
							6652: {'name': 'Intereses por descuento de efectos en otras entidades de crédito vinculadas'},
							6653: {'name': 'Intereses por descuento de efectos en otras entidades de crédito'},
							6654: {'name': 'Intereses por operaciones de factoring con entidades de crédito del grupo'},
							6655: {'name': 'Intereses por operaciones de factoring con entidades de crédito asociadas'},
							6656: {'name': 'Intereses por operaciones de factoring con otras entidades de crédito vinculadas'},
							6657: {'name': 'Intereses por operaciones de factoring con otras entidades de crédito'}
						}
					},
					666: {
						'name': 'Perdidas en participaciones y valores representativos de deuda',
						'children': {
							6660: {'name': 'Perdidas en valores representativos de deuda LP, empresas del grupo'},
							6661: {'name': 'Perdidas en valores representativos de deuda LP, empresas asociadas'},
							6662: {'name': 'Perdidas en participaciones y valores representativos de deuda LP, otras partes vinculadas'},
							6663: {'name': 'Perdidas en participaciones y valores representativos de deuda LP, otras empresas'},
							6665: {'name': 'Perdidas en participaciones y valores representativos de deuda CP, empresas del grupo'},
							6666: {'name': 'Perdidas en participaciones y valores representativos de deuda CP, empresas asociadas'},
							6667: {'name': 'Perdidas en valores representativos de deuda CP, otras partes vinculadas'},
							6668: {'name': 'Perdidas en valores representativos de deuda CP, otras partes vinculadas'}
						}
					},
					667: {
						'name': 'Perdidas de créditos no comerciales',
						6670: {'name': 'Perdidas de créditos LP, empresas del grupo'},
						6671: {'name': 'Perdidas de créditos LP, empresas asociadas'},
						6672: {'name': 'Perdidas de créditos LP, otras partes vinculadas'},
						6673: {'name': 'Perdidas de créditos LP, otras empresas'},
						6675: {'name': 'Perdidas de créditos CP, empresas del grupo'},
						6676: {'name': 'Perdidas de créditos CP, empresas asociadas'},
						6677: {'name': 'Perdidas de créditos CP, otras partes vinculadas'},
						6678: {'name': 'Perdidas de créditos CP, otras empresas'}
					},
					668: {'name': 'Diferencias negativas de cambio'},
					669: {'name': 'Otros gastos financieros'}
				}
			},
			67: {
				'name': 'Pérdidas procedentes de activos no corrientes y gastos excepcionales',
				'children': {
					670: {'name': 'Pérdidas procedentes del inmovilizado intangible'},
					671: {'name': 'Pérdidas procedentes del inmovilizado material'},
					672: {'name': 'Pérdidas procedentes de las inversiones inmobiliarias'},
					673: {
						'name': 'Pérdidas procedentes de participaciones LP en partes vinculadas',
						'children': {
							6733: {'name': 'Perdidas procedentes de participaciones LP, empresas del grupo'},
							6734: {'name': 'Perdidas procedentes de participaciones LP, empresas asociadas'},
							6735: {'name': 'Perdidas procedentes de participaciones LP, otras partes vinculadas'}
						}
					},
					675: {'name': 'Perdidas por operaciones con obligaciones propias'},
					678: {'name': 'Gastos excepcionales'}
				}
			},
			68: {
				'name': 'Dotaciones para amortizaciones',
				'children': {
					680: {'name': 'Amortizacion del inmovilizado intangible'},
					681: {'name': 'Amortizacion del inmovilizado material'},
					682: {'name': 'Amortizacion de las inversiones inmobiliarias'},
				}
			},
			69: {
				'name': 'Perdidas por deterioro y otras dotaciones',
				'children': {
					690: {'name': 'Perdidas por deterioro del inmovilizado intangible'},
					691: {'name': 'Perdidas por deterioro del inmovilizado material'},
					692: {'name': 'Perdidas por deterioro de las inversiones inmobiliarias'},
					693: {
						'name': 'Perdidas por deterioro de existencias',
						'children': {
							6930: {'name': 'Pérdidas por deterioro de productos no terminados en curso de fabricación'},
							6931: {'name': 'Perdidas por deterioro de mercaderías'},
							6932: {'name': 'Perdidas por deterioro de materias primas'},
							6933: {'name': 'Perdidas por deterioro de otros aprovisionamientos'}
						}
					},
					694: {'name': 'Perdidas por deterioro de créditos por operaciones comerciales'},
					695: {
						'name': 'Dotación a la provision por operaciones comerciales',
						'children': {
							6954: {'name': 'Dotación a la provision por contratos onerosos'},
							6959: {'name': 'Dotación a la provision para otras operaciones comerciales'}
						}
					},
					696: {
						'name': 'Perdidas por deterioro de participaciones y valores representativos de deuda LP',
						'children': {
							6960: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio '
							               'neto LP, empresas del grupo'},
							6961: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio '
							               'neto LP, empresas asociadas'},
							6962: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio '
							               'neto LP, otras partes vinculadas'},

							6963: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio neto'
							               ' LP, otras empresas'},

							6965: {'name': 'Pérdidas por deterioro en valores representativos deuda LP, empresas del grupo'},
							6966: {'name': 'Perdidas por deterioro en valores representativos deuda LP, empresas asociadas'},
							6967: {'name': 'Perdidas por deterioro en valores representativos deuda LP, otras partes vinculadas'},
							6968: {'name': 'Perdidas por deterioro en valores representativos deuda LP, otras empresas'}
						}
					},
					697: {
						'name': 'Pérdidas por deterioro de créditos LP',
						'children': {
							6970: {'name': 'Pérdidas por deterioro de créditos LP, empresas del grupo'},
							6971: {'name': 'Pérdidas por deterioro de créditos LP, empresas asociadas'},
							6972: {'name': 'Pérdidas por deterioro de créditos LP, otras partes vinculadas'},
							6973: {'name': 'Pérdidas por deterioro de créditos LP, otras empresas'}
						}
					},
					698: {
						'name': 'Pérdidas por deterioro de participaciones y valores representativos de deuda CP',
						'children': {
							6980: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio '
							               'neto CP, empresas del grupo'},
							6981: {'name': 'Pérdidas por deterioro de participaciones en instrumentos de patrimonio '
							               'neto CP, empresas asociadas'},

							6985: {'name': 'Pérdidas por deterioro en valores representativos deuda CP, empresas del grupo'},
							6986: {'name': 'Perdidas por deterioro en valores representativos deuda CP, empresas asociadas'},
							6987: {'name': 'Perdidas por deterioro en valores representativos deuda CP, otras partes vinculadas'},
							6988: {'name': 'Perdidas por deterioro en valores representativos deuda CP, otras empresas'}
						}
					},
					699: {
						'name': 'Perdidas por deterioro de créditos CP',
						'children': {
							6990: {'name': 'Pérdidas por deterioro de créditos CP, empresas del grupo'},
							6991: {'name': 'Pérdidas por deterioro de créditos CP, empresas asociadas'},
							6992: {'name': 'Pérdidas por deterioro de créditos CP, otras partes vinculadas'},
							6993: {'name': 'Pérdidas por deterioro de créditos CP, otras empresas'}
						}
					}
				}
			}
		}
	},
	7: {
		'name': 'Ventas e Ingresos',
		'children': {
			70: {
				'name': 'Ventas de mercaderías, de producción propia, de servicios, etc.',
				'children': {
					700: {'name': 'Ventas de mercaderías'},
					701: {'name': 'Ventas de productos terminados'},
					702: {'name': 'Ventas de productos semiterminados'},
					703: {'name': 'Ventas de subproductos y residuos'},
					704: {'name': 'Ventas de envases y embalajes'},
					705: {'name': 'Prestación de servicios'},
					706: {
						'name': 'Descuentos sobre ventas por pronto pago',
						'children': {
							7060: {'name': 'Descuentos sobre ventas por pronto pago, mercaderías'},
							7061: {'name': 'Descuentos sobre ventas por pronto pago de productos terminados'},
							7062: {'name': 'Descuentos sobre ventas por pronto pago de productos semiterminados'},
							7063: {'name': 'Descuentos sobre ventas por pronto pago de subproductos y residuos'},
						}
					},
					708: {
						'name': 'Devoluciones de ventas y operaciones similares',
						'children': {
							7080: {'name': 'Devoluciones de ventas de mercaderías'},
							7081: {'name': 'Devoluciones de ventas de productos terminados'},
							7082: {'name': 'Devoluciones de ventas de productos semiterminados'},
							7083: {'name': 'Devoluciones de ventas de subproductos y residuos'},
							7084: {'name': 'Devoluciones de ventas de envases y embalajes'},
						}
					},
					709: {
						'name': 'Rappels sobre ventas',
						'children': {
							7090: {'name': 'Rappels sobre ventas de mercaderías'},
							7091: {'name': 'Rappels sobre ventas de productos terminados'},
							7092: {'name': 'Rappels sobre ventas de productos semiterminados'},
							7093: {'name': 'Rappels sobre ventas de subproductos y residuos'},
							7094: {'name': 'Rappels sobre ventas de envases y embalajes'}
						}
					}
				}
			},
			71: {
				'name': 'Variación de existencias',
				'children': {
					710: {'name': 'Variación de existencias de mercaderías'},
					711: {'name': 'Variación de existencias de productos terminados'},
					712: {'name': 'Variación de existencias de productos semiterminados'},
					713: {'name': 'Variación de existencias de subproductos y residuos'}
				}
			},
			73: {
				'name': 'Trabajos realizados para la empresa',
				'children': {
					730: {'name': 'Trabajos realizados para el inmovilizado intangible'},
					731: {'name': 'Trabajos realizados para el inmovilizado material'},
					732: {'name': 'Trabajos realizados en inversiones inmobiliarias'},
					733: {'name': 'Trabajos realizados para el inmovilizado material en curso'},
				}
			},
			74: {
				'name': 'Subvenciones, Donaciones, Legados',
				'children': {
					740: {'name': 'Subvenciones, donaciones, legados a la explotación'},
					746: {'name': 'Subvenciones, donaciones, legados de capital transferidos al resultado del ejercicio'},
					747: {'name': 'Otras subvenciones, donaciones y legados transferidos al resultado del ejercicio'}
				}
			},
			75: {
				'name': 'Otros ingresos de gestión',
				'children': {
					751: {
						'name': 'Resultados de operaciones en común',
						'children': {
							7510: {'name': 'Perdida transferida ( gestor)'},
							7511: {'name': 'Beneficio atribuido ( participe o asociado no gestor)'},
						}
					},
					752: {'name': 'Ingresos por arrendamientos'},
					753: {'name': 'Ingresos por propiedad industrial cedida en explotación'},
					754: {'name': 'Ingresos por comisiones'},
					755: {'name': 'Ingresos por servicios al personal'},
					759: {'name': 'Ingresos por servicios diversos'}
				}
			},

			76: {
				'name': 'Ingresos Financieros',
				'children': {
					760: {
						'name': 'Ingresos de participaciones en instrumentos de patrimonio',
						'children': {
							7600: {'name': 'Ingresos de participaciones en instrumentos de patrimonio, empresas del grupo'},
							7601: {'name': 'Ingresos de participaciones en instrumentos de patrimonio, empresas asociadas'},
							7602: {'name': 'Ingresos de participaciones en instrumentos de patrimonio, otras partes vinculadas'},
							7603: {'name': 'Ingresos de participaciones en instrumentos de patrimonio, otras empresas'}
						}
					},
					761: {
						'name': 'Ingresos de valores representativos de deuda',
						'children': {
							7610: {'name': 'Ingresos de valores representativos de deuda, empresas del grupo'},
							7611: {'name': 'Ingresos de valores representativos de deuda, empresas asociadas'},
							7612: {'name': 'Ingresos de valores representativos de deuda, otras partes vinculadas'},
							7613: {'name': 'Ingresos de valores representativos de deuda, otras empresas'}
						}
					},
					762: {
						'name': 'Ingresos de créditos',
						'children': {
							7620: {
								'name': 'Ingresos de créditos LP',
								'children': {
									76200: {'name': 'Ingresos de créditos LP, empresas del grupo'},
									76201: {'name': 'Ingresos de créditos LP, empresas asociadas'},
									76202: {'name': 'Ingresos de créditos LP, otras partes vinculadas'},
									76203: {'name': 'Ingresos de créditos LP, otras empresas'}
								}
							},
							7621: {
								'name': 'Ingresos de créditos CP',
								'children': {
									76210: {'name': 'Ingresos de créditos CP, empresas del grupo'},
									76211: {'name': 'Ingresos de créditos CP, empresas asociadas'},
									76212: {'name': 'Ingresos de créditos CP, otras partes vinculadas'},
									76213: {'name': 'Ingresos de créditos CP, otras empresas'}
								}
							}
						}
					},
					763: {
						'name': 'Beneficios por valoracion de instrumentos financieros por su valor razonable',
						'children': {
							7630: {'name': 'Beneficios de cartera de negociación'},
							7631: {'name': 'Beneficios de designados por la empresa'},
							7632: {'name': 'Beneficios de activos financieros a valor razonable con cambios en el Neto'},
							7633: {'name': 'Beneficios de instrumentos de cobertura'},
							7634: {'name': 'Beneficios de otros instrumentos financieros'}
						}
					},
					766: {
						'name': 'Beneficios en participaciones y valores representativos de deuda',
						'children': {
							7660: {'name': 'Beneficios en participaciones y valores representativos de deuda LP, empresas del grupo'},
							7661: {'name': 'Beneficios en participaciones y valores representativos de deuda LP, empresas asociadas'},
							7662: {'name': 'Beneficios en participaciones y valores representativos de deuda LP, otras partes vinculadas'},
							7663: {'name': 'Beneficios en participaciones y valores representativos de deuda LP, otras empresas'},

							7665: {'name': 'Beneficios en participaciones y valores representativos de deuda CP, empresas del grupo'},
							7666: {'name': 'Beneficios en participaciones y valores representativos de deuda CP, empresas asociadas'},
							7667: {'name': 'Beneficios en participaciones y valores representativos de deuda CP, otras partes vinculadas'},
							7668: {'name': 'Beneficios en participaciones y valores representativos de deuda CP, otras empresas'}
						}
					},
					767: {'name': 'Ingresos de activos afectos y de derechos de reembolso relativos a retribuciones a largo plazo'},
					768: {'name': 'Diferencias positivas de cambio'},
					769: {'name': 'Otros ingresos financieros'}
				}
			},
			77: {
				'name': 'Beneficios procedentes de activos no corrientes e ingresos excepcionales',
				'children': {
					770: {'name': 'Beneficios procedentes de inmovilizado intangible'},
					771: {'name': 'Beneficios procedentes de inmovilizado material'},
					772: {'name': 'Beneficios procedentes de inversiones inmobiliarias'},
					773: {
						'name': 'Beneficios procedentes de participaciones LP en partes vinculadas',
						'children': {
							7733: {'name': 'Beneficios procedentes de participaciones LP, empresas del grupo'},
							7734: {'name': 'Beneficios procedentes de participaciones LP, empresas asociadas'},
							7735: {'name': 'Beneficios procedentes de participaciones LP, otras partes vinculadas'},
						}
					},
					774: {'name': 'Diferencia negativa en combinaciones de negocios'},
					775: {'name': 'Beneficios por operaciones con obligaciones propias'},
					779: {'name': 'Ingresos excepcionales'}
				}
			},
			79: {
				'name': 'Excesos y aplicaciones de provisiones y de perdidas por deterioro',
				'children': {
					790: {'name': 'Reversión del deterioro del inmovilizado intangible'},
					791: {'name': 'Reversión del deterioro del inmovilizado material'},
					792: {'name': 'Reversion del deterioro del inmovilizado intangible'},
					793: {
						'name': 'Reversión del deterioro de existencias',
						'children': {
							7930: {'name': 'Reversión del deterioro de productos terminados y en curso de fabricación'},
							7931: {'name': 'Reversión del deterioro de mercaderías'},
							7932: {'name': 'Reversión del deterioro de materias primas'},
							7933: {'name': 'Reversión del deterioro de otros aprovisionamientos'}
						}
					},
					794: {'name': 'Reversión del deterioro de créditos por operaciones comerciales'},
					795: {
						'name': 'Exceso de provisiones',
						'children': {
							7950: {'name': 'Exceso de provisión por retribuciones al personal'},
							7951: {'name': 'Exceso de provision para impuestos'},
							7952: {'name': 'Exceso de provision para otras responsabilidades'},
							7954: {
								'name': 'Exceso de provisión por operaciones comerciales',
								'children': {
									79544: {'name': 'Exceso de provisión por contratos onerosos'},
									79549: {'name': 'Exceso de provision para otras operaciones comerciales'},
								}
							},
							7955: {'name': 'Exceso de provisión para actuaciones medioambientales'},
							7956: {'name': 'Exceso de provisión para reestructuraciones'},
							7957: {'name': 'Exceso de provisión por transacciones con pagos basados en instrumentos de patrimonio'},
						}
					},
					796: {
						'name': 'Reversion del deterioro de participaciones y valores representaivos de deuda LP',
						'children': {
							7960: {'name': 'Reversión del deterioro de participaciones en instrumentos de patrimonio Neto LP, empresas del grupo'},
							7961: {'name': 'Reversión del deterioro de participaciones en instrumentos de patrimonio Neto LP, empresas asociadas'},

							7965: {'name': 'Reversión del deterioro de valores representativos de deuda LP, empresas del grupo'},
							7966: {'name': 'Reversión del deterioro de valores representativos de deuda LP, empresas asociadas'},
							7967: {'name': 'Reversión del deterioro de valores representativos de deuda LP, otras partes vinculadas'},
							7968: {'name': 'Reversión del deterioro de valores representativos de deuda LP, otras empresas'}

						}

					},
					797: {
						'name': 'Reversion del deterioro de créditos a largo plazo',
						'children': {
							7970: {'name': 'Reversion del deterioro de créditos LP, empresas del grupo'},
							7971: {'name': 'Reversion del deterioro de créditos LP, empresas asociadas'},
							7972: {'name': 'Reversion del deterioro de créditos LP, otras partes vinculadas'},
							7973: {'name': 'Reversion del deterioro de créditos LP, otras empresas'}
						}
					},
					798: {
						'name': 'Reversion del deterioro de participaciones y valores representativos de deuda CP',
						'children': {
							7980: {'name': 'Reversion del deterioro de participaciones en instrumentos de patrimonio Neto CP, empresas del grupo'},
							7981: {'name': 'Reversion del deterioro de participaciones en instrumentos de patrimonio Neto CP, empresas asociadas'},
							7985: {'name': 'Reversion del deterioro de valores representativos de deuda CP, empresas del grupo'},
							7986: {'name': 'Reversion del deterioro de valores representativos de deuda CP, empresas asociadas'},
							7987: {'name': 'Reversion del deterioro de valores representativos de deuda CP, otras partes vinculadas'},
							7988: {'name': 'Reversion del deterioro de valores representativos de deuda CP, otras empresas'}
						}
					},
					799: {
						'name': 'Reversion del deterioro de créditos a corto plazo',
						'children': {
							7990: {'name': 'Reversion del deterioro de créditos CP, empresas del grupo'},
							7991: {'name': 'Reversion del deterioro de créditos CP, empresas asociadas'},
							7992: {'name': 'Reversion del deterioro de créditos CP, otras partes vinculadas'},
							7993: {'name': 'Reversion del deterioro de créditos CP, otras empresas'}
						}
					}
				}
			}
		}
	},

	8: {
		'name': 'Gastos imputados al Patrimonio Neto',
		'children': {
			80: {
				'name': 'Gastos financieros por valoración de activos y pasivos',
				'children': {
					800: 'Perdidas de activos financieros a valor razonable con cambios en el Patrimonio Neto',
					802: 'Transferencia de beneficios en activos financieros de valor razonable con cambios en el patrimonio Neto'
				}
			},
			81: {
				'name': 'Gastos en operaciones de cobertura',
				'children': {
					810: {'name': 'Pérdidas por coberturas de flujos de efectivo'},
					811: {'name': 'Pérdidas por coberturas de inversiones netas en un negocio extranjero'},
					812: {'name': 'Transferencia de beneficios por coberturas de flujos de efectivo'},
					813: {'name': 'Transferencia de beneficios por coberturas de inversiones netas en un negocio extranjero'}
				}
			},
			82: {
				'name': 'Gastos por diferencias de conversion',
				'children': {
					820: {'name': 'Diferencias de conversion negativas'},
					821: {'name': 'Transferencia de diferencias de conversion positivas'}
				}
			},
			83: {
				'name': 'Impuesto sobre beneficios',
				'children': {
					830: {
						'name': 'Impuesto sobre beneficios',
						'children': {
							8300: {'name': 'Impuesto corriente'},
							8301: {'name': 'Impuesto diferido'}
						}

					},
					833: {'name': 'Ajustes negativos en la imposición sobre beneficios'},
					834: {'name': 'Ingresos fiscales por diferencias permanentes'},
					835: {'name': 'Ingresos fiscales por deducciones'},
					836: {'name': 'Transferencia de diferencias permanentes'},
					837: {'name': 'Transferencia de deducciones y bonificaciones'},
					838: {'name': 'Ajustes positivos en la imposición sobre beneficios'}
				}
			},
			84: {
				'name': 'Transferencias de subvenciones, donaciones y legados',
				'children': {
					840: {'name': 'Transferencias de subvenciones oficiales de capital'},
					841: {'name': 'Transferencias de donaciones y legados de capital'},
					842: {'name': 'Transferencias de otras subvenciones, donaciones y legados'}
				}
			},
			85: {
				'name': 'Gastos por perdidas actuariales y ajustes en los activos por retribuciones a LP de prestacion definida',
				'children': {
					850: {'name': 'Perdidas actuariales'},
					851: {'name': 'Ajustes negativos en activos por retribuciones a LP de prestación definida'}
				}
			},
			86: {
				'name': 'Gastos por activos no corrientes en venta',
				'children': {
					860: {'name': 'Perdidas en activos no corrientes y grupos enajenables de elementos mantenidos para la venta'},
					862: {'name': 'Transferencia de beneficios en activos no corrientes y grupos enajenables de '
					              'elementos mantenidos para la venta'}
				}
			},
			89: {
				'name': 'Gastos de participaciones en empresas del grupo o asociados con ajustes valorativos positivos previos',
				'children': {
					891: {'name': 'Deterioro de participaciones en el patrimonio, empresas del grupo'},
					892: {'name': 'Deterioro de participaciones en el patrimonio, empresas asociadas'}
				}
			}
		}
	},

	9: {
		'name': 'Ingresos imputados al Patrimonio neto',
		'children': {
			90: {
				'name': 'Ingresos financieros por valoración de activos y pasivos',
				'children': {
					900: {'name': 'Beneficios en activos financieros a valor razonable con cambios en el Patrimonio Neto'},
					902: {'name': 'Transferencia de pérdidas en activos financieros de valor razonable con cambios en el patrimonio Neto'}
				}
			},
			91: {
				'name': 'Ingresos en operaciones de cobertura',
				'children': {
					910: {'name': 'Beneficios por coberturas de flujos de efectivo'},
					911: {'name': 'Beneficios por coberturas de una inversion neta en un negocio en el extranjero'},
					912: {'name': 'Transferencias de pérdidas por coberturas de flujos de efectivo'},
					913: {'name': 'Transferencias de pérdidas por coberturas de una inversion neta en un negocio en el extranjero'}
				}
			},
			92: {
				'name': 'Ingresos por diferencias de conversión',
				'children': {
					920: {'name': 'Diferencias de conversiones positivas'},
					921: {'name': 'Transferencia de diferencias de conversión negativas'}
				}
			},
			94: {
				'name': 'Ingresos de subvenciones oficiales de capital',
				'children': {
					940: {'name': 'Ingresos de subvenciones oficiales de capital'},
					941: {'name': 'Ingresos de donaciones y legados de capital'},
					942: {'name': 'Ingresos de otras subvenciones, donaciones, legados'}
				}
			},
			95: {
				'name': 'Ingresos por ganancias actuariales y ajustes en los activos por retribuciones LP de prestación definida',
				'children': {
					950: {'name': 'Ganancias Actuariales'},
					951: {'name': 'Ajustes positivos en activos por retribuciones LP de prestación definida'}
				}
			},
			96: {
				'name': 'Ingresos por activos no corrientes en venta',
				'children': {
					960: {'name': 'Beneficios en activos no corrientes y grupos enajenables de elementos mantenidos para la venta'},
					962: {'name': 'Transferencia de pérdidas en activos no corrientes y grupos enajenables de '
					              'elementos mantenidos para la venta'}
				}
			},
			99: {
				'name': 'Ingresos de participaciones en empresas del grupo o asociadas con ajustes valorativos negativos previos',
				'children': {
					991: {'name': 'Recuperación de ajustes valorativos negativos previos, empresas del grupo'},
					992: {'name': 'Recuperación de ajustes valorativos negativos previos, empresas asociadas'},
					993: {'name': 'Transferencia por deterioro de ajustes valorativos negativos previos, empresas del grupo'},
					994: {'name': 'Transferencia por deterioro de ajustes valorativos negativos previos, empresas asociadas'}
				}
			}
		}
	}
}


def save_accounts(accounts, parent=None):
	for group, accounts in accounts.items():
		try:
			account = Account(code=group, name=accounts['name'], parent=parent)
			session.add(account)
			save_accounts(accounts['children'], parent=account)
		except (KeyError, TypeError):
			continue


def create_initial_balance():
	pass


if __name__ == '__main__':

	save_accounts(ACCOUNTS)
	session.commit()
