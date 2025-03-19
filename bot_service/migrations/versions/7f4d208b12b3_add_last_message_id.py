"""Add last_message_id

Revision ID: 7f4d208b12b3
Revises: ed152b883501
Create Date: 2025-03-18 21:56:37.162355

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7f4d208b12b3"
down_revision: Union[str, None] = "ed152b883501"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_state", sa.Column("last_message_id", sa.Integer(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user_state", "last_message_id")
    # ### end Alembic commands ###
