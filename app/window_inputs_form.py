

from ui_window_inputs_form import Ui_Dialog


from PyQt5.QtWidgets import QDialog, QMessageBox

import utils


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

    if start_date_parsed > end_date_parsed:
        return False, "Start date must be before end date"

    if end_date_parsed > utils.get_current_date():
        return False, "End date must be before current date"

    return True, ""

class Form(Ui_Dialog, QDialog):
    def __init__(self, parent):
        super(Form, self).__init__(parent=parent)
        self.setupUi(self)

        self.start.setText(utils.get_current_year_first_date())
        self.end.setText(utils.get_current_month_last_date())

        self.run.clicked.connect(self.run_handler)
        self.exit.clicked.connect(self.close)

    def run_handler(self):

        is_valid, error_message = validate_inputs(
            self.start.text(),
            self.end.text(),
            self.default_rate.text()
        )

        if not is_valid:
            QMessageBox.critical(self, 'Error', error_message)
            return


        start_date = self.start.text()
        end_date = self.end.text()
        default_rate = float(self.default_rate.text())

        utils.run_report(start_date, end_date, default_rate, utils.collect_args_file_path())


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    form = Form(None)
    form.show()
    sys.exit(app.exec_())
    