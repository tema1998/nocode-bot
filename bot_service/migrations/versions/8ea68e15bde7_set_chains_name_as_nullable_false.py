"""Set chains_name as nullable false

Revision ID: 8ea68e15bde7
Revises: 974e5f098b7c
Create Date: 2025-03-23 16:41:59.233907

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8ea68e15bde7"
down_revision: Union[str, None] = "974e5f098b7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "chain_steps", "name", existing_type=sa.VARCHAR(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "chain_steps", "name", existing_type=sa.VARCHAR(), nullable=True
    )
    # ### end Alembic commands ###
