


from PyQt5.QtWidgets import QDialog, QMessageBox

from ui_inventory_form import Ui_InventoryForm

from models import InventoryModel

import utils 

def prepare_filters_dict(filters):
    filters = {k: v for k, v in filters.items() if v}

    if 'date' not in filters:
        raise ValueError('Date must be provided')
    else:
        try:
            filters['date'] = utils.parse_date(filters['date']).date()
        except ValueError:
            raise ValueError('Incorrect date format: ddmmyyyy')

    if 'description' in filters:
        description = filters['description']

        try:
            item_id = utils.description_id_map[description]
        except KeyError:
            if 'Mixed' in description:
                ids = utils.get_itemids_from_mixed_description(description)
            else:
                ids = utils.get_items_ids_by_keyword(description)
            filters['item_ids'] = ids
        else:
            filters['item_ids'] = [item_id]

        del filters['description']

    if 'warehouse' in filters:
        try:
            filters['warehouse_id'] = utils.warehouse_id_map[filters['warehouse']]
        except KeyError:
            pass

        del filters['warehouse']

    # Delete from dict if no value are provided:
    filters = {k: v for k, v in filters.items() if v}

    return filters


class InventoryForm(Ui_InventoryForm, QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent) 
        self.setupUi(self)
        self.model = None

        self.apply.clicked.connect(self.apply_handler)
        self.excel.clicked.connect(self.excel_handler) 

        self.set_completers()

        self.date.setText(utils.today_date())
        self.description.setFocus()

    def set_completers(self):
        for field, data in [
            (self.description, utils.descriptions),
            (self.condition, utils.conditions), 
            (self.spec, utils.specs), 
            (self.warehouse, utils.warehouse_id_map.keys())
        ]:
            utils.setCompleter(field, data) 
   
    def excel_handler(self):
        from utils import get_file_path

        if self.model is None:
            return 
        
        file_path = get_file_path(self)
        
        if not file_path:
            return

        try:
            self.model.export(file_path)
        except:
            QMessageBox.information(self, 'Error', 'An error occurred while exporting data')
        else:
            QMessageBox.information(self, 'Information', 'Data exported successfully')

    def apply_handler(self):
        try:
            filters = self.build_filters_dict()
        except ValueError as ex:
            QMessageBox.critical(self, 'Error', str(ex))
            return

        self.model = InventoryModel(filters)
        self.total.setText('Total: ' + str(self.model.total))
        self.view.setModel(self.model)
        self.view.resizeColumnToContents(1)

        self.view.selectionModel().selectionChanged.connect(self.selection_changed)

    def selection_changed(self):
        indexes = self.view.selectedIndexes()
        self.selected.setText(
            'Selected: ' + str(
                sum(
                    self.model[r].quantity
                    for r in {
                        index.row() for index in indexes
                    }

                )
            )
        )

    def build_filters_dict(self):
        return prepare_filters_dict(
            {
                'serie': self.serie.text(),
                'description': self.description.text().strip(),
                'condition': self.spec.text().strip(),
                'spec': self.condition.text().strip(),
                'warehouse': self.warehouse.text().strip(),
                'date': self.date.text(),
                'include_no_series': self.include_no_serie.isChecked()
            }
        )


