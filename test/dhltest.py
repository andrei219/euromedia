from python_dhl.service import DHLService
from python_dhl.resources.address import DHLContactInformation
from python_dhl.resources.address import DHLPostalAddress
from python_dhl.resources.helper import ShipperType
from python_dhl.resources.helper import TypeCode
from python_dhl.resources.address import DHLRegistrationNumber
from python_dhl.resources.helper import next_business_day

from python_dhl.resources.shipment import DHLProduct

# Euromedia export 301920854
# Soapside export 313048052

DHL_API_KEY = 'apA5lA5eR5aA0n'
DHL_API_SECRET = 'X^9cO$7gW#5gU@1e'
DHL_ACCOUNT = ''
DHL_ACCOUNT_IMPORT = ''
DHL_ACCOUNT_EXPORT = '301920854'

if __name__ == '__main__':

    service = DHLService(DHL_API_KEY, DHL_API_SECRET, DHL_ACCOUNT_EXPORT, test_mode=True)

    sender_contact = DHLContactInformation(
        full_name='Euromedia Investment Group, S.L.',
        phone='+34633333973',
        contact_type=ShipperType.BUSINESS.value,
        email='administracion@euromediagroup.es'
    )

    sender_address = DHLPostalAddress(
        street_line1='Calle Camino Real 22 Bajo Izq.',
        city_name='Torrente',
        postal_code='46900',
        country_code='ES',
        county_name='Valencia',
    )

    registration_numbers = [
        DHLRegistrationNumber(
            type_code=TypeCode.VAT.name,
            number='B98815608',
            issuer_country_code='ES'
        )
    ]

    receiver_contact = DHLContactInformation(
        full_name='Circular Consulting',
        phone='+32471060469',
        contact_type=ShipperType.BUSINESS,
        company_name='Circular Consulting'
    )

    receiver_address = DHLPostalAddress(
        street_line1='Avenue Louise 207',
        postal_code='1050',
        country_code='BE',
        city_name='Bruxelles',
    )

    product = DHLProduct(
        weight=8,
        height=40,
        length=30,
        width=26
    )

    import datetime
    import pytz

    shipment_date = datetime.datetime(2022, 6, 27, 16, 30, 0, 0, pytz.UTC)

    response = service.get_rates(
        sender=sender_address,
        receiver=receiver_address,
        product=product,
        shipment_date=shipment_date

    )

    for product in response.products:
        print(product)


import requests

url = "https://api-mock.dhl.com/mydhlapi/rates"

payload = {
    "customerDetails": {
        "shipperDetails": {
            "postalCode": "14800",
            "cityName": "Prague",
            "countryCode": "CZ",
            "provinceCode": "CZ",
            "addressLine1": "addres1",
            "addressLine2": "addres2",
            "addressLine3": "addres3",
            "countyName": "Central Bohemia"
        },
        "receiverDetails": {
            "postalCode": "14800",
            "cityName": "Prague",
            "countryCode": "CZ",
            "provinceCode": "CZ",
            "addressLine1": "addres1",
            "addressLine2": "addres2",
            "addressLine3": "addres3",
            "countyName": "Central Bohemia"
        }
    },
    "accounts": [
        {
            "typeCode": "shipper",
            "number": "123456789"
        }
    ],
    "productCode": "P",
    "localProductCode": "P",
    "valueAddedServices": [
        {
            "serviceCode": "II",
            "localServiceCode": "II",
            "value": 100,
            "currency": "GBP",
            "method": "cash"
        }
    ],
    "productsAndServices": [
        {
            "productCode": "P",
            "localProductCode": "P",
            "valueAddedServices": [
                {
                    "serviceCode": "II",
                    "localServiceCode": "II",
                    "value": 100,
                    "currency": "GBP",
                    "method": "cash"
                }
            ]
        }
    ],
    "payerCountryCode": "CZ",
    "plannedShippingDateAndTime": "2020-03-24T13:00:00GMT+00:00",
    "unitOfMeasurement": "metric",
    "isCustomsDeclarable": False,
    "monetaryAmount": [
        {
            "typeCode": "declaredValue",
            "value": 100,
            "currency": "CZK"
        }
    ],
    "requestAllValueAddedServices": False,
    "returnStandardProductsOnly": False,
    "nextBusinessDay": False,
    "productTypeCode": "all",
    "packages": [
        {
            "typeCode": "3BX",
            "weight": 10.5,
            "dimensions": {
                "length": 25,
                "width": 35,
                "height": 15
            }
        }
    ]
}
headers = {
    "content-type": "application/json",

    "Message-Reference": "SOME_STRING_VALUE",
    "Message-Reference-Date": "SOME_STRING_VALUE",
    "Plugin-Name": "SOME_STRING_VALUE",
    "Plugin-Version": "SOME_STRING_VALUE",
    "Shipping-System-Platform-Name": "SOME_STRING_VALUE",
    "Shipping-System-Platform-Version": "SOME_STRING_VALUE",
    "Webstore-Platform-Name": "SOME_STRING_VALUE",
    "Webstore-Platform-Version": "SOME_STRING_VALUE",

    "Authorization": "Basic REPLACE_BASIC_AUTH"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)
