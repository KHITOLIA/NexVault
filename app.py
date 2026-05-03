from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import hashlib, time
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import numpy as np

load_dotenv()
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "nexvault-secret-2025")

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
    transactions = db.relationship('Transaction', backref='user', lazy=True)


# ================= TRANSACTION TABLE =================
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(20), db.ForeignKey('users.account_no'), nullable=False)
    type = db.Column(db.String(20))
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


# ================= TRANSFER TABLE =================
class Transfer(db.Model):
    __tablename__ = 'transfers'

    id = db.Column(db.Integer, primary_key=True)
    send_account_no = db.Column(db.String(20), db.ForeignKey('users.account_no'), nullable=False)
    receive_account_no = db.Column(db.String(20), db.ForeignKey('users.account_no'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()


# ==================== HOME ====================
@app.route("/")
def home():
    return render_template("home.html")


# ==================== REGISTER ====================
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account_no = str(np.random.randint(1000000, 9999999))
        user = User(
            account_no=account_no,
            name=request.form['name'],
            pin=hash_pin(request.form['pin']),
            balance=request.form['balance'],
            email=request.form['email'],
            security_answer=request.form['security_answer']
        )
        db.session.add(user)
        db.session.commit()

        # Send email AFTER saving — so a mail failure doesn't break registration

        msg = f'Account created successfully! Account No: {account_no} — please login.'
        return render_template('home.html', msg=msg)

    return render_template('register.html')


# ==================== LOGIN ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.get(request.form['account'])

        if not user:
            return render_template('login.html', error="Account not found")

        if user.is_locked:
            if time.time() - user.lock_time < 180:
                return render_template('login.html', error="Account locked for 3 minutes due to failed attempts")
            else:
                user.failed_attempts = 0
                user.is_locked = False

        if user.pin == hash_pin(request.form['pin']):
            session['account'] = user.account_no
            user.failed_attempts = 0
            db.session.commit()
            return redirect(url_for('dashboard'))   # ← correct redirect

        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.is_locked = True
            user.lock_time = time.time()

        db.session.commit()
        return render_template('login.html', error="Wrong PIN")

    return render_template('login.html')


# ==================== DASHBOARD ====================
@app.route('/dashboard')
def dashboard():
    if 'account' not in session:
        return redirect('/login')
    user = User.query.get(session['account'])
    return render_template('dashboard.html', user=user)


# ==================== BALANCE ====================
@app.route('/check_balance')
def check_balance():
    if 'account' not in session:
        return redirect('/login')
    user = User.query.get(session['account'])
    return render_template('balance.html', balance=user.balance)


# ==================== CHANGE PIN ====================
@app.route('/change_pin', methods=['GET', 'POST'])
def change_pin():
    if 'account' not in session:
        return redirect('/login')

    if request.method == 'POST':
        user = User.query.get(session['account'])
        if hash_pin(request.form['old_pin']) == user.pin:
            user.pin = hash_pin(request.form['new_pin'])
            db.session.commit()
            return render_template('change_pin.html', msg='PIN changed successfully')
        else:
            return render_template('change_pin.html', msg='Current PIN is incorrect')

    return render_template('change_pin.html')


# ==================== DEPOSIT ====================
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'account' not in session:
        return redirect('/login')

    if request.method == 'POST':
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

        total_deposit = sum(t.amount for t in transactions)
        remaining_limit = user.deposit_limit - total_deposit

        if amount > remaining_limit:
            return render_template('deposit.html', msg=f"Daily limit exceeded. Remaining: ₹{remaining_limit:,.2f}")

        user.balance += amount
        db.session.add(Transaction(account_no=user.account_no, type="deposit", amount=amount))
        db.session.commit()

        msg = f'A/c XX{str(user.account_no)[-4:]} credited INR {amount} on {datetime.now().strftime("%d %b %Y %I:%M %p")} | Bal INR {user.balance:,.2f}'
        return render_template('W_D_success.html', msg=msg)

    return render_template('deposit.html')


# ==================== WITHDRAW ====================
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'account' not in session:
        return redirect('/login')

    if request.method == 'POST':
        user = User.query.get(session['account'])
        amount = float(request.form['amount'])

        if amount > user.balance:
            return render_template('withdraw.html', msg="Insufficient balance")

        start = datetime.combine(date.today(), datetime.min.time())
        end = start + timedelta(days=1)

        # ✅ FIXED: was .scalar() which caused a crash — must be .all()
        transactions = Transaction.query.filter(
            Transaction.account_no == user.account_no,
            Transaction.type == "withdraw",
            Transaction.timestamp >= start,
            Transaction.timestamp < end
        ).all()

        total_withdraw = sum(t.amount for t in transactions)
        remaining_limit = user.withdraw_limit - total_withdraw

        if amount > remaining_limit:
            return render_template('withdraw.html', msg=f"Daily limit exceeded. Remaining: ₹{remaining_limit:,.2f}")

        user.balance -= amount
        db.session.add(Transaction(account_no=user.account_no, type="withdraw", amount=amount))
        db.session.commit()

        msg = f'A/c XX{str(user.account_no)[-4:]} debited INR {amount} on {datetime.now().strftime("%d %b %Y %I:%M %p")} | Bal INR {user.balance:,.2f}'
        return render_template('W_D_success.html', msg=msg)

    return render_template('withdraw.html')


# ==================== DETAILS ====================
@app.route('/show_details')
def show_details():
    if "account" not in session:
        return redirect("/login")
    user = User.query.get(session['account'])
    details = f"""
    Account No : {user.account_no}
    Balance : {user.balance}
    Name : {user.name}
    """
    return render_template('detail.html', details=details)


# ==================== TRANSFER ====================
@app.route("/transfer", methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        if "account" not in session:
            return redirect("/login")

        sender = User.query.get(session['account'])
        receiver = User.query.get(request.form['receiver'])
        amount = float(request.form['amount'])

        if not receiver:
            return render_template('transfer.html', msg='Receiver account not found')

        if amount > sender.balance:
            return render_template('transfer.html', msg='Insufficient balance')

        if amount > sender.transfer_limit:
            return render_template('transfer.html', msg='Transfer limit exceeded')

        sender.balance -= amount
        receiver.balance += amount

        db.session.add(Transfer(
            send_account_no=sender.account_no,
            receive_account_no=receiver.account_no,
            amount=amount
        ))
        db.session.commit()
        return render_template('transfer.html', msg='Transfer successful')

    return render_template('transfer.html')


# ==================== BANK STATEMENT ====================
@app.route('/bank_statement', methods=['GET', 'POST'])
def bank_statement():
    if "account" not in session:
        return redirect("/login")

    user_acc = session['account']

    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d") + timedelta(days=1)

        transactions = Transaction.query.filter(
            Transaction.account_no == user_acc,
            Transaction.timestamp >= start_date,
            Transaction.timestamp < end_date
        ).order_by(Transaction.timestamp.desc()).all()

        transfers = Transfer.query.filter(
            (Transfer.send_account_no == user_acc) | (Transfer.receive_account_no == user_acc),
            Transfer.timestamp >= start_date,
            Transfer.timestamp < end_date
        ).order_by(Transfer.timestamp.desc()).all()

        total_deposit = sum(t.amount for t in transactions if t.type == 'deposit')
        total_withdraw = sum(t.amount for t in transactions if t.type == 'withdraw')
        total_sent = sum(tr.amount for tr in transfers if tr.send_account_no == user_acc)
        total_received = sum(tr.amount for tr in transfers if tr.receive_account_no == user_acc)

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


# ==================== FORGET PIN ====================
@app.route("/forget_pin", methods=['GET', 'POST'])
def forget_pin():
    if request.method == 'POST':
        user = User.query.get(request.form['account_no'])
        security_answer = request.form['security_answer']

        if user and security_answer == user.security_answer:
            new_pin = str(np.random.randint(100000, 999999))          # ✅ FIXED: hash() is not hashlib
            user.pin = hash_pin(new_pin)
            db.session.commit()
            try:
                from send_email import send_forget_pin
                send_forget_pin(user.name, user.account_no, new_pin, user.email)
            except Exception as e:
                print(f"Email failed: {e}")
            return render_template('home.html', msg='PIN reset successful — check your email')

        return render_template('home.html', msg="Account not found or wrong answer")

    return render_template('forget_pin.html')


# ==================== CHANGE LIMIT ====================
@app.route("/change_limit", methods=['GET', 'POST'])
def change_limit():
    if "account" not in session:
        return redirect("/login")

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
            msg = f"{type_of_limit.capitalize()} limit updated successfully"
        except Exception as e:
            msg = f"Invalid input: {e}"

        return render_template('change_limit.html', msg=msg)

    return render_template("change_limit.html")


# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')


# ==================== INIT DB + RUN ====================
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))           # ✅ FIXED: reads Railway's PORT
    app.run(host="0.0.0.0", port=port, debug=False)    # ✅ FIXED: host must be 0.0.0.0
