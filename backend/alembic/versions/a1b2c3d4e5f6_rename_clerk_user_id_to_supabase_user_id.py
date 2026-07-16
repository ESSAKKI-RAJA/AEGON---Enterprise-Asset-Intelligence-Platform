"""rename_clerk_user_id_to_supabase_user_id

Revision ID: a1b2c3d4e5f6
Revises: c885348698ca
Create Date: 2026-07-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "c885348698ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename clerk_user_id to supabase_user_id on the users table."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        # Drop the old Clerk index
        batch_op.drop_index("ix_users_clerk_user_id")
        # Rename the column
        batch_op.alter_column(
            "clerk_user_id",
            new_column_name="supabase_user_id",
            existing_type=sa.String(length=255),
            existing_nullable=True,
        )
        # Recreate the index under the new name
        batch_op.create_index("ix_users_supabase_user_id", ["supabase_user_id"], unique=True)


def downgrade() -> None:
    """Revert supabase_user_id back to clerk_user_id."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index("ix_users_supabase_user_id")
        batch_op.alter_column(
            "supabase_user_id",
            new_column_name="clerk_user_id",
            existing_type=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.create_index("ix_users_clerk_user_id", ["clerk_user_id"], unique=True)
