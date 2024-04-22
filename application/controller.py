from datetime import datetime, timedelta
from application import app
from flask import request, render_template, redirect, flash, url_for, session
from application.database import db
from application.model import User,Product,Category, My_cart, Purchase
import os
import matplotlib
matplotlib.use('Agg') #anti gain geometry
import matplotlib.pyplot as plt


app.secret_key = 'jfglkafjdf4556'

def is_admin_exist():
    flag = False
    users = User.query.all()
    for user in users:
        if user.role == 'admin':
            flag = True
            break
    return flag


def admin():
     if is_admin_exist():
        return 
     else:
        admins = User(name = 'ajoy',username = 'ajoydas123',password = '123456', email_id = 'ajoyd23@gmail.com')
        admins.role = 'admin'
        db.session.add(admins)
        db.session.commit()

def get_category_product():
    getting_products = Product.query.all()
    category_products = []
    category_product_display = {}

    for product in getting_products:
        cat_id = product.category_id
        category = Category.query.get(cat_id)
        category_products.append((product, category))
    for  product,category in category_products:
        category_product_display[category.name] = []

    for  product,category in category_products:
        category_product_display[category.name].append(product)
    
    for category, products in category_product_display.items():
        category_product_display[category] = sorted(products, key=lambda x: x.id, reverse=True)
    return category_product_display

@app.route('/')
def homepage():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        
        if user.role == 'admin':
            return redirect(url_for('category'))
        else:
            category_product_display = get_category_product()

            return render_template('after_login_home.html', category_product_display = category_product_display, username = username)
            
    else:
        getting_products = Product.query.all()
        if getting_products:
            category_product_display = get_category_product()

            return render_template('home.html', category_product_display = category_product_display)
        else:
            return render_template('home.html', category_product_display = getting_products)
    



def username_or_email_exists(username, email):
    user = User.query.filter((User.username == username) | (User.email_id == email)).first()
    return user is not None

@app.route('/user/register', methods = ['GET','POST'])
def user_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email_id = request.form['email']
        if username_or_email_exists(username, email_id):
            error_messages = []
            if username_or_email_exists(username, email_id):
                error_messages.append('Username and/or email already exist. Please choose different ones.')
            elif username_or_email_exists(username, None):
                error_messages.append('Username already exists. Please choose a different username.')
            elif username_or_email_exists(None, email_id):
                error_messages.append('Email already exists. Please choose a different email.')

            flash('<br>'.join(error_messages), 'error')
            return render_template('user_register.html')
        
        user = User(name = name, username = username, password = password, email_id = email_id)
        db.session.add(user)
        db.session.commit()
        flash('You have sucessfully registered', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_register.html')


@app.route('/userlogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_valid = User.query.filter_by(username=username).first()

        if user_valid and user_valid.role == 'users':
            # If the username exists, check if the password matches
            if user_valid.password == password:
                session['username'] = username
                # session['password'] = password
                return redirect(url_for('homepage'))
            else:
                flash('Password for this username did not match.', 'error')
                return redirect(url_for('user_login'))
        elif user_valid and user_valid.role == 'admin':
            flash('Please do the login at admin login page', 'error')
            return redirect(url_for('admin_login'))
        else:
            flash('This username does not exist. If you haven\'t registered, please do registration else give correct username.', 'error')
            return redirect(url_for('user_login'))

    return render_template('login.html')



@app.route('/admin/login', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin_valid = User.query.filter_by(username = username).first()
        if admin_valid:
            if admin_valid.password == password and admin_valid.role == 'admin':
                session['username'] = username
                # session['password'] = password
                return redirect(url_for('homepage', username = username))
            else:
                flash('password of this admin did not matched')
                return render_template('admin_login.html')
        else:    
            flash('This admin username does not exists, Please entry correct admin username.', 'warning')
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')
        
@app.route('/user/logout')
def user_logout():
    session.pop('username', None)
    return redirect(url_for('user_login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('username', None)
    return redirect(url_for('admin_login'))

#------------------------------------------------------ Category Part -----------------------------------------------------------------------------

@app.route('/category') 
def category():
    if 'username' in session:
        username = session['username']
        category_list = Category.query.all()
        if category_list:
            getting_products = Product.query.all()
            if getting_products:
                category_products = []

                for product in getting_products:
                    cat_id = product.category_id
                    category = Category.query.get(cat_id)
                    category_products.append((product, category))
                return render_template('add_product_card.html', username = username, category_products = category_products)
            else:
                return render_template('add_category.html', username = username, categories = category_list)
        else:
            
            return render_template('no_category_product.html', username = username)
    else:   
       return redirect(url_for('admin_login'))

#category--add, update, delete
@app.route('/addcategory', methods = ['GET','POST'])
def add_category():
    if 'username' in session:
        username = session['username']
        if request.method =='POST':
            name = request.form['categoryName']
            check = Category.query.filter_by(name = name).first()
            if check:
                flash('This category already exists', 'error')
                categories = Category.query.all()
                return render_template('add_category.html', username = username, categories = categories)
            else:
                category1 = Category(name)
                db.session.add(category1)
                db.session.commit()
                categories = Category.query.all()
                flash('Category added successfully', 'success')
                return render_template('add_category.html', categories = categories, username = username)
        else:
           categories = None
           return render_template('add_category.html', username = username, categories = categories)
    else:
        return redirect(url_for('admin_login'))
           
   
    
@app.route('/deletecategory/<int:id>')
def delete_category(id):
    if 'username' in session:
        username = session['username']
        category = Category.query.filter_by(id = id).first()
        db.session.delete(category)
        db.session.commit()
        # category = None
        valid_category = Category.query.all()
        if valid_category:
           return render_template('add_category.html', username = username, categories = valid_category)
        else:
            return render_template('no_category_product.html', username = username)
    return redirect(url_for('admin_login'))


@app.route('/updatecategory/<int:id>', methods = ['POST', 'GET'])
def update_category(id):
     if 'username' in session:
        username = session['username']
        category = Category.query.get(id)
        if request.method == 'POST':
            name = request.form['categoryName']

            # category1 = Category.query.filter_by(name = name).first()  
            category.name = name
            db.session.commit()
            categories = Category.query.all()
            flash('Product updated successfully', 'success')
            return render_template('add_category.html', username = username, categories = categories)
        else:
            # category = Category.query.all()
            return render_template('update_category.html', username = username, category = category)
     return redirect(url_for('admin_login'))


@app.route('/getcategory')
def get_category():
    if 'username' in session:
        username = session['username']
        categories = Category.query.all()
        if categories:
            return render_template('add_category.html', username = username, categories = categories)
        else:
            return render_template('add_category.html', username = username, categories = categories)
        # return render_template('add_category.html', username = username, categories = categories)
    else:
        redirect(url_for('admin_login'))

#------------------------------------------------------ Product part -----------------------------------------------------------------------------------
   
@app.route('/product/<int:id>')
def product(id):
    if 'username' in session:
        username = session['username']
        category = Category.query.get(id)
        return render_template('add_product.html', username = username, category = category)
    else:
        return redirect(url_for('admin_login'))


@app.route('/addproduct', methods = ['GET', 'POST'])
def add_product():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            quantity = request.form['quantity']
            unit = request.form.get('unit')  
            
            category_name = request.form['category_hidden']
            
            category = Category.query.filter_by(name = category_name).first()  # getting category instance
            # manufacturing_date = datetime.strptime(manufacturing_date_str, '%Y-%m-%d').date()
            # exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
            product = Product(name = name, price = price, description = description, unit = unit, quantity= quantity)
            product.Total_price = int(price)*int(quantity)
            product.category_id = category.id
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for('get_product', username = username))
            # except ValueError:
            #     flash('Invalid date format. Please use the format YYYY-MM-DD.', 'error')
            #     return redirect(url_for('add_product', username = username, category = category))
            
    
    redirect(url_for('admin_login'))
    

@app.route('/deleteproduct/<int:id>' )
def delete_product(id):
    if 'username' in session:
        username = session['username']
        product = Product.query.filter_by(id = id).first()
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('get_product', username = username))
    else:
        return redirect(url_for('admin_login'))


@app.route('/updateproduct/<int:id>', methods = ['GET', 'POST'])
def update_product(id):
    if 'username' in session:
        product = Product.query.get(id)
        username = session['username']
        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            quantity = request.form['quantity']
            unit = request.form.get('unit')  
            
            product.name = name
            product.price = price
            product.description = description
            product.quantity = quantity
            product.unit = unit
            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('get_product', username = username))
        else:
            product_category = []
            category = Category.query.get(product.category_id)
            product_category.append((product, category))
            return render_template('update_product.html', username = username, product_category = product_category)
    else:
        return redirect(url_for('admin_login'))


@app.route('/getproduct')
def get_product():
    if 'username' in session:
        username = session['username']
        getting_products = Product.query.all()
        category_products = []
        category_product_display = {}
        # categories = []
        for product in getting_products:
            cat_id = product.category_id
            category = Category.query.get(cat_id)
            category_products.append((product, category))
        for category, product in category_products:
            category_product_display[category.name] = []

        for category, product in category_products:
                    category_product_display[category.name].append(product)

        return render_template('add_product_card.html', username = username, category_products = category_products)
   
    else:
        return redirect(url_for('admin_login'))

# @app.route('/')

@app.route('/get/product/<int:id>')
def get_product_using_id(id):
    if 'username' in session:
        username = session['username']
        
        get_product = Product.query.get(id)
        cat_id = get_product.category_id
        category = Category.query.get(cat_id)
        return render_template('cart_form.html', username = username, category = category, product = get_product)

        # products

        
    else:
        return redirect(url_for('admin_login'))
    

# --------------------------------------------------------- My Cart part --------------------------------------------------------------------------

def group_product_with_category(products):
    sum_of_price = 0
    cart_products = []
    for product in products:
        category = Category.query.get(product.category_id)
        cart_products.append((product, category))
        sum_of_price += product.total_price
    return cart_products, sum_of_price

@app.route('/get/product/cart')
def get_product_cart():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        products = My_cart.query.filter_by(user_id = user.id)
        cart_products, sum_price = group_product_with_category(products)
        return render_template('my_cart.html', username = username, cart_products = cart_products, sum_price = sum_price, user = user )


    else:
        redirect(url_for('user_login'))

@app.route('/add/product/cart/<int:id>', methods = ['POST', 'GET'])
def add_product_cart(id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first() 
        # product = Product.query.get(id)
        if request.method == 'POST':
            quantity = int(request.form['quantity'])
            # price = float(request.form['price'])
            product = Product.query.get(id)
            if quantity <= product.quantity:
                name = product.name
                unit = product.unit   
                cart = My_cart(name= name, quantity = quantity, price= product.price, unit= unit)
                cart.category_id = product.category_id
                cart.product_id = id
                cart.user_id = user.id
                db.session.add(cart)
                db.session.commit()
                products = My_cart.query.filter_by(user_id = user.id)
                cart_products, sum_price = group_product_with_category(products)
                # flash('Product added successfullly', 'success')
                return render_template('my_cart.html', username = username, cart_products = cart_products, sum_price = sum_price, user = user )
            else:
                flash(f'Quantity exceeds available stock. Please enter a quantity less than or equal to {product.quantity}.', 'danger') 
                return redirect(url_for('get_product_cart'))
    else:
        return redirect(url_for('user_login'))


@app.route('/delete/product/cart/<int:id>')
def delete_product_cart(id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first() 
        product = My_cart.query.get(id)
        db.session.delete(product)
        db.session.commit()
        get_products = My_cart.query.filter_by(user_id = user.id)
        if get_products:
            products = My_cart.query.filter_by(user_id = user.id)
            cart_products, sum_price = group_product_with_category(products)
            return render_template('my_cart.html', username = username, cart_products = cart_products, sum_price = sum_price, user = user ) 

        else:
            flash('NO product there in your card')
            return redirect(url_for('homepage'))
    else:
        return redirect(url_for('user_login'))
    
@app.route('/update/product/cart/<int:id>', methods = ['POST', 'GET'])
def update_product_cart(id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if request.method == 'POST':
            quantity = request.form['quantity']
            cart_product = My_cart.query.filter_by(id = id, user_id = user.id).first()
            product_id = cart_product.product_id
            available_quantity = int(cart_product.quantity) + int(quantity)
            product = Product.query.filter_by(id = product_id).first()
            if available_quantity < product.quantity:
                if cart_product.quantity == quantity:
                    products = My_cart.query.filter_by(user_id = user.id)
                    cart_products, sum_price = group_product_with_category(products)
                    return render_template('my_cart.html', username = username, cart_products = cart_products, sum_price = sum_price, user = user )
                else:
                    cart_product.quantity = quantity
                    db.session.commit()
                    products = My_cart.query.filter_by(user_id = user.id)
                    cart_products, sum_price = group_product_with_category(products)
                    return render_template('my_cart.html', username = username, cart_products = cart_products, sum_price = sum_price, user = user )
            else:
                order_quantity = int(product.quantity) - int(cart_product.quantity)
                flash(f'Quantity exceeds available stock. Please enter a quantity less than or equal to {order_quantity}.', 'danger') 
                return redirect(url_for('get_product_cart'))
        else:
            cart_product = My_cart.query.filter_by(id = id, user_id = user.id).first()
            category_id = cart_product.category_id
            category = Category.query.filter_by(id = category_id).first()
            return render_template('update_cart_form.html', username = username, product = cart_product, category = category )
            
        
    else:
        return redirect(url_for('user_login'))


@app.route('/buying/product/<int:id>', methods = ['POST', 'GET'])
def buying_product(id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first() 
        if request.method == 'POST':
            select_cart_products = My_cart.query.filter_by(user_id = id)
            for product in select_cart_products:
                purchase = Purchase(quantity= product.quantity, purchase_date=datetime.utcnow(),
                                     user_id = product.user_id, product_id = product.product_id)
                db.session.add(purchase)
                db_product = Product.query.get(product.product_id)
                # db_product.sold = 
                db_product.increment_sold(int(product.quantity))
                db_product.quantity -= int(product.quantity)

                cart_item = My_cart.query.get(product.id)
                db.session.delete(cart_item)
           
            db.session.commit()
            flash('Order has been placed. Thanks for the buying', 'success')
            return redirect(url_for('homepage'))


    else:
        return redirect(url_for('user_login'))
    

@app.route('/search', methods = ['GET', 'POST'])
def search():
   if request.method == 'POST':
       n_search = request.form['p_search']
       check = f'%{n_search}%'
       categories = Category.query.filter(Category.name.ilike(check)).all()
    #    print(categories)
       if categories:
            category_products = []
            category_product_display = {}
            # product = Product.query.filter_by(category_id = category.id)
            for category in categories:
                products = Product.query.filter_by(category_id = category.id).all()
                for product in products:
                    category_products.append((product, category))
            for  product,category in category_products:
                category_product_display[category.name] = []

            for  product,category in category_products:
                category_product_display[category.name].append(product)
            
            for category, products in category_product_display.items():
                category_product_display[category] = sorted(products, key=lambda x: x.id, reverse=True)

            if 'username' in session:
                   username = session['username']
                   return render_template('after_login_home.html', category_product_display = category_product_display, username = username)
            else:
                return render_template('home.html', category_product_display = category_product_display)
       else:
           products = Product.query.filter(Product.name.ilike(check)).all()
        #    print(products)
           if products:
               category_products = []
               category_product_display = {}
               for product in products:
                   category = Category.query.filter_by(id = product.category_id).first()
                   category_products.append((product, category))
               for  product, category in category_products:
                   category_product_display[category.name] = []
               for product, category in category_products:
                   category_product_display[category.name].append(product)

               for category, products in category_product_display.items():
                    category_product_display[category] = sorted(products, key=lambda x: x.id, reverse=True) 
               if 'username' in session:
                   username = session['username']
                   return render_template('after_login_home.html', category_product_display = category_product_display, username = username)
               else:   
                   return render_template('home.html', category_product_display = category_product_display)
           else:
               flash(f"don\'t have any category and product name of '{n_search}' name", 'warning')
               return redirect(url_for('homepage'))



@app.route('/summary')
def summary():
    if 'username' in session:
        username = session['username']
        purchases_all = Purchase.query.all()
        quantities = []
        categories = []
        for purchase in purchases_all:
            quantities.append(purchase.quantity)
            product = Product.query.filter_by(id = purchase.product_id).first()
            category = Category.query.filter_by(id = product.category_id).first()
            categories.append(category.name)
        plt.bar(categories, quantities)
        # plt.xlabel('category')
        plt.ylabel('quantity')
        plt.title('Category-wise products')
        plt.xticks(rotation = 45)
        plt.tight_layout()
        # plt.savefig('static/image/product_pic1.jpg')
        chart_name = 'products_pic1.jpg'
        # chart_path = app.static/image + '/' + chart_name
        chart_path = os.path.join(app.static_folder, 'image' , chart_name)
        plt.savefig(chart_path, format='jpg')
        plt.close()
        
        last_week = datetime.utcnow() - timedelta(days = 7)
        last_week_purchases = Purchase.query.filter(Purchase.purchase_date>= last_week).all()
        l_w_products = []
        l_w_quantities = []
        for purchase in last_week_purchases:
            l_w_quantities.append(purchase.quantity)
            product = Product.query.filter_by(id = purchase.product_id).first()
            l_w_products.append(product.name)

        plt.bar(l_w_products, l_w_quantities)
        # plt.xlabel('product')
        plt.ylabel('quantity')
        plt.title('products bought last week')
        plt.xticks(rotation = 45)
        plt.tight_layout()
        # plt.savefig('static/image/product_pic1.jpg')
        chart_name1 = 'products_pic2.jpg'
        # chart_path = app.static/image + '/' + chart_name
        chart_path = os.path.join(app.static_folder, 'image' , chart_name1)
        plt.savefig(chart_path, format='jpg')
        plt.close()

        # return render_template('summary.html', username = username, chart_name = chart_name)
        return render_template('summary.html', username = username)

    else:
        return redirect(url_for('admin_login'))

    

   


