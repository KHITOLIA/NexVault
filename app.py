from flask import Flask, render_template, request, redirect,url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import hashlib,time
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import numpy as np
from send_email import send_welcome_email, send_forget_pin
load_dotenv()
import os

app = Flask(__name__)
app.secret_key = 'secret'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  


import os

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atm.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 280,
    "pool_pre_ping": True,
    "pool_timeout": 30
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= USER TABLE =================
class User(db.Model):
    __tablename__ = 'users'

    account_no = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    pin = db.Column(db.String(256), nullable=False)
    balance = db.Column(db.Float, default=0)

    role = db.Column(db.String(10), default='user')

    withdraw_limit = db.Column(db.Float, default=20000)
    deposit_limit = db.Column(db.Float, default=20000)
    transfer_limit = db.Column(db.Float, default=10000)

    failed_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    lock_time = db.Column(db.Float)

    security_answer = db.Column(db.String(100))

    # 🔗 relationships (optional but useful)
    transactions = db.relationship('Transaction', backref='user', lazy=True)


# ================= TRANSACTION TABLE =================
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)

    account_no = db.Column(
        db.String(20),
        db.ForeignKey('users.account_no'),
        nullable=False
    )

    type = db.Column(db.String(20))  # deposit, withdraw, send, receive
    amount = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now)


# ================= TRANSFER TABLE =================
class Transfer(db.Model):
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)

    send_account_no = db.Column(
        db.String(20),
        db.ForeignKey('users.account_no'),
        nullable=False
    )

    receive_account_no = db.Column(
        db.String(20),
        db.ForeignKey('users.account_no'),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.now)
    

def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()

# routings

@app.route("/")
def home():
    # admin = User(
    # account_no="7827458285",
    # name="Admin",
    # pin=hash_pin("2026"),
    # balance=0,
    # email = 'tushar@trainingbasket.co',
    # role="admin")
    # db.session.add(admin)
    # db.session.commit()
    return render_template("home.html")

#====================registration=================
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        account_no = str(np.random.randint(1000000,9999999))
        user = User(account_no = account_no, 
                    name = request.form['name'], 
                    pin = hash_pin(request.form['pin']), 
                    balance = request.form['balance'], 
                    email = request.form['email'],
                    security_answer = request.form['security_answer'])
        send_welcome_email(user.email, user.name, user.account_no, request.form['pin'])
        db.session.add(user)
        db.session.commit()
        msg = f'Your account has been created \n Account No: {account_no} \n please login to use services'
        return render_template('home.html', msg = msg)
    
    return render_template('register.html')


#===================login=================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.get(request.form['account'])

        if not user:
            return render_template('login.html', error="Account not found")
        
        else:  

            if user.is_locked:
                if time.time() - user.lock_time < 180:
                    return render_template('login.html', error="Account locked")
                else:
                    user.failed_attempts = 0
                    user.is_locked = False

            if user.pin == hash_pin(request.form['pin']):
                session['account'] = user.account_no
                user.failed_attempts = 0
                db.session.commit()
                return  redirect(url_for('dashboard'))
            user.failed_attempts += 1
            if user.failed_attempts >= 3:
                user.is_locked = True
                user.lock_time = time.time()

            db.session.commit()
            return render_template('login.html', error="Wrong PIN")

    return render_template('login.html')


# ===================== DASHBOARD =====================   
@app.route('/dashboard')
def dashboard():
    if 'account' not in session:
        return redirect('/login')
    user = User.query.get(session['account'])
    return render_template('dashboard.html', user=user)


# ===================== BALANCE =====================
@app.route('/check_balance')
def check_balance():
    if 'account' not in session:
        return redirect('/login')
    
    user = User.query.get(session['account'])
    balance = user.balance
    return render_template('balance.html', balance = balance)


# ===================== CHANGE PIN =====================
@app.route('/change_pin', methods = ['Get', 'POST'])
def change_pin():
    if request.method == 'POST':
        if 'account' not in session:
            return redirect('/login')
        
        user = User.query.get(session['account'])

        if hash_pin(request.form['old_pin']) == user.pin:
            user.pin = hash_pin(request.form['new_pin'])
            db.session.commit()

        return render_template('change_pin.html', msg = 'Pin Changed successfully')
    
    return render_template('change_pin.html')


# ===================== DEPOSIT =====================
@app.route('/deposit', methods = ['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        if 'account' not in session:
            return redirect('/login')
        
        user = User.query.get(session['account'])
        amount = float(request.form['amount'])
        start = datetime.combine(date.today(), datetime.min.time())
        end = start + timedelta(days=1)
        transactions = Transaction.query.filter(
                        Transaction.account_no == user.account_no,
                        Transaction.type == "deposit",
                        Transaction.timestamp >= start,
                        Transaction.timestamp < end
                    ).all()
        if transactions:
            
            total_deposit = sum(t.amount for t in transactions)
            
            remaining_limit = user.deposit_limit - total_deposit

            if amount > remaining_limit:
                
                return render_template('deposit.html', msg = f"Daily limit exceed Remaining Limit: {remaining_limit}")
        

        user.balance += amount
        db.session.add(Transaction(
                        account_no=user.account_no,
                        type="deposit",
                        amount=amount
                    ))
        db.session.commit()
        msg = f'''A/c {"XX" + str(user.account_no)[-4:]} credited INR {amount} on {datetime.now()} Bal INR {user.balance}'''
        return render_template('W_D_success.html', msg = msg)
    
    return render_template('deposit.html')


# ===================== WITHDRAW =====================
@app.route('/withdraw', methods = ['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        if 'account' not in session:
            return redirect('/login')
        
        user = User.query.get(session['account'])
        amount = float(request.form['amount'])
        start = datetime.combine(date.today(), datetime.min.time())
        end = start + timedelta(days=1)
        transactions = Transaction.query.filter(
                        Transaction.account_no == user.account_no,
                        Transaction.type == "withdraw",
                        Transaction.timestamp >= start,
                        Transaction.timestamp < end
                    ).scalar()
        
        total_withdraw = sum(t.amount for t in transactions)
        
        remaining_limit = user.withdraw_limit - total_withdraw

        if amount > remaining_limit:
            
            return render_template('withdraw.html', msg = f"Daily limit exceed Remaining Limit: {remaining_limit}")
        
        user.balance -= amount
        db.session.add(Transaction(
                        account_no=user.account_no,
                        type="withdraw",
                        amount=amount
                    ))
        db.session.commit()
        msg = f'''A/c {"XX" + str(user.account_no)[-4:]} debited INR {amount} on {datetime.now()} Bal INR {user.balance}'''
        return render_template('W_D_success.html', msg = msg)    

    return render_template('withdraw.html')


# ===================== details =====================
@app.route('/show_details')
def show_details():
    if "account" not in session:
        return redirect("/")
    user = User.query.get(session['account'])
    details = f"""
    Account No : {user.account_no}
    Balance : {user.balance}
    Name : {user.name}
            """
    return render_template('detail.html', details = details)


@app.route("/transfer", methods = ['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        if "account" not in session:
            return redirect("/login")
        sender = User.query.get(session['account'])
        receiver = User.query.get(request.form['receiver'])
        amount = float(request.form['amount'])

        if not receiver:
            return render_template('W_D_success.html', msg = 'receiver not found')
        
        if amount > sender.balance:
            return render_template('transaction.html', msg = 'Insufficient Balance')

        if amount > sender.transfer_limit:
            return render_template('transaction.html', msg = 'Transaction Limit Exceed')
        
        sender.balance -= amount
        receiver.balance += amount

        db.session.add(Transfer(
                        send_account_no=sender.account_no,
                        receive_account_no=receiver.account_no,
                        amount=amount
                    ))
        db.session.commit()
        return render_template('transfer.html', msg = 'Transfer Successfull')
    return render_template('transfer.html')


@app.route('/bank_statement', methods=['GET', 'POST'])
def bank_statement():

    if "account" not in session:
        return redirect("/")

    user_acc = session['account']

    if request.method == 'POST':

        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d") + timedelta(days=1)

        transactions = Transaction.query.filter(
            Transaction.account_no == user_acc,
            Transaction.timestamp >= start_date,
            Transaction.timestamp < end_date   # 🔥 important fix
        ).order_by(Transaction.timestamp.desc()).all()

        transfers = Transfer.query.filter(
            (
                (Transfer.send_account_no == user_acc) |
                (Transfer.receive_account_no == user_acc)
            ),
            Transfer.timestamp >= start_date,
            Transfer.timestamp < end_date   # 🔥 important fix
        ).order_by(Transfer.timestamp.desc()).all()

        total_deposit = 0
        total_withdraw = 0
        total_sent = 0
        total_received = 0

        # Transactions (deposit/withdraw only)
        for t in transactions:
            if t.type == 'deposit':
                total_deposit += t.amount
            elif t.type == 'withdraw':
                total_withdraw += t.amount

        # Transfers (send/receive)
        for tr in transfers:
            if tr.send_account_no == user_acc:
                total_sent += tr.amount
            elif tr.receive_account_no == user_acc:
                total_received += tr.amount

        return render_template(
            'statement.html',
            transactions=transactions,
            transfers=transfers,
            total_deposit=total_deposit,
            total_withdraw=total_withdraw,
            total_sent=total_sent,
            total_received=total_received
        )
    return render_template('statement_form.html')



@app.route("/forget_pin", methods = ['GET','POST'])
def forget_pin():
    
    if request.method == 'POST':
        user = User.query.get(request.form['account_no'])
        security_asnwer = request.form['security_answer']
        if user and security_asnwer == user.security_answer:
            user.pin = hash(np.random.randint(100000, 9999999))
            send_forget_pin(user.name, user.account_no, user.pin, user.email)
            db.session.commit()
            return render_template('home.html', msg = 'PIN reset successfull')
        return render_template('home.html', msg = "Account not Found or Wrong Answer")
        
    return render_template('forget_pin.html')        
    
@app.route("/change_limit", methods=['GET', 'POST'])
def change_limit():
    if "account" not in session:
        return redirect("/")

    user = User.query.get(session['account'])

    if request.method == 'POST':
        type_of_limit = request.form['limit_type']

        try:
            if type_of_limit == 'deposit':
                user.deposit_limit = float(request.form['deposit_limit'])

            elif type_of_limit == 'withdraw':
                user.withdraw_limit = float(request.form['withdraw_limit'])

            elif type_of_limit == 'transfer':
                user.transfer_limit = float(request.form['transfer_limit'])

            db.session.commit()
            msg = f"{type_of_limit} limit updated successfully"

        except:
            msg = "Invalid input!"

        return render_template('change_limit.html', msg=msg)

    return render_template("change_limit.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template('home.html')


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
