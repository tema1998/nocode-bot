"""Update digital-models

Revision ID: ad68c98765a4
Revises: 8368cf7d1fa1
Create Date: 2025-02-24 20:40:35.504151

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "ad68c98765a4"
down_revision: Union[str, None] = "8368cf7d1fa1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "buttons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("step_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("next_step_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["next_step_id"],
            ["funnel_steps.id"],
        ),
        sa.ForeignKeyConstraint(
            ["step_id"],
            ["funnel_steps.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_buttons_id"), "buttons", ["id"], unique=False)
    op.add_column(
        "funnel_steps", sa.Column("text", sa.String(), nullable=True)
    )
    op.drop_constraint(
        "funnel_steps_next_step_id_fkey", "funnel_steps", type_="foreignkey"
    )
    op.drop_column("funnel_steps", "content")
    op.drop_column("funnel_steps", "next_step_id")
    op.drop_column("funnel_steps", "step_type")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "funnel_steps",
        sa.Column(
            "step_type", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "funnel_steps",
        sa.Column(
            "next_step_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "funnel_steps",
        sa.Column(
            "content",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "funnel_steps_next_step_id_fkey",
        "funnel_steps",
        "funnel_steps",
        ["next_step_id"],
        ["id"],
    )
    op.drop_column("funnel_steps", "text")
    op.drop_index(op.f("ix_buttons_id"), table_name="buttons")
    op.drop_table("buttons")
    # ### end Alembic commands ###
