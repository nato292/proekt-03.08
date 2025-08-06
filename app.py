from flask import Flask, render_template, request, redirect, url_for, session, flash
from online_restaurant_db import Base, engine, Session, User, Menu, Orders, Reservation
from flask_login import LoginManager, current_user, login_required, login_user
import datetime
import secrets
import os

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['MAX_FORM_MEMORY_SIZE'] = 1024 * 1024  # 1MB
app.config['MAX_FORM_PARTS'] = 500

app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

app.config['SECRET_KEY'] = '#cv)3v7w$*s3fk;5c!@y0?:?№3"9)#'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        user = session.query(User).filter_by(id = user_id).first()
        if user:
            return user

@app.after_request
def apply_csp(response):
    nonce = secrets.token_urlsafe(16)
    csp = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'unsafe-inline'; " 
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp
    response.set_cookie('nonce', nonce)
    return response

@app.route('/')
@app.route('/home')
def home():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

    return render_template('home.html')


def init_cart():
    if "cart" not in session:
        session["cart"] = {}


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session_db = Session()
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if session_db.query(User).filter_by(username=username).first():
            return "Користувач вже існує"
        if session_db.query(User).filter_by(email=email).first():
            return "Пошта вже використовується"

        new_user = User(username=username, password=password, email=email)
        session_db.add(new_user)
        session_db.commit()
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session_db = Session()
        username = request.form['username']
        password = request.form['password']
        user = session_db.query(User).filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return "Невірні дані"
    return render_template("login.html")

@app.route('/menu')
def menu():
    products = [
        {
            'id': 1,
            'name': 'Голубці',
            'description': 'Традиційна українська страва з капустяного листя з начинкою з м’яса та рису, тушкована в томатному соусі..',
            'image_url': url_for('static', filename='menu/Golubchi.png')
        },
        {
            'id': 2,
            'name': 'Борщ',
            'description': 'Український національний суп на основі буряка з м’ясом і овочами.',
            'image_url': url_for('static', filename='menu/Borsh.png')
        },
        {
            'id': 3,
            'name': 'Вареники',
            'description': 'Традиційна українська страва з тіста з начинкою з картоплі.',
            'image_url': url_for('static', filename='menu/Vareniki.png')
        },
    ]
    return render_template('menu.html', products=products)


@app.route('/position/<int:id>')
def position(id):
    init_cart()
    products = {
        1: {
            'name': 'Голубці',
            'description': 'капустяне листя, свинячий або яловичий фарш, рис, морква, цибуля, сіль, перець, томатна паста, лавровий лист, соняшникова олія, сметана, часник, зелень',
            'price': 110,
            'image_url': url_for('static', filename='menu/Golubchi.png')
        },
        2: {
            'name': 'Борщ',
            'description': 'буряк, капуста, картопля, морква, цибуля, томатна паста, часник, лавровий лист, сіль, перець, свинячі або яловичі ребра, соняшникова олія, зелень, оцет, цукор, сметана',
            'price': 150,
            'image_url': url_for('static', filename='menu/Borsh.png')
        },
        3: {
            'name': 'Вареники',
            'description': 'борошно, вода, сіль, яйце, картопля, смажена цибуля, вершкове масло, чорний перець, сметана',
            'price': 130,
            'image_url': url_for('static', filename='menu/Vareniki.png')
        },
    }
    product = products.get(id)
    if not product:
        return "Страва не знайдена", 404
    
    product['id'] = id 
    return render_template('position.html', product=product, cart=session["cart"])


@app.route("/cart")
def cart():
    init_cart()
    return render_template("position.html", product=None, cart=session["cart"])

@app.route("/cart/update/<product_id>", methods=["POST"])
def update_cart(product_id):
    init_cart()
    quantity = int(request.form.get("quantity", 1))

    if quantity < 1 or quantity > 10:
        flash("Кількість повинна бути від 1 до 10")
    else:
        if product_id in session["cart"]:
            session["cart"][product_id]["quantity"] = quantity
            flash("Кількість оновлено")

    session.modified = True
    return redirect(url_for("cart"))


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    init_cart()

    products = {
        1: {'name': 'Голубці', 'price': 110},
        2: {'name': 'Борщ', 'price': 150},
        3: {'name': 'Вареники', 'price': 130},
    }

    product = products.get(product_id)
    if not product:
        return "Продукт не знайдено", 404

    str_id = str(product_id)

    if str_id in session["cart"]:
        if session["cart"][str_id]["quantity"] < 10:
            session["cart"][str_id]["quantity"] += 1
    else:
        session["cart"][str_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": 1
        }

    session.modified = True
    flash("Товар додано в кошик")
    return redirect(url_for("cart"))


@app.route("/cart/delete/<product_id>")
def delete_from_cart(product_id):
    init_cart()
    session["cart"].pop(product_id, None)
    flash("Товар видалено з кошика")
    session.modified = True
    return redirect(url_for("cart"))


@app.route('/create_order', methods=['GET','POST'])
def create_order():
    cart = session.get('cart')
    if request.method == 'POST':

        if request.form.get("csrf_token") != session["csrf_token"]:
            return "Запит заблоковано!", 403

        if not current_user:
            flash("Для оформлення замовлення необхідно бути зареєстрованим")
        else:
            if not cart:
                flash("Ваш кошик порожній")
            else:
                with Session() as cursor:
                    new_order = Orders(order_list = cart,order_time = datetime.now(), user_id=current_user.id)
                    cursor.add(new_order)
                    cursor.commit()
                    session.pop('cart')
                    cursor.refresh(new_order)
                    return redirect(f"/my_order/{new_order.id}")

    return render_template('create_order.html', csrf_token=session["csrf_token"], cart=cart)


@app.route('/my_orders')
@login_required
def my_orders():
    with Session() as cursor:
        us_orders = cursor.query(Orders).filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', us_orders=us_orders)

@app.route("/my_order/<int:id>")
@login_required
def my_order(id):
    with Session() as cursor:
        us_order = cursor.query(Orders).filter_by(id=id).first()
        total_price = sum(int(cursor.query(Menu).filter_by(name=i).first().price) * int(cnt) for i, cnt in us_order.order_list.items())
    return render_template('my_order.html', order=us_order, total_price=total_price)


############################### ADMINKA

@app.route('/add_menu', methods=['GET', 'POST'])
@login_required
def add_menu():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form.get("csrf_token") != session['csrf_token']:
            return "Запит заблоковано!", 403

        name = request.form['name']
        weight = request.form['weight']
        ingredients = request.form['ingredients']
        description = request.form['description']
        price = request.form['price']
        photo = request.files['photo']
        photo.save(os.path.join('static/menu', photo.filename))
        file_name = photo.filename
        with Session() as cursor:
            new_dish = Menu(
                name=name,
                weight=weight,
                ingredients=ingredients,
                description=description,
                price=int(price),
                active=True,
                file_name=file_name
            )
            cursor.add(new_dish)
            cursor.commit()
        return redirect(url_for('menu_check'))

    return render_template('add_menu.html', csrf_token=session["csrf_token"])


@app.route('/menu_check', methods=['GET', 'POST'])
@login_required
def menu_check(request):
    if current_user.username != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form.get("csrf_token") != session['csrf_token']:
            return "Запит заблоковано!", 403

        position_id = request.form['pos_id']
        with Session() as cursor:
            position_obj = cursor.query(Menu).filter_by(id=position_id).first()
            if 'change_status' in request.form:
                position_obj.active = not position_obj.active
            elif 'delete_position' in request.form:
                cursor.delete(position_obj)
            cursor.commit()

    with Session() as cursor:
        all_positions = cursor.query(Menu).all()
    return render_template('check_menu.html', all_positions=all_positions, csrf_token=session["csrf_token"])


@app.route('/all_users')
@login_required
def all_users():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    with Session() as cursor:
        all_users = cursor.query(User).with_entities(User.id, User.nickname, User.email).all()
    return render_template('all_users.html', all_users=all_users)

@app.route('/orders_check', methods=['GET', 'POST'])
@login_required
def orders_check():
    if current_user.nickname != 'Admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form.get("csrf_token") != session['csrf_token']:
            return "Запит заблоковано!", 403

        order_id = request.form['order_id']
        with Session() as cursor:
            order_obj = cursor.query(Orders).filter_by(id=order_id).first()
            
            if 'delete_order' in request.form:
                cursor.delete(order_obj)
            cursor.commit()

    with Session() as cursor:
        all_orders = cursor.query(Orders).all()
    return render_template('check_orders.html', all_orders=all_orders, csrf_token=session["csrf_token"])

@app.route('/reserved', methods=['GET', 'POST'])
@login_required
def reserved():
    if request.method == "POST":
        if request.form.get("csrf_token") != session["csrf_token"]:
            return "Запит заблоковано!", 403


        table_type = request.form['table_type']
        reserved_time_start = request.form['time']

        with Session() as cursor:
            reserved_check = cursor.query(Reservation).filter_by(type_table=table_type).count()
            user_reserved_check = cursor.query(Reservation).filter_by(user_id=current_user.id).first()


            message = f'Бронь на {reserved_time_start} столика на {table_type} людини успішно створено!'
            if  not user_reserved_check:
                new_reserved = Reservation(type_table=table_type, time_start=reserved_time_start, user_id=current_user.id)
                cursor.add(new_reserved)
                cursor.commit()
            elif user_reserved_check:
                message = 'Можна мати лише одну активну бронь'
            else:
                message = 'На жаль, бронь такого типу стола наразі неможлива'
            return render_template('reserved.html', message=message, csrf_token=session["csrf_token"])
    return render_template('reserved.html', csrf_token=session["csrf_token"])

@app.route('/reservations_check', methods=['GET', 'POST'])
@login_required
def reservations_check():
    if current_user.username != 'Admin':
        return redirect(url_for('home'))

    if request.method == "POST":
        if request.form.get("csrf_token") != session["csrf_token"]:
            return "Запит заблоковано!", 403


        reserv_id = request.form['reserv_id']
        with Session() as cursor:
            reservation = cursor.query(Reservation).filter_by(id=reserv_id).first()
            cursor.delete(reservation)
            cursor.commit()


    with Session() as cursor:
        all_reservations = cursor.query(Reservation).all()
        return render_template('reservations_check.html', all_reservations=all_reservations, csrf_token=session["csrf_token"])


if __name__ == "__main__":
    app.run(host="0.0.0.0")


