"""Fix delete user state

Revision ID: fa1b12f9b03d
Revises: c600e7f341b4
Create Date: 2025-04-18 14:23:57.662166

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fa1b12f9b03d"
down_revision: Union[str, None] = "c600e7f341b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "bot_users_bot_id_fkey", "bot_users", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "bot_users",
        "bots",
        ["bot_id"],
        ["id"],
        source_schema="public",
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "user_state_chain_id_fkey", "user_state", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "user_state", "chains", ["chain_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user_state", type_="foreignkey")  # type:ignore
    op.create_foreign_key(
        "user_state_chain_id_fkey",
        "user_state",
        "chains",
        ["chain_id"],
        ["id"],
    )
    op.drop_constraint(
        None, "bot_users", schema="public", type_="foreignkey"  # type:ignore
    )  # type:ignore
    op.create_foreign_key(
        "bot_users_bot_id_fkey",
        "bot_users",
        "bots",
        ["bot_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###
