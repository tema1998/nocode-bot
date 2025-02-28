"""Add digital-funnel models

Revision ID: 8368cf7d1fa1
Revises: 279547ea5e39
Create Date: 2025-02-24 11:54:50.313355

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8368cf7d1fa1"
down_revision: Union[str, None] = "279547ea5e39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "funnels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("bot_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bot_id"],
            ["bots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_funnels_id"), "funnels", ["id"], unique=False)
    op.create_table(
        "funnel_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("funnel_id", sa.Integer(), nullable=True),
        sa.Column("step_type", sa.String(), nullable=True),
        sa.Column("content", sa.JSON(), nullable=True),
        sa.Column("next_step_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["funnel_id"],
            ["funnels.id"],
        ),
        sa.ForeignKeyConstraint(
            ["next_step_id"],
            ["funnel_steps.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_funnel_steps_id"), "funnel_steps", ["id"], unique=False
    )
    op.create_table(
        "user_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("bot_id", sa.Integer(), nullable=True),
        sa.Column("funnel_id", sa.Integer(), nullable=True),
        sa.Column("current_step_id", sa.Integer(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bot_id"],
            ["bots.id"],
        ),
        sa.ForeignKeyConstraint(
            ["current_step_id"],
            ["funnel_steps.id"],
        ),
        sa.ForeignKeyConstraint(
            ["funnel_id"],
            ["funnels.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_states_id"), "user_states", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_states_id"), table_name="user_states")
    op.drop_table("user_states")
    op.drop_index(op.f("ix_funnel_steps_id"), table_name="funnel_steps")
    op.drop_table("funnel_steps")
    op.drop_index(op.f("ix_funnels_id"), table_name="funnels")
    op.drop_table("funnels")
    # ### end Alembic commands ###
