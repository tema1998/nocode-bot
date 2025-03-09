"""Add index to main_menu bot_id

Revision ID: f1fc49ae882a
Revises: 14de7b9f6b95
Create Date: 2025-03-09 09:00:57.617353

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f1fc49ae882a"
down_revision: Union[str, None] = "14de7b9f6b95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("ix_buttons_bot_id"), "buttons", ["bot_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_buttons_bot_id"), table_name="buttons")
    # ### end Alembic commands ###
