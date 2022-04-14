

# from suds.client import Client


from  zeep import  Client

if __name__ == '__main__':

    wsdl_url = 'https://www.agenciatributaria.es/static_files/AEAT/Contenidos_Comunes/La_Agencia_Tributaria' \
               '/Modelos_y_formularios/Suministro_inmediato_informacion/FicherosSuministros/V_1_1' \
               '/SuministroFactEmitidas.wsdl'

    location = "https://www7.aeat.es/wlpl/SSII-FACT/ws/fe/SiiFactFEV1SOAP"

    client = Client(wsdl_url)

    # client.service._binding_options['address'] = location


    data = {

        'Cabecera': {

            'IDVersionSii': '1.1',

            'Titular': {

                'NombreRazon': 'Euromedia Investment Group',

                'NIF':'B98815608',
            },

            'TipoComunicacion': 'A0',


        },
        'RegistroLRFacturasEmitidas': {

            'PeriodoLiquidacion':{

                'Ejercicio':2022,

                'Periodo':4

            },

            'IDFactura':{

                'IDEmisorFactura':{

                    'NIF':'B98815608'
                },

                'NumSerieFacturaEmisor':'1-00001',

                'FechaExpedicionFacturaEmisor':'22-10-2021',

            },

            'FacturaExpedida':{

                'TipoFactura':'1',

                'ClaveRegimenEspecialOTrascendencia':'01',

                'DescripcionOperacion':'Venta de cosas',

                'TipoDesglose':{
                    'DesgloseFactura':{

                        'Sujeta':{

                            'NoExenta':{
                                'TipoNoExenta':'S1',
                                'DesgloseIVA':{
                                    'DetalleIVA':{
                                        'BaseImponible':120
                                    }
                                }
                            }
                        }
                    },
                }
            },
        }
    }

    client.service.SuministroLRFacturasEmitidas(**data)
    