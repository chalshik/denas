"""add_draft_status_to_products

Revision ID: cef1bd7b451a
Revises: 48a1db15a68b
Create Date: 2025-06-26 12:53:29.098212

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cef1bd7b451a'
down_revision = '48a1db15a68b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новый статус 'draft' в enum product_status
    op.execute("ALTER TYPE product_status ADD VALUE 'draft' BEFORE 'pending'")


def downgrade() -> None:
    # В PostgreSQL нельзя просто удалить значение из enum
    # Нужно создать новый enum без 'draft' и заменить старый
    # Это сложная операция, поэтому оставляем пустым
    pass 