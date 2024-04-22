from application import app
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.sqlite3'

db = SQLAlchemy(app)

from application.model import *
from application.model import My_cart

app.app_context().push()
# db.drop_all()
# metadata = db.metadata

# # Drop the "My_cart" table
# metadata.drop_all(bind=db.engine, tables=[My_cart.__table__])
db.create_all()