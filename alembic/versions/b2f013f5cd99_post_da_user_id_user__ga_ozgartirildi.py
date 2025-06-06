"""post da user_id user_ ga ozgartirildi

Revision ID: b2f013f5cd99
Revises: df54edc0c573
Create Date: 2025-05-31 18:15:43.906889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f013f5cd99'
down_revision: Union[str, None] = 'df54edc0c573'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('user_', sa.Integer(), nullable=True))
    op.drop_constraint(op.f('post_user_id_fkey'), 'post', type_='foreignkey')
    op.create_foreign_key(None, 'post', 'users', ['user_'], ['id'])
    op.drop_column('post', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.create_foreign_key(op.f('post_user_id_fkey'), 'post', 'users', ['user_id'], ['id'])
    op.drop_column('post', 'user_')
    # ### end Alembic commands ###
