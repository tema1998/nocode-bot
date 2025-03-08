"""Add default_reply field to bot model

Revision ID: 40e112d2ab18
Revises: 142ffa79c748
Create Date: 2025-03-05 20:01:21.885984

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "40e112d2ab18"
down_revision: Union[str, None] = "142ffa79c748"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "bots", sa.Column("default_reply", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("bots", "default_reply")
    # ### end Alembic commands ###
