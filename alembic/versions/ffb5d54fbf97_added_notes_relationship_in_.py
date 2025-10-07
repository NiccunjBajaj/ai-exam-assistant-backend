"""Added notes relationship in stydySessions

Revision ID: ffb5d54fbf97
Revises: c35256332d5e
Create Date: 2025-08-07 21:50:33.403384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffb5d54fbf97'
down_revision: Union[str, None] = 'c35256332d5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
