"""empty message

Revision ID: e068f321c502
Revises: 3059dcbb20fc
Create Date: 2023-12-01 10:12:01.961067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e068f321c502'
down_revision: Union[str, None] = '3059dcbb20fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('avatar_user_AVATAR_NO_fkey', 'avatar_user', type_='foreignkey')
    op.drop_column('avatar_user', 'AVATAR_NO')
    op.drop_constraint('item_log_ITEM_NO_fkey', 'item_log', type_='foreignkey')
    op.drop_column('item_log', 'ITEM_NO')
    op.drop_constraint('item_user_ITEM_NO_fkey', 'item_user', type_='foreignkey')
    op.drop_column('item_user', 'ITEM_NO')
    op.drop_table('avatar')
    op.drop_table('item')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item_user', sa.Column('ITEM_NO', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('item_user_ITEM_NO_fkey', 'item_user', 'item', ['ITEM_NO'], ['ITEM_NO'])
    op.add_column('item_log', sa.Column('ITEM_NO', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('item_log_ITEM_NO_fkey', 'item_log', 'item', ['ITEM_NO'], ['ITEM_NO'])
    op.add_column('avatar_user', sa.Column('AVATAR_NO', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('avatar_user_AVATAR_NO_fkey', 'avatar_user', 'avatar', ['AVATAR_NO'], ['AVATAR_NO'])
    op.create_table('item',
    sa.Column('ITEM_NO', sa.INTEGER(), server_default=sa.text('nextval(\'"item_ITEM_NO_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('ITEM_NM', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('ITEM_NO', name='item_pkey')
    )
    op.create_table('avatar',
    sa.Column('AVATAR_NO', sa.INTEGER(), server_default=sa.text('nextval(\'"avatar_AVATAR_NO_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('AVATAR_NM', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('AvatarType', postgresql.ENUM('CHARACTER', 'PET', name='avatartype'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('AVATAR_NO', name='avatar_pkey')
    )
    # ### end Alembic commands ###
