"""empty message

Revision ID: 2f775b3b98a6
Revises: 080ed13eba0f
Create Date: 2023-12-01 00:10:09.185030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2f775b3b98a6'
down_revision: Union[str, None] = '080ed13eba0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('avatar',
    sa.Column('AVATAR_NO', sa.Integer(), nullable=False),
    sa.Column('AVATAR_NM', sa.String(), nullable=False),
    sa.Column('AvatarType', sa.Enum('CHARACTER', 'PET', name='avatartype'), nullable=True),
    sa.PrimaryKeyConstraint('AVATAR_NO')
    )
    op.create_table('item',
    sa.Column('ITEM_NO', sa.Integer(), nullable=False),
    sa.Column('ITEM_NM', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('ITEM_NO')
    )
    op.create_table('avatar_user',
    sa.Column('AVATAR_USER_NO', sa.Integer(), nullable=False),
    sa.Column('IS_EQUIP', sa.Boolean(), nullable=True),
    sa.Column('AVATAR_NO', sa.Integer(), nullable=True),
    sa.Column('USER_NO', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['AVATAR_NO'], ['avatar.AVATAR_NO'], ),
    sa.ForeignKeyConstraint(['USER_NO'], ['user.USER_NO'], ),
    sa.PrimaryKeyConstraint('AVATAR_USER_NO')
    )
    op.drop_table('pet')
    op.drop_table('character')
    op.add_column('item_log', sa.Column('ITEM_NO', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'item_log', 'item', ['ITEM_NO'], ['ITEM_NO'])
    op.drop_column('item_log', 'ITEM_NM')
    op.add_column('item_user', sa.Column('ITEM_USER_NO', sa.Integer(), nullable=False))
    op.alter_column('item_user', 'ITEM_NO',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('nextval(\'"item_user_ITEM_NO_seq"\'::regclass)'))
    op.create_foreign_key(None, 'item_user', 'item', ['ITEM_NO'], ['ITEM_NO'])
    op.drop_column('item_user', 'ITEM_NM')
    op.drop_constraint('user_USER_EMAIL_key', 'user', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('user_USER_EMAIL_key', 'user', ['USER_EMAIL'])
    op.add_column('item_user', sa.Column('ITEM_NM', postgresql.ENUM('BOOM', 'HAMMER', name='ItemType'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'item_user', type_='foreignkey')
    op.alter_column('item_user', 'ITEM_NO',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('nextval(\'"item_user_ITEM_NO_seq"\'::regclass)'))
    op.drop_column('item_user', 'ITEM_USER_NO')
    op.add_column('item_log', sa.Column('ITEM_NM', postgresql.ENUM('BOOM', 'HAMMER', name='ItemType'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'item_log', type_='foreignkey')
    op.drop_column('item_log', 'ITEM_NO')
    op.create_table('character',
    sa.Column('CHARACTER_NO', sa.INTEGER(), server_default=sa.text('nextval(\'"character_CHARACTER_NO_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('CHARACTER_NM', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('STATUS', postgresql.ENUM(name='OwnerShipType'), autoincrement=False, nullable=True),
    sa.Column('USER_NO', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['USER_NO'], ['user.USER_NO'], name='character_USER_NO_fkey'),
    sa.PrimaryKeyConstraint('CHARACTER_NO', name='character_pkey')
    )
    op.create_table('pet',
    sa.Column('PET_NO', sa.INTEGER(), server_default=sa.text('nextval(\'"pet_PET_NO_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('PetType', postgresql.ENUM('PET_TYPE1', 'PET_TYPE2', name='pettype'), autoincrement=False, nullable=True),
    sa.Column('STATUS', postgresql.ENUM(name='OwnerShipType'), autoincrement=False, nullable=True),
    sa.Column('USER_NO', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['USER_NO'], ['user.USER_NO'], name='pet_USER_NO_fkey'),
    sa.PrimaryKeyConstraint('PET_NO', name='pet_pkey')
    )
    op.drop_table('avatar_user')
    op.drop_table('item')
    op.drop_table('avatar')
    # ### end Alembic commands ###
