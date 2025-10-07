"""Add ON DELETE CASCADE to notes.session_id

Revision ID: c35256332d5e
Revises: b57e8b120283
Create Date: 2025-08-07 21:47:58.533374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c35256332d5e'
down_revision: Union[str, None] = 'b57e8b120283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the old FK constraint
    op.drop_constraint('notes_session_id_fkey', 'notes', type_='foreignkey')

    # Add the new FK constraint with ON DELETE CASCADE
    op.create_foreign_key(
        'notes_session_id_fkey',
        'notes', 'studysessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Reverse the change
    op.drop_constraint('notes_session_id_fkey', 'notes', type_='foreignkey')

    op.create_foreign_key(
        'notes_session_id_fkey',
        'notes', 'studysessions',
        ['session_id'], ['id'],
        ondelete=None  # Default (RESTRICT)
    )