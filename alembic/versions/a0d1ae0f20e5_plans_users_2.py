"""Plans users 2

Revision ID: a0d1ae0f20e5
Revises: 834d30f8b072
Create Date: 2021-07-27 00:25:43.504677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0d1ae0f20e5'
down_revision = '834d30f8b072'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('memberships',
    sa.Column('left_id', sa.Integer(), nullable=False),
    sa.Column('right_id', sa.Integer(), nullable=False),
    sa.Column('expiring_date', sa.DateTime(), nullable=False),
    sa.Column('expired', sa.Boolean(), nullable=True),
    sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['left_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['right_id'], ['plans.id'], ),
    sa.PrimaryKeyConstraint('left_id', 'right_id')
    )
    op.drop_table('association')
    op.add_column('plans', sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('plans', sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('users', sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('users', 'type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('users', 'time_updated')
    op.drop_column('users', 'time_created')
    op.drop_column('plans', 'time_updated')
    op.drop_column('plans', 'time_created')
    op.create_table('association',
    sa.Column('left_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('right_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['left_id'], ['users.id'], name='association_left_id_fkey'),
    sa.ForeignKeyConstraint(['right_id'], ['plans.id'], name='association_right_id_fkey'),
    sa.PrimaryKeyConstraint('left_id', 'right_id', name='association_pkey')
    )
    op.drop_table('memberships')
    # ### end Alembic commands ###
