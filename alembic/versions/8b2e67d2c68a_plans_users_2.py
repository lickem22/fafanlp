"""Plans users 2

Revision ID: 8b2e67d2c68a
Revises: a0d1ae0f20e5
Create Date: 2021-07-27 00:26:53.546662

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b2e67d2c68a'
down_revision = 'a0d1ae0f20e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('type', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'type')
    # ### end Alembic commands ###
