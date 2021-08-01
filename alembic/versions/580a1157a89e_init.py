"""init

Revision ID: 580a1157a89e
Revises: 
Create Date: 2021-07-24 00:09:57.857854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '580a1157a89e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
     op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('contact', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('created', sa.DateTime()),
        sa.Column('updated', sa.DateTime())
    )


def downgrade():
    op.drop_table('users')
