"""clerk_auth_refactor

Revision ID: c885348698ca
Revises: a4368b114bac
Create Date: 2026-07-11 10:58:47.387948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c885348698ca'
down_revision: Union[str, Sequence[str], None] = 'a4368b114bac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add clerk_user_id column to users
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('clerk_user_id', sa.String(length=255), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_clerk_user_id'), ['clerk_user_id'], unique=True)
        # Make hashed_password nullable
        batch_op.alter_column('hashed_password',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        # Revert hashed_password to non-nullable (SQLite doesn't enforce, but strictly speaking)
        batch_op.alter_column('hashed_password',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=False)
        batch_op.drop_index(batch_op.f('ix_users_clerk_user_id'))
        batch_op.drop_column('clerk_user_id')
