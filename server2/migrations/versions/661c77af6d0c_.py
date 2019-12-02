"""empty message

Revision ID: 661c77af6d0c
Revises: f1ac88f46f14
Create Date: 2019-11-28 15:51:51.584128

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '661c77af6d0c'
down_revision = 'f1ac88f46f14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('category', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('post', 'content',
               existing_type=mysql.TEXT(),
               nullable=False)
    op.alter_column('post', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('post', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('post', 'content',
               existing_type=mysql.TEXT(),
               nullable=True)
    op.alter_column('category', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###