"""set condition_eq_target_if_not_target

Revision ID: 33f713f8b5ab
Revises: b81d335db009
Create Date: 2023-02-21 13:38:54.465336

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from app.db import WhIncomingRmaLine


# revision identifiers, used by Alembic.
revision = '33f713f8b5ab'
down_revision = 'b81d335db009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Irreversible migration. Original values cannot be preserved.
    Backup created before running this upgrade: 21022023 at 13:50. """

    Session = sessionmaker(bind=op.get_bind())
    session = Session()

    lines = session.query(WhIncomingRmaLine).where(WhIncomingRmaLine.target_condition=='').all()

    for line in lines:
        line.target_condition = line.condition

    session.commit()


def downgrade() -> None:
    pass
