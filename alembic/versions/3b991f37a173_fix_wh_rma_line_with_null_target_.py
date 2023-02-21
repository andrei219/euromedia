"""fix wh_rma_line with null target condition

Revision ID: 3b991f37a173
Revises: 8fb458adb6a2
Create Date: 2023-02-21 15:39:40.563534

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker
from app.db import WhIncomingRmaLine

# revision identifiers, used by Alembic.
revision = '3b991f37a173'
down_revision = '8fb458adb6a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Irreversible migration. Original values cannot be preserved.
        Backup created before running this upgrade: 21022023 at 13:50. """
    Session = sessionmaker(bind=op.get_bind())
    session = Session()

    ''' Update target condition to condition if target condition is null. '''
    session.query(
        WhIncomingRmaLine
    ).where(
        WhIncomingRmaLine.target_condition == None
    ).update(
        {WhIncomingRmaLine.target_condition: WhIncomingRmaLine.condition}
    )

    session.commit()

def downgrade() -> None:
    pass
