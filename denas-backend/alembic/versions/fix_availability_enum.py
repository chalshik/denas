"""fix availability type enum

Revision ID: fix_availability_enum
Revises: 2b3f505a0a64
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_availability_enum'
down_revision = '2b3f505a0a64'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the old enum and create a new one with correct values
    op.execute("ALTER TYPE availabilitytype RENAME TO availabilitytype_old")
    op.execute("CREATE TYPE availabilitytype AS ENUM ('IN_STOCK', 'PRE_ORDER', 'DISCONTINUED')")
    op.execute("ALTER TABLE products ALTER COLUMN availability_type TYPE availabilitytype USING availability_type::text::availabilitytype")
    op.execute("DROP TYPE availabilitytype_old")

def downgrade():
    # Reverse the changes
    op.execute("ALTER TYPE availabilitytype RENAME TO availabilitytype_old")
    op.execute("CREATE TYPE availabilitytype AS ENUM ('IN_STOCK', 'PRE_ORDER', 'DISCONTINUED')")
    op.execute("ALTER TABLE products ALTER COLUMN availability_type TYPE availabilitytype USING availability_type::text::availabilitytype")
    op.execute("DROP TYPE availabilitytype_old")