"""empty message

Revision ID: a3a1e88dfeec
Revises: 34f949b90cc5
Create Date: 2022-09-22 13:49:28.303962

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a3a1e88dfeec'
down_revision = '34f949b90cc5'
branch_labels = None
depends_on = None


def upgrade():
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
    op.add_column('sale_invoices', sa.Column('wh_incoming_rma_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'sale_invoices', 'wh_incoming_rmas', ['wh_incoming_rma_id'], ['id'])
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


def downgrade():
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
    op.drop_constraint(None, 'sale_invoices', type_='foreignkey')
    op.drop_column('sale_invoices', 'wh_incoming_rma_id')
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