"""post to user_

Revision ID: f2bf08174cb2
Revises: f090acd27d11
Create Date: 2025-06-03 11:07:55.303116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2bf08174cb2'
down_revision: Union[str, None] = 'f090acd27d11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("post", "user_", new_column_name="user_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("post", "user_id", new_column_name="user_")

