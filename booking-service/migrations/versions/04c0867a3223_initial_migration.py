
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '04c0867a3223'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('location_name', sa.String(length=150), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('service_name', sa.String(length=150), nullable=False),
    sa.Column('service_duration_minutes', sa.Integer(), nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('employee_name', sa.String(length=220), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=True),
    sa.Column('appointment_date', sa.String(length=10), nullable=False),
    sa.Column('appointment_time', sa.String(length=5), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_employee_id'), 'bookings', ['employee_id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_location_id'), 'bookings', ['location_id'], unique=False)
    op.create_index(op.f('ix_bookings_service_id'), 'bookings', ['service_id'], unique=False)
    op.create_index(op.f('ix_bookings_user_email'), 'bookings', ['user_email'], unique=False)
    


def downgrade() -> None:
    
    op.drop_index(op.f('ix_bookings_user_email'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_service_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_location_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_employee_id'), table_name='bookings')
    op.drop_table('bookings')
    