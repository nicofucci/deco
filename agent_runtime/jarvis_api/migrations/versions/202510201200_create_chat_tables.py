"""create conversations and messages tables with web search + rag fields"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "202510201200"
down_revision = None
branch_labels = None
depends_on = None


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not _table_exists(inspector, "conversations"):
        op.create_table(
            "conversations",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("user_id", sa.String(), nullable=False, index=True),
            sa.Column("title", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("is_archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("auto_title_generated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("web_search_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        )
    else:
        if not _column_exists(inspector, "conversations", "auto_title_generated"):
            op.add_column(
                "conversations",
                sa.Column("auto_title_generated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            )
        if not _column_exists(inspector, "conversations", "web_search_enabled"):
            op.add_column(
                "conversations",
                sa.Column("web_search_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            )
        if not _column_exists(inspector, "conversations", "metadata"):
            op.add_column(
                "conversations",
                sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
            )

    if not _table_exists(inspector, "messages"):
        op.create_table(
            "messages",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column(
                "conversation_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("conversations.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.Column("attachments", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
            sa.Column("tool_calls", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
            sa.Column("uses_web_search", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("is_important", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("embedding", postgresql.JSONB(), nullable=True),
            sa.Column("rag_status", sa.String(), server_default="none", nullable=True),
            sa.Column("metadata", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=True),
        )
    else:
        if not _column_exists(inspector, "messages", "uses_web_search"):
            op.add_column(
                "messages",
                sa.Column("uses_web_search", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            )
        if not _column_exists(inspector, "messages", "is_important"):
            op.add_column(
                "messages",
                sa.Column("is_important", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            )
        if not _column_exists(inspector, "messages", "embedding"):
            op.add_column("messages", sa.Column("embedding", postgresql.JSONB(), nullable=True))
        if not _column_exists(inspector, "messages", "created_at"):
            op.add_column(
                "messages",
                sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            )
        if not _column_exists(inspector, "messages", "tool_calls"):
            op.add_column(
                "messages",
                sa.Column("tool_calls", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "messages"):
        op.drop_table("messages")
    if _table_exists(inspector, "conversations"):
        op.drop_table("conversations")
