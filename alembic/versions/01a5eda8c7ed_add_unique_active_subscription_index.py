"""add unique active subscription index

Revision ID: 01a5eda8c7ed
Revises: c3d835016770
Create Date: 2025-11-01 13:49:22.424601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01a5eda8c7ed'
down_revision: Union[str, None] = 'c3d835016770'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS unique_active_subscription_per_user
        ON user_subscriptions (user_id)
        WHERE is_active = true;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP INDEX IF EXISTS unique_active_subscription_per_user;
    """)
