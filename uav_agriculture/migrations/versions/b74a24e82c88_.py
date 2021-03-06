"""empty message

Revision ID: b74a24e82c88
Revises: 63402540ed9d
Create Date: 2020-10-29 09:35:20.701535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b74a24e82c88'
down_revision = '63402540ed9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'survey_parameters_farm_id_fkey', 'survey_parameters', type_='foreignkey')
    op.drop_column('survey_parameters', 'farm_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_parameters', sa.Column('farm_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key(u'survey_parameters_farm_id_fkey', 'survey_parameters', 'farm', ['farm_id'], ['id'])
    # ### end Alembic commands ###
