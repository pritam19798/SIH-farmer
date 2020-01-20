from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = mysql.connector.connect(host="remotemysql.com", user="5y7pgTHrDJ", password="0f1tf9vYUw",
                               database="5y7pgTHrDJ")

cursor = conn.cursor()


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register/farmer')
def register():
    return render_template('register.html', user='f')


@app.route('/register/vender')
def registerv():
    return render_template('register.html', user='v')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')
    session['login'] = request.form['user']
    if session['login'] == 'f':
        cursor.execute(
            """SELECT * FROM `Farmer`  WHERE `Email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
        myuser = cursor.fetchall()
        if len(myuser) > 0:
            session['farmer_ID'] = myuser[0][0]
            return redirect('/account')
        else:
            return redirect('/')
    elif session['login'] == 'v':
        cursor.execute(
            """SELECT * FROM `Vender`  WHERE `Email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
        myvender = cursor.fetchall()
        if len(myvender) > 0:
            session['vender_ID'] = myvender[0][0]

            return redirect('/account')
        else:
            return redirect('/')
    else:
        return redirect('/')


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute(
        """INSERT INTO `Farmer` (`farmer_ID`, `farmer_name`, `Email`, `password`) 
        VALUES(NULL,'{}', '{}' , '{}')""".format(name, email, password))
    conn.commit()
    cursor.execute("""SELECT * FROM `Farmer` WHERE `Email` LIKE '{}'""".format(email))
    return redirect('/')


@app.route('/add_vender', methods=['POST'])
def add_vender():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute(
        """INSERT INTO `Vender` (`vender_ID`, `vender_name`, `Email`, `password`) 
        VALUES(NULL,'{}', '{}' , '{}')""".format(name, email, password))
    conn.commit()
    cursor.execute("""SELECT * FROM `Vender` WHERE `Email` LIKE '{}'""".format(email))
    return redirect('/')


@app.route('/logout')
def logout():
    if session['login'] == 'f':
        session.pop('farmer_ID')
        session['login'] = ''
    elif session['login'] == 'v':
        session.pop('vender_ID')
        session['login'] = ''
    return redirect('/')


@app.route('/account')
def account():
    d = {}
    if session['login'] == 'f':
        if 'farmer_ID' in session:
            cursor.execute("""SELECT * FROM `Product` WHERE `far_id` LIKE '{}'""".format(session['farmer_ID']))
            myproduct = cursor.fetchall()
            return render_template('acccount.html', var=session['farmer_ID'], prods=myproduct, login=session['login'])
        else:
            return redirect('/dunny')
    elif session['login'] == 'v':
        if 'vender_ID' in session:
            cursor.execute("""SELECT * FROM `Product` """)
            myproduct = cursor.fetchall()
            for i in myproduct:
                if i[4] not in d:
                    cursor.execute("""SELECT * FROM `Farmer`  WHERE `farmer_ID` LIKE '{}'""".format(i[4]))
                    f = cursor.fetchall()
                    d[i[4]] = f[0]
            return render_template('acccount.html', var=session['vender_ID'], prods=myproduct, cursor=cursor, d=d,
                                   login=session['login'])
        else:
            return redirect('/dunny')


@app.route('/bid', methods=['POST'])
def bid():
    prod_id = int(request.form.get('prod_id'))
    far_id = int(request.form.get('far_id'))
    far_price = int(request.form.get('far_price'))
    bid_price = int(request.form.get('bid_price'))
    cursor.execute("""SELECT * FROM `Bid` WHERE `far_id` LIKE '{}' AND `pro_id` LIKE '{}'""".format(far_id, prod_id))
    mybid = cursor.fetchall()
    if not (len(mybid) > 0):
        cursor.execute(
            """INSERT INTO `Bid`(`bid_id`, `pro_id`, `far_id`, `far_price`, `bid_price`, `vender_id`) 
            VALUES(NULL,'{}', '{}' , '{}','{}' , '{}')""".format(prod_id, far_id, far_price, bid_price,
                                                                 session['vender_ID']))
        conn.commit()
    else:
        cursor.execute(
            """UPDATE `Bid` SET `bid_price`='{}' WHERE `far_id` LIKE '{}' AND `pro_id` LIKE '{}' """
                .format(bid_price, far_id, prod_id))
        conn.commit()
        print('edit')
    return redirect('/account')


@app.route('/post_product', methods=['POST'])
def post_product():
    if session['farmer_ID'] >= 1:
        return render_template('post_product.html', var=session['farmer_ID'])
    else:
        return redirect('/dunny')


@app.route('/post_validation', methods=['POST'])
def post_validation():
    product = request.form.get('product')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    details = request.form.get('detail')
    if int(price) >= 0 and int(quantity) >= 1:
        cursor.execute(
            """INSERT INTO `Product` (`product_ID`, `product`, `quantity`, `price`, `far_ID`, `description`) 
            VALUES(NULL,'{}', '{}' , '{}','{}', '{}' )""".format(product, quantity, price, session['farmer_ID'],
                                                                 details))
        conn.commit()

        if session['farmer_ID'] >= 1:
            return redirect('/account')
        else:
            return redirect('/dunny')


@app.route('/account/profile_farmer')
def profile_f():
    return render_template('profile.html', user='f')


@app.route('/account/profile_vender')
def profile_v():
    return render_template('profile.html', user='v')


@app.route('/add_profile', methods=['POST'])
def profile():
    address = request.form.get('address')
    address2 = request.form.get('address2')
    zip = request.form.get('zip')
    if session['login'] == 'f':
        cursor.execute(
                """INSERT INTO `farmer_details` (`description_id`, `far_ID`, `address`, `address2`, `zip`) 
             VALUES(NULL, '{}', '{}', '{}', '{}')""".format(session['farmer_ID'],address, address2, zip))
    else:
        cursor.execute(
            """INSERT INTO `vender_details` (`description_id`, `vender_ID`, `address`, `address2`, `zip`) 
         VALUES(NULL, '{}', '{}', '{}', '{}')""".format(session['vender_ID'], address, address2, zip))
    conn.commit()
    return redirect('/account/profile')


@app.route('/account/profile')
def profile_show():
    if session['login'] == 'f':
        cursor.execute("SELECT * FROM `farmer_details`")
        profile = cursor.fetchall()
        return render_template('profile_show.html', data=profile)
    else:
        cursor.execute("SELECT * FROM `vender_details`")
        profile = cursor.fetchall()
        return render_template('profile_show.html', data=profile)


if __name__ == "__main__":
    app.run(debug=True)
