"""add_rejection_reason_to_vendor_profiles

Revision ID: d1fdd3567535
Revises: 7f830ae9426c
Create Date: 2025-07-06 18:02:35.512595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1fdd3567535'
down_revision = '7f830ae9426c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add rejection_reason column to vendor_profiles table
    op.add_column('vendor_profiles', sa.Column('rejection_reason', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove rejection_reason column from vendor_profiles table
    op.drop_column('vendor_profiles', 'rejection_reason') 