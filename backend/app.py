from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', transactions=transactions)


@app.route('/all')
@login_required
def all_transactions():
    transactions = (
        db.session.query(Transaction, User.username)
        .join(User, Transaction.user_id == User.id)
        .all()
    )
    return render_template('all_transactions.html', transactions=transactions)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    from flask import request
    if request.method == 'POST':
        t = Transaction(
            user_id=current_user.id,
            date=request.form['date'],
            category=request.form['category'],
            amount=request.form['amount'],
            description=request.form['description'],
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_transaction.html')


@app.route('/edit/<int:tx_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(tx_id):
    from flask import request
    t = Transaction.query.get_or_404(tx_id)
    if t.user_id != current_user.id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        t.date = request.form['date']
        t.category = request.form['category']
        t.amount = request.form['amount']
        t.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_transaction.html', transaction=t)


@app.route('/delete/<int:tx_id>')
@login_required
def delete_transaction(tx_id):
    t = Transaction.query.get_or_404(tx_id)
    if t.user_id == current_user.id:
        db.session.delete(t)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask import request
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    from flask import request
    if request.method == 'POST':
        user = User(username=request.form['username'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized')

if __name__ == '__main__':
    app.run(debug=True)
