"""add weight field

Revision ID: 91dd70cb68c7
Revises: 3b991f37a173
Create Date: 2023-03-03 10:35:47.878606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91dd70cb68c7'
down_revision = '3b991f37a173'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'weight')
    # ### end Alembic commands ###