from application.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(40), nullable = False, unique = True)
    email_id = db.Column(db.String(34), nullable = False, unique = True)
    password = db.Column(db.String(60), nullable = False)
    role = db.Column(db.String(60), nullable = False, default = 'users')


    def __init__(self, name, username, password, email_id):
        self.name = name
        self.username = username
        self.password = password
        self.email_id = email_id
        

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(80), nullable = False)
    quantity = db.Column(db.Integer ,nullable = False)
    sold = db.Column(db.Integer , default = 0)
    unit = db.Column(db.String(20), nullable = False)
    Total_price = db.Column(db.Integer,nullable = False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)
    
    product_cart = db.relationship('My_cart', backref = 'product', lazy = True, cascade='all, delete-orphan')

    def __init__(self, name, price, description, quantity, unit):
        self.name = name
        self.price = price
        self.description = description
        self.quantity = quantity
        self.sold = 0
        self.unit = unit
        
        # self.category_id = category_id
    
    def increment_sold(self, quantity_sold):
        self.sold += quantity_sold
        self.quantity -= quantity_sold
    
  
class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False, unique = True)
    products = db.relationship('Product', backref = 'category', lazy = True, cascade='all, delete-orphan')
    category_cart = db.relationship('My_cart', backref = 'category', lazy = True, cascade='all, delete-orphan')

    def __init__(self, name):
        self.name = name
    

class My_cart(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    unit = db.Column(db.String(20), nullable = False)
    total_price = db.Column(db.Integer,nullable = False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __init__(self, name, price, unit,  quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.unit = unit
        self.total_price = int(price)*int(quantity)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable = False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    user = db.relationship('User', backref='purchases')
    product = db.relationship('Product', backref='purchases')


        