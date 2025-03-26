"""Add on_delete SET NULL for chain steps

Revision ID: 9b5e734111fd
Revises: 8ea68e15bde7
Create Date: 2025-03-26 16:07:00.981156

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9b5e734111fd"
down_revision: Union[str, None] = "8ea68e15bde7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "chain_buttons_next_step_id_fkey", "chain_buttons", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "chain_buttons",
        "chain_steps",
        ["next_step_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(
        "chain_steps_next_step_id_fkey", "chain_steps", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "chain_steps",
        "chain_steps",
        ["next_step_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "chain_steps", type_="foreignkey")  # type: ignore
    op.create_foreign_key(
        "chain_steps_next_step_id_fkey",
        "chain_steps",
        "chain_steps",
        ["next_step_id"],
        ["id"],
    )
    op.drop_constraint(
        None, "chain_buttons", type_="foreignkey"  # type: ignore
    )  # type:ignore
    op.create_foreign_key(
        "chain_buttons_next_step_id_fkey",
        "chain_buttons",
        "chain_steps",
        ["next_step_id"],
        ["id"],
    )
    # ### end Alembic commands ###
