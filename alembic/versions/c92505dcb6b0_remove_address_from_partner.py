"""remove address from partner

Revision ID: c92505dcb6b0
Revises: c1486f139707
Create Date: 2023-06-27 17:00:36.547164

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c92505dcb6b0'
down_revision = 'c1486f139707'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('advanced_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('agent_documents', 'document',
               existing_type=mysql.LONGBLOB(),
               type_=sa.LargeBinary(length=4294967295),
               existing_nullable=True)
    op.alter_column('agents', 'fixed_salary',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('agents', 'from_profit',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('agents', 'from_turnover',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('agents', 'fixed_perpiece',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('credit_note_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('incoming_rma_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('partner_documents', 'document',
               existing_type=mysql.LONGBLOB(),
               type_=sa.LargeBinary(length=4294967295),
               existing_nullable=True)
    op.alter_column('partners', 'amount_credit_limit',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.drop_column('partners', 'shipping_city')
    op.drop_column('partners', 'shipping_country')
    op.drop_column('partners', 'shipping_line1')
    op.drop_column('partners', 'shipping_line2')
    op.drop_column('partners', 'shipping_postcode')
    op.drop_column('partners', 'shipping_state')
    op.alter_column('purchase_documents', 'document',
               existing_type=mysql.LONGBLOB(),
               type_=sa.LargeBinary(length=4294967295),
               existing_nullable=True)
    op.alter_column('purchase_expenses', 'amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('purchase_payments', 'amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('purchase_payments', 'rate',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('purchase_proforma_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('purchase_proformas', 'credit_amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('sale_documents', 'document',
               existing_type=mysql.LONGBLOB(),
               type_=sa.LargeBinary(length=4294967295),
               existing_nullable=True)
    op.alter_column('sale_expenses', 'amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('sale_payments', 'amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('sale_payments', 'rate',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('sale_proforma_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    op.alter_column('sale_proformas', 'credit_amount',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('wh_incoming_rma_lines', 'price',
               existing_type=mysql.DOUBLE(asdecimal=True),
               type_=sa.Float(precision=32),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('wh_incoming_rma_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('sale_proformas', 'credit_amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    op.alter_column('sale_proforma_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('sale_payments', 'rate',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('sale_payments', 'amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('sale_expenses', 'amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('sale_documents', 'document',
               existing_type=sa.LargeBinary(length=4294967295),
               type_=mysql.LONGBLOB(),
               existing_nullable=True)
    op.alter_column('purchase_proformas', 'credit_amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    op.alter_column('purchase_proforma_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('purchase_payments', 'rate',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('purchase_payments', 'amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    op.alter_column('purchase_expenses', 'amount',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    op.alter_column('purchase_documents', 'document',
               existing_type=sa.LargeBinary(length=4294967295),
               type_=mysql.LONGBLOB(),
               existing_nullable=True)
    op.add_column('partners', sa.Column('shipping_state', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('partners', sa.Column('shipping_postcode', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('partners', sa.Column('shipping_line2', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('partners', sa.Column('shipping_line1', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('partners', sa.Column('shipping_country', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('partners', sa.Column('shipping_city', mysql.VARCHAR(length=50), nullable=True))
    op.alter_column('partners', 'amount_credit_limit',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    op.alter_column('partner_documents', 'document',
               existing_type=sa.LargeBinary(length=4294967295),
               type_=mysql.LONGBLOB(),
               existing_nullable=True)
    op.alter_column('incoming_rma_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('credit_note_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('agents', 'fixed_perpiece',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('agents', 'from_turnover',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('agents', 'from_profit',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('agents', 'fixed_salary',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=False)
    op.alter_column('agent_documents', 'document',
               existing_type=sa.LargeBinary(length=4294967295),
               type_=mysql.LONGBLOB(),
               existing_nullable=True)
    op.alter_column('advanced_lines', 'price',
               existing_type=sa.Float(precision=32),
               type_=mysql.DOUBLE(asdecimal=True),
               existing_nullable=True)
    # ### end Alembic commands ###