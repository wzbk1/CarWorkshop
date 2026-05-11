
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=False),
        sa.Column('user_name', sa.String(length=200), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_user_email'), 'reviews', ['user_email'])
    op.create_index(op.f('ix_reviews_location_id'), 'reviews', ['location_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_reviews_location_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_user_email'), table_name='reviews')
    op.drop_table('reviews')