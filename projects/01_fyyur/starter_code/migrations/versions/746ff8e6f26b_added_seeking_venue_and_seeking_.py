"""Added seeking_venue and seeking_description to Artist

Revision ID: 746ff8e6f26b
Revises: 3a2abf6595cb
Create Date: 2021-08-16 12:31:05.166411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '746ff8e6f26b'
down_revision = '3a2abf6595cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=500), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True, server_default='t'))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
