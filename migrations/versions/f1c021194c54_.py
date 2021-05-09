"""empty message

Revision ID: f1c021194c54
Revises: bf15da390f02
Create Date: 2021-05-04 17:00:54.394864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1c021194c54'
down_revision = 'bf15da390f02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blog_post', sa.Column('date', sa.DateTime(), nullable=True))
    op.add_column('comment', sa.Column('text', sa.Text(), nullable=False))
    op.add_column('comment', sa.Column('date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'date')
    op.drop_column('comment', 'text')
    op.drop_column('blog_post', 'date')
    # ### end Alembic commands ###
