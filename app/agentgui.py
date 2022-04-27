

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QModelIndex

from ui_agentgui import Ui_AgentGui

from db import Agent, AgentDocument

import utils

class AgentGui(QWidget, Ui_AgentGui):
    
    EDITABLE_MODE, NEW_MODE = 0, 1  

    def __init__(self, parent, view, index=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.model = view.model() 

        self.bank_country_combobox.addItems(utils.countries)
        self.agent_country_combobox.addItems(utils.countries)
        
        if index:
            self.mode = AgentGui.EDITABLE_MODE   
            self.agent = self.model.agents[index.row()]
            self.agentToForm()
        else:
            self.mode = AgentGui.NEW_MODE
            self.agent = Agent() 
            self.docs_button.setToolTip('Save agent to enable attaching documents')
            self.docs_button.setToolTipDuration(2000)
            self.docs_button.setEnabled(False)
            self.agent = Agent() 
        
        self.docs_button.clicked.connect(self.docsButtonHandler)
        self.save_button.clicked.connect(self.saveButtonHandler)
        self.iban_line_edit.textChanged.connect(self.ibanHandler)

    def ibanHandler(self, text):
        if utils.validIban(text):
            self.swift_line_edit.setText(utils.swiftFromIban(text))        

    def docsButtonHandler(self):
        from documents_form import Form
        f = Form(self, self.agent)
        f.exec_()


    def saveButtonHandler(self): 
        if self.mode == AgentGui.NEW_MODE:
            self.formToAgent() 
            try:
                self.model.add(self.agent)
                self.mode = AgentGui.EDITABLE_MODE
                self.agent_code_line_edit.setText(str(self.agent.id))
                self.docs_button.setEnabled(True)
                self.docs_button.setToolTipDuration(0)
                QMessageBox.information(self, 'Agent - Create ', 'Agent Created Successfully')

            except:
                # raise
                QMessageBox.critical(self, 'Agent - Update ','Fields fiscal name, name and email are mandatory' )  

        elif self.mode == AgentGui.EDITABLE_MODE:
            try:
                self.formToAgent() 
                self.model.update(self.agent)
                QMessageBox.information(self, 'Agent - Update ', 'Agent updated successfully') 
            except:
                raise
                # QMessageBox.critical(self, 'Agent - Update', 'Fields fiscal name, name and email are mandatory')
    
    def formToAgent(self):
            self.agent.fiscal_name = self.fiscal_name_line_edit.text()
            self.agent.fiscal_number = self.fiscal_number_line_edit.text()
            self.agent.phone = self.phone_number_line_edit.text()
            self.agent.email = self.email_line_edit.text()
            self.agent.country = self.agent_country_combobox.currentText() 
            self.agent.active = self.active_checkbox.isChecked()
            
            self.agent.fixed_salary = self.fixed_salary_spinbox.value()
            self.agent.from_profit = self.from_profit_spinbox.value()
            self.agent.from_turnover = self.from_turnover_spinbox.value()
            self.agent.fixed_perpiece = self.fixed_per_piece_spinbox.value()
            self.agent.bank_name = self.bank_name_line_edit.text()
            self.agent.bank_address = self.address_line_edit.text() 
            self.agent.iban = self.iban_line_edit.text()
            self.agent.swift = self.swift_line_edit.text() 
            self.agent.bank_postcode = self.postcode_line_edit.text() 
            self.agent.bank_city = self.city_line_edit.text()
            self.agent.bank_state = self.state_line_edit.text()
            self.agent.bank_country = self.bank_country_combobox.currentText()  
            self.agent.bank_routing = self.routing.text()

    def agentToForm(self):
        self.agent_code_line_edit.setText(str(self.agent.id))
        self.active_checkbox.setChecked(self.agent.active)
        self.fiscal_number_line_edit.setText(self.agent.fiscal_number)
        self.fiscal_name_line_edit.setText(self.agent.fiscal_name)
        self.email_line_edit.setText(self.agent.email)
        self.phone_number_line_edit.setText(self.agent.phone)
        self.agent_country_combobox.setCurrentText(self.agent.country)

        if self.agent.fixed_salary:
            self.fixed_salary_spinbox.setValue(self.agent.fixed_salary)
        if self.agent.from_profit:
            self.from_profit_spinbox.setValue(self.agent.from_profit)
        if self.agent.from_turnover:
            self.from_turnover_spinbox.setValue(self.agent.from_turnover)
        if self.agent.fixed_perpiece:
            self.fixed_per_piece_spinbox.setValue(self.agent.fixed_perpiece)
        if self.agent.bank_name:
            self.bank_name_line_edit.setText(self.agent.bank_name)
        if self.agent.iban:
            self.iban_line_edit.setText(self.agent.iban)
        if self.agent.swift:
            self.swift_line_edit.setText(self.agent.swift)
        if self.agent.bank_address:
            self.address_line_edit.setText(self.agent.bank_address)
        if self.agent.bank_postcode:
            self.postcode_line_edit.setText(self.agent.bank_postcode)
        if self.agent.bank_city:
            self.city_line_edit.setText(self.agent.bank_city)
        if self.agent.bank_state:
            self.state_line_edit.setText(self.agent.bank_state)
        if self.agent.bank_country:
            self.bank_country_combobox.setCurrentText(self.agent.bank_country)
        if self.agent.bank_routing:
            self.routing.setText(self.agent.bank_routing)

    def closeEvent(self, event):
        try:
            self.parent.opened_windows_classes.remove(self.__class__)
            # self.parent.opened_windows_instances.remove(self)
        except KeyError:
            pass 
            