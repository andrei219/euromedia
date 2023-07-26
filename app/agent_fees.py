
import typing

from datetime import datetime

from ui_agent_fees import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex

from db import session, Agent

class AgentModel(QAbstractListModel):

    def __init__(self):
        super().__init__()
        self.agents: typing.List[Agent] = session.query(Agent).all()

    def rowCount(self, index: QModelIndex) -> int:
        return len(self.agents)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return

        if role == Qt.DisplayRole:
            agent = self.agents[index.row()]
            return agent.fiscal_name + (f' - {agent.fiscal_number}' if agent.fiscal_number else '')


class Form(Ui_Dialog, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.model = AgentModel()
        self.view.setModel(self.model)

        self._export.clicked.connect(self.export_handler)
        self._init_from_to_fields()

    def _init_from_to_fields(self):
        self.to.setText(datetime.today().strftime('%d%m%Y'))
        self._from.setText(f'0101{datetime.now().year}')

    def export_handler(self):
        print('clicked export')


if __name__ == '__main__':

    for agent in session.query(Agent):
        print('agent=', agent)
        agent.from_profit_purchase = True
        agent.from_profit_sale = True
        agent.from_turnover_purchase = True
        agent.from_turnover_sale = True
        agent.fixed_perpiece_purchase = True
        agent.fixed_perpiece_sale = True

    session.commit()
