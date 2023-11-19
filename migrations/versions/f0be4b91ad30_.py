"""empty message

Revision ID: f0be4b91ad30
Revises: 75222199a503
Create Date: 2023-11-16 10:37:30.272402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f0be4b91ad30'
down_revision: Union[str, None] = '75222199a503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team_goal', sa.Column('MODIFY_DT', sa.DateTime(), nullable=True))
    op.drop_column('team_goal', 'MODIFY_DATE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team_goal', sa.Column('MODIFY_DATE', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('team_goal', 'MODIFY_DT')
    # ### end Alembic commands ###
