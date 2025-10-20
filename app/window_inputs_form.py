

from ui_window_inputs_form import Ui_Dialog


from PyQt5.QtWidgets import QDialog, QMessageBox

import utils
import window_inputs_model as model 

def validate_inputs(start_date: str, end_date: str, default_rate_str: str) -> tuple[bool, str]:
    try:
        default_rate = float(default_rate_str)
    except ValueError:
        return False, "Invalid default rate"

    try:
        start_date_parsed = utils.parse_date(start_date)
    except ValueError:
        return False, "Invalid start date"

    try:
        end_date_parsed = utils.parse_date(end_date)
    except ValueError:
        return False, "Invalid end date"

    return True, ""


class Form(Ui_Dialog, QDialog):
    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)

        self.start.setText(utils.get_current_year_first_date())
        self.end.setText(utils.get_current_month_last_date())

        self.run.clicked.connect(self.run_handler)
        self.exit.clicked.connect(self.close)


    def collect_inputs(self) -> tuple[str, str, float]:
        start_date = self.start.text().strip()
        end_date = self.end.text().strip()
        default_rate = float(self.rate.text().strip())
        return start_date, end_date, default_rate


    def run_handler(self):

        is_valid, error_message = validate_inputs(
            self.start.text(),
            self.end.text(),
            self.rate.text()
        )

        if not is_valid:
            QMessageBox.critical(self, 'Error', error_message)
            return

        start_date, end_date, default_rate = self.collect_inputs()

        try:
            model.run_report(
                start_date,
                end_date,
                default_rate,
                utils.get_file_path(self),
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
            return

        QMessageBox.information(self, 'Success', 'Report created successfully')


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    form = Form(None)
    form.show()
    sys.exit(app.exec_())
    