"""empty message

Revision ID: 962ecb81d3de
Revises: 6d8f2f9fa925
Create Date: 2020-10-18 16:48:40.528581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '962ecb81d3de'
down_revision = '6d8f2f9fa925'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('collected_image', 'status',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('collected_image', 'status',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###