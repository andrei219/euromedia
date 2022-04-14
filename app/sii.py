# from suds.client import Client

from zeep import Client
from zeep.plugins import HistoryPlugin


# wsdl_url = 'https://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria' \
#            '/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_1_1' \
#            '/SuministroFactEmitidas.wsdl'

wsdl_url = 'https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii_1_1/fact/ws/SuministroFactEmitidas.wsdl'


location = "https://www7.aeat.es/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP"

history = HistoryPlugin()




client = Client(
    wsdl_url,
    plugins=[history],
)


#
# client = Client(wsdl_url, plugins=[MessagePlugin()])

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
            'Periodo': '4'
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
            'DescripcionOperacion': 'Operacion Nacional',
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
            'DescripcionOperacion': 'Operacion Nacional',
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

# print(history.last_sent)


# from dict2xml import dict2xml
#
#
#
# print(dict2xml(data))


#
# import requests
#
# url="https://www7.aeat.es/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP"
#
#
# headers = {'content-type': 'application/soap+xml'}
#
# # headers = {'content-type': 'text/xml'}
#
# body = """<?xml version="1.0" encoding="UTF-8"?>
# <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
# xmlns:siiLR="https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroLR.xsd"
# xmlns:sii="https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroInformacion.xsd">
#  <soapenv:Header/>
#  <soapenv:Body>
#  <siiLR:SuministroLRFacturasEmitidas>
#  <sii:Cabecera>
#  <sii:IDVersionSii>1.0</sii:IDVersionSii>
#  <sii:Titular>
#  <sii:NombreRazon>Euromedia Investment Group, S.L.</sii:NombreRazon>
#  <sii:NIF>B98815608</sii:NIF>
#  </sii:Titular>
#  <sii:TipoComunicacion>A0</sii:TipoComunicacion>
#  </sii:Cabecera>
#  <siiLR:RegistroLRFacturasEmitidas>
#  <sii:PeriodoLiquidacion>
#  <sii:Ejercicio>2022</sii:Ejercicio>
#  <sii:Periodo>05</sii:Periodo>
#  </sii:PeriodoLiquidacion>
#  <siiLR:IDFactura>
#  <sii:IDEmisorFactura>
#  <sii:NIF>A84532501</sii:NIF>
#  </sii:IDEmisorFactura>
#  <sii:NumSerieFacturaEmisor>01</sii:NumSerieFacturaEmisor>
#  <sii:FechaExpedicionFacturaEmisor>10-05-2017</sii:FechaExpedicionFacturaEmisor>
#  </siiLR:IDFactura>
#  <siiLR:FacturaExpedida>
#  <sii:TipoFactura>F1</sii:TipoFactura>
#  <sii:ClaveRegimenEspecialOTrascendencia>01</sii:ClaveRegimenEspecialOTrascendencia>
#  <sii:ImporteTotal>26.70</sii:ImporteTotal>
#  <sii:DescripcionOperacion>VentaXXXXXXX</sii:DescripcionOperacion>
#  <sii:Contraparte>
#  <sii:NombreRazon>EMPRESAYYYYYYYY</sii:NombreRazon>
#  <sii:NIF>94234500B</sii:NIF>
#  </sii:Contraparte>
#  <sii:TipoDesglose>
#  <sii:DesgloseFactura>
#  <sii:Sujeta>
#  <sii:NoExenta>
#  <sii:TipoNoExenta>S1</sii:TipoNoExenta>
#  <sii:DesgloseIVA>
#  <sii:DetalleIVA>
#  <sii:TipoImpositivo>21</sii:TipoImpositivo>
#  <sii:BaseImponible>22.07</sii:BaseImponible>
#  <sii:CuotaRepercutida>4.63</sii:CuotaRepercutida>
#  </sii:DetalleIVA>
#  </sii:DesgloseIVA>
#  </sii:NoExenta>
#  </sii:Sujeta>
#  </sii:DesgloseFactura>
#  </sii:TipoDesglose>
#  </siiLR:FacturaExpedida>
#  </siiLR:RegistroLRFacturasEmitidas>
#  <siiLR:RegistroLRFacturasEmitidas>
#  <sii:PeriodoLiquidacion>
#  <sii:Ejercicio>2017</sii:Ejercicio>
#  <sii:Periodo>05</sii:Periodo>
#  </sii:PeriodoLiquidacion>
#  <siiLR:IDFactura>
#  <sii:IDEmisorFactura>
#  <sii:NIF>A84532501</sii:NIF>
#  </sii:IDEmisorFactura>
#  <sii:NumSerieFacturaEmisor>02</sii:NumSerieFacturaEmisor>
#  <sii:FechaExpedicionFacturaEmisor>10-05-2017</sii:FechaExpedicionFacturaEmisor>
# </siiLR:IDFactura>
#  <siiLR:FacturaExpedida>
#  <sii:TipoFactura>F2</sii:TipoFactura>
#  <sii:ClaveRegimenEspecialOTrascendencia>01</sii:ClaveRegimenEspecialOTrascendencia>
#  <sii:ImporteTotal>50</sii:ImporteTotal>
#  <sii:DescripcionOperacion> VentaYYYYYYY</sii:DescripcionOperacion>
#  <sii:TipoDesglose>
#  <sii:DesgloseFactura>
#  <sii:Sujeta>
#  <sii:NoExenta>
#  <sii:TipoNoExenta>S1</sii:TipoNoExenta>
#  <sii:DesgloseIVA>
#  <sii:DetalleIVA>
#  <sii:TipoImpositivo>21</sii:TipoImpositivo>
#  <sii:BaseImponible>10</sii:BaseImponible>
#  <sii:CuotaRepercutida>2.1</sii:CuotaRepercutida>
#  </sii:DetalleIVA>
#  </sii:DesgloseIVA>
#  </sii:NoExenta>
#  </sii:Sujeta>
#  </sii:DesgloseFactura>
#  </sii:TipoDesglose>
#  </siiLR:FacturaExpedida>
#  </siiLR:RegistroLRFacturasEmitidas>
#  </siiLR:SuministroLRFacturasEmitidas>
#  </soapenv:Body>
# </soapenv:Envelope>"""
#
# response = requests.post(url, data=body, headers=headers)
# print(response.content)
