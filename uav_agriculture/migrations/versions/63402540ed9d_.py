"""empty message

Revision ID: 63402540ed9d
Revises: 962ecb81d3de
Create Date: 2020-10-29 09:32:06.580281

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '63402540ed9d'
down_revision = '962ecb81d3de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('survey_parameters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slope', sa.Float(), nullable=False),
    sa.Column('spacing', sa.Float(), nullable=False),
    sa.Column('altitude', sa.Float(), nullable=False),
    sa.Column('speed', sa.Float(), nullable=False),
    sa.Column('farm_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['farm_id'], ['farm.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'activity_log', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column(u'activity_log', 'type',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column(u'collected_image', 'details',
               existing_type=sa.VARCHAR(length=1000),
               nullable=False)
    op.alter_column(u'collected_image', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column(u'encyclopedic_information', 'type',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column(u'path', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column(u'schedule', 'status',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column(u'user', 'access_level',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column(u'weather_information', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'weather_information', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column(u'user', 'access_level',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column(u'schedule', 'status',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column(u'path', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column(u'encyclopedic_information', 'type',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column(u'collected_image', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column(u'collected_image', 'details',
               existing_type=sa.VARCHAR(length=1000),
               nullable=True)
    op.alter_column(u'activity_log', 'type',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column(u'activity_log', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_table('survey_parameters')
    # ### end Alembic commands ###
