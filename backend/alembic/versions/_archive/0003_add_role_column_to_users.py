from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_role_column_to_users'
down_revision = '0002_add_email_is_active'
branch_labels = None
depends_on = None

def upgrade():
    # Create the enum type for user roles
    role_enum = sa.Enum('admin', 'standard_user', name='userrole')
    role_enum.create(op.get_bind())
    op.add_column('users', sa.Column('role', role_enum, nullable=False, server_default='standard_user'))

def downgrade():
    op.drop_column('users', 'role')
    sa.Enum(name='userrole').drop(op.get_bind())