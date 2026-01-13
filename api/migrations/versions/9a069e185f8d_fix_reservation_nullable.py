"""fix_reservation_nullable

Revision ID: 9a069e185f8d
Revises: 8429afbefc81
Create Date: 2026-01-13 18:43:03.841745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a069e185f8d'
down_revision: Union[str, None] = '8429afbefc81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('reservation', 'id_bibliotecaire',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('reservation', 'id_bibliotecaire',
               existing_type=sa.INTEGER(),
               nullable=False)
