"""initial migration

Revision ID: 8bfba2626334
Revises: 
Create Date: 2025-01-22 06:43:12.720419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bfba2626334'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True, comment='User first name'),
    sa.Column('last_name', sa.String(length=50), nullable=True, comment='User last name'),
    sa.Column('username', sa.String(length=50), nullable=False, comment='Unique username for login'),
    sa.Column('password', sa.String(length=255), nullable=False, comment='Hashed password'),
    sa.Column('age', sa.Integer(), nullable=True, comment='User age'),
    sa.Column('address', sa.String(length=255), nullable=True, comment='User address'),
    sa.Column('email', sa.String(length=100), nullable=True, comment='User email address'),
    sa.Column('tier', sa.Enum('BASIC', 'PREMIUM', 'VIP', name='usertier'), nullable=True, comment='User subscription tier'),
    sa.Column('nin', sa.String(length=11), nullable=True, comment='Nigerian National Identification Number'),
    sa.Column('bvn', sa.String(length=11), nullable=True, comment='Bank Verification Number'),
    sa.Column('verified', sa.Boolean(), nullable=False, comment='Email verification status'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Account active status'),
    sa.Column('date_joined', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Account creation timestamp'),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True, comment='Last login timestamp'),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
    sa.PrimaryKeyConstraint('id'),
    comment='Stores user account information'
    )
    op.create_index(op.f('ix_users_bvn'), 'users', ['bvn'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_nin'), 'users', ['nin'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('currency', sa.Enum('NGN', 'USD', 'EUR', 'GBP', name='currency'), nullable=False, comment='Account currency type'),
    sa.Column('account_number', sa.String(length=20), nullable=False, comment='Unique account number'),
    sa.Column('balance', sa.Numeric(precision=20, scale=4), nullable=False, comment='Current account balance'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Account active status'),
    sa.Column('is_default', sa.Boolean(), nullable=False, comment='Whether this is the default account for the currency'),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Account creation timestamp'),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    comment='Stores user currency accounts'
    )
    op.create_index(op.f('ix_accounts_account_number'), 'accounts', ['account_number'], unique=True)
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_number'), table_name='accounts')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_nin'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_bvn'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
