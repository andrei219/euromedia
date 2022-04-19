# from suds.client import Client

from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml import etree

wsdl_url = 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii_1_1/fact/ws/SuministroFactEmitidas.wsdl'


location = "https://www7.aeat.es/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP"

history = HistoryPlugin()
client = Client(
    wsdl_url,
    plugins=[history]
)



data = {
    'Cabecera': {
        'IDVersionSii': '1.1',
        'Titular': {
            'NombreRazon': 'Euromedia Investment Group S.L',
            'NIF': 'B98815608'
        },
        'TipoComunicacion': 'A0'
    },
    'RegistroLRFacturasEmitidas': {
        'PeriodoLiquidacion': {
            'Ejercicio': '2022',
            'Periodo': '04'
        },
        'IDFactura': {
            'IDEmisorFactura': {
                'NIF': 'B98815608'
            },
            'NumSerieFacturaEmisor': '1-000001',
            'FechaExpedicionFacturaEmisor': '22-10-2021'
        },
        'FacturaExpedida': {
            'TipoFactura': 'F1',
            'ClaveRegimenEspecialOTrascendencia': '01',
            'DescripcionOperacion': 'Venta de móviles y accesorios',
            'Contraparte': {
                'NombreRazon': 'Cliente xyz',
                'NIF': '1234213123213214213'
            },
            'TipoDesglose': {
                'DesgloseFactura': {
                    'Sujeta': {
                        'NoExenta': {
                            'TipoNoExenta': 'S1',
                            'DesgloseIVA': {
                                'DetalleIVA': {
                                    'BaseImponible': '120'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# client.service.SuministroLRFacturasEmitidas(**data)

client.service.SuministroLRFacturasEmitidas(
    Cabecera={
        'IDVersionSii': '1.1',
        'Titular': {
            'NombreRazon': 'Euromedia Investment Group S.L',
            'NIF': 'B98815608'
        },
        'TipoComunicacion': 'A0'
    },
    RegistroLRFacturasEmitidas={
        'PeriodoLiquidacion': {
            'Ejercicio': '2022',
            'Periodo': '04'
        },
        'IDFactura': {
            'IDEmisorFactura': {
                'NIF': 'B98815608'
            },
            'NumSerieFacturaEmisor': '1-00001',
            'FechaExpedicionFacturaEmisor': '22-10-2021'
        },
        'FacturaExpedida': {
            'TipoFactura': 'F1',
            'ClaveRegimenEspecialOTrascendencia': '01',
            'DescripcionOperacion': 'Venta de móviles y accesorios',
            'Contraparte': {
                'NombreRazon': 'Cliente xyz',
                'NIF': 'B40685608'
            },
            'TipoDesglose': {
                'DesgloseFactura': {
                    'Sujeta': {
                        'NoExenta': {
                            'TipoNoExenta': 'S1',
                            'DesgloseIVA': {
                                'DetalleIVA': {
                                    'BaseImponible': 120
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)

print(history.last_sent)

print('NEVER REACHED')


import lxml

# from dict2xml import dict2xml
#
#
#
# print(dict2xml(data))
