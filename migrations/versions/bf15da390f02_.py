"""empty message

Revision ID: bf15da390f02
Revises: 
Create Date: 2021-05-04 16:50:27.351591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf15da390f02'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('login', sa.String(length=128), nullable=False),
    sa.Column('password', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('blog_post',
    sa.Column('blogid', sa.Integer(), nullable=False),
    sa.Column('author', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('blogid')
    )
    op.create_table('comment',
    sa.Column('comid', sa.Integer(), nullable=False),
    sa.Column('blog', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['blog'], ['blog_post.blogid'], ),
    sa.ForeignKeyConstraint(['user'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('comid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    op.drop_table('blog_post')
    op.drop_table('user')
    # ### end Alembic commands ###
