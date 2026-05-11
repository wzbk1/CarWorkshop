
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.create_table(
        'car_brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_location_id'), 'services', ['location_id'])

    
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('specialization', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_location_id'), 'employees', ['location_id'])

    
    op.create_table(
        'cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('vin', sa.String(length=17), nullable=True),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('mileage', sa.Integer(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['brand_id'], ['car_brands.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vin')
    )
    op.create_index(op.f('ix_cars_user_email'), 'cars', ['user_email'])

    
    op.create_table(
        'business_hours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('open_time', sa.String(length=5), nullable=True),
        sa.Column('close_time', sa.String(length=5), nullable=True),
        sa.Column('lunch_start', sa.String(length=5), nullable=True),
        sa.Column('lunch_end', sa.String(length=5), nullable=True),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_hours_location_id'), 'business_hours', ['location_id'])

    
    op.create_table(
        'location_exceptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('exception_date', sa.String(length=10), nullable=False),
        sa.Column('open_time', sa.String(length=5), nullable=True),
        sa.Column('close_time', sa.String(length=5), nullable=True),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_location_exceptions_exception_date'), 'location_exceptions', ['exception_date'])
    op.create_index(op.f('ix_location_exceptions_location_id'), 'location_exceptions', ['location_id'])

    
    op.create_table(
        'employee_absences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('absence_date', sa.String(length=10), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_absences_absence_date'), 'employee_absences', ['absence_date'])
    op.create_index(op.f('ix_employee_absences_employee_id'), 'employee_absences', ['employee_id'])

    
    op.create_table(
        'employee_services',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('employee_id', 'service_id')
    )

    
    op.create_table(
        'location_car_brands',
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('car_brand_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['car_brand_id'], ['car_brands.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('location_id', 'car_brand_id')
    )


def downgrade() -> None:
    op.drop_table('location_car_brands')
    op.drop_table('employee_services')
    op.drop_index(op.f('ix_employee_absences_employee_id'), table_name='employee_absences')
    op.drop_index(op.f('ix_employee_absences_absence_date'), table_name='employee_absences')
    op.drop_table('employee_absences')
    op.drop_index(op.f('ix_location_exceptions_location_id'), table_name='location_exceptions')
    op.drop_index(op.f('ix_location_exceptions_exception_date'), table_name='location_exceptions')
    op.drop_table('location_exceptions')
    op.drop_index(op.f('ix_business_hours_location_id'), table_name='business_hours')
    op.drop_table('business_hours')
    op.drop_index(op.f('ix_cars_user_email'), table_name='cars')
    op.drop_table('cars')
    op.drop_index(op.f('ix_employees_location_id'), table_name='employees')
    op.drop_table('employees')
    op.drop_index(op.f('ix_services_location_id'), table_name='services')
    op.drop_table('services')
    op.drop_table('locations')
    op.drop_table('car_brands')