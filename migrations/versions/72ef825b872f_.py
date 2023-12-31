"""empty message

Revision ID: 72ef825b872f
Revises: e80fd067389e
Create Date: 2023-12-04 20:03:50.677825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72ef825b872f'
down_revision: Union[str, None] = 'e80fd067389e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('challenge_master', sa.Column('CHALLENGE_STATUS', sa.Enum('PENDING', 'PROGRESS', 'COMPLETE', 'FAILED', name='ChallengeStatusType'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('challenge_master', 'CHALLENGE_STATUS')
    # ### end Alembic commands ###
