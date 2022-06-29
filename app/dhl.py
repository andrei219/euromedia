from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QAbstractTableModel

from ui_dhl import Ui_Dialog

from models import BaseTable


class Table(BaseTable, QAbstractTableModel):

    def __init__(self):
        pass


class Form(Ui_Dialog, QDialog):

    def __init__(self, parent, expedition):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)
        self.connect_handlers()

    def connect_handlers(self):
        self.no_batteries.toggled.connect(self.no_batteries_toggled)
        self.yes_batteries.toggled.connect(self.yes_batteries_toggled)

    def yes_batteries_toggled(self, flag):
        self.no_batteries.setChecked(not flag)

    def no_batteries_toggled(self, flag):
        self.yes_batteries.setChecked(not flag)

    def calculate_handler(self):
        pass

    def create_handler(self):
        pass

if __name__ == '__main__':

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
