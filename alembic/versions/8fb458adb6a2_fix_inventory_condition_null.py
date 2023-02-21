"""fix_inventory_condition_null

Revision ID: 8fb458adb6a2
Revises: 33f713f8b5ab
Create Date: 2023-02-21 14:00:12.749032

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app.db import Imei


# revision identifiers, used by Alembic.
revision = '8fb458adb6a2'
down_revision = '33f713f8b5ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Irreversible migration. Original values cannot be preserved.
       Backup created before running this upgrade: 21022023 at 13:50. """

    imei_condition_map = {
        '357463525650247': 'AB',
        '353039110585198': 'AB/LCD A+',
        '350765871333369': 'A+/A',
        '353039113726906': 'AB',
        '354842977410288': 'A+/A',
        '353051110201445': 'AB'
    }

    Session = sessionmaker(bind=op.get_bind())
    session = Session()

    for imei, condition in imei_condition_map.items():
        ''' Emit update statement for each imei using update() method. '''
        session.query(Imei).filter(Imei.imei == imei).update({Imei.condition: condition})

    session.commit()
    

def downgrade() -> None:
    pass
