"""empty message

Revision ID: b2b6b17949d9
Revises: 80eabc1c188f
Create Date: 2023-12-07 09:17:43.989902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2b6b17949d9'
down_revision: Union[str, None] = '80eabc1c188f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('challenge_master', 'START_DT',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)
    op.alter_column('challenge_master', 'END_DT',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('challenge_master', 'END_DT',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)
    op.alter_column('challenge_master', 'START_DT',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)
    # ### end Alembic commands ###
