"""empty message

Revision ID: 60032f4fcb14
Revises: a693f37246c8
Create Date: 2024-01-01 00:56:37.565327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60032f4fcb14'
down_revision: Union[str, None] = 'a693f37246c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item_log', sa.Column('IS_VIEW', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item_log', 'IS_VIEW')
    # ### end Alembic commands ###
