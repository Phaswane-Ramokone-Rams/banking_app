from flask import Flask, render_template, request, redirect, session, flash
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'database.txt'

def read_database():
    """Reads all accounts from the database file."""
    if not os.path.exists(DATABASE):
        with open(DATABASE, 'w'): pass  # Create the file if it doesn't exist
    with open(DATABASE, 'r') as db:
        return [eval(line.strip()) for line in db if line.strip()]

def write_to_database(record):
    """Writes a single record to the database."""
    with open(DATABASE, 'a') as db:
        db.write(f"{record}\n")

def update_database(data):
    """Overwrites the database with updated data."""
    with open(DATABASE, 'w') as db:
        for record in data:
            db.write(f"{record}\n")

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        id_number = request.form['id_number']
        username = request.form['username']
        password = request.form['password']
        
        account_number = str(uuid.uuid4().int)[:10]
        new_account = {
            'name': name,
            'phone': phone,
            'id_number': id_number,
            'username': username,
            'password': password,
            'account_number': account_number,
            'balance': 0,
            'transactions': []
        }
        accounts = read_database()
        
        # Check for duplicate username
        if any(acc['username'] == username for acc in accounts):
            flash('Username already exists. Please use a different one.', 'danger')
            return redirect('/register')

        write_to_database(new_account)
        flash('Account created successfully! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        accounts = read_database()

        # Check if username and password match
        user_accounts = [acc for acc in accounts if acc['username'] == username and acc['password'] == password]
        if user_accounts:
            session['user'] = user_accounts[0]
            session['user_accounts'] = user_accounts
            return redirect('/dashboard')
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    user_accounts = session['user_accounts']
    current_account = user_accounts[0]
    
    if request.method == 'POST':
        action = request.form['action']
        amount = float(request.form['amount'])
        accounts = read_database()

        # Locate the account being modified
        account_to_modify = next(acc for acc in accounts if acc['account_number'] == current_account['account_number'])

        if action == 'deposit':
            account_to_modify['balance'] += amount
            account_to_modify['transactions'].append({'type': 'Deposit', 'amount': amount})
            flash(f'Successfully deposited ${amount:.2f}', 'success')
        
        elif action == 'withdraw':
            if amount > account_to_modify['balance']:
                flash('Insufficient funds.', 'danger')
            else:
                account_to_modify['balance'] -= amount
                account_to_modify['transactions'].append({'type': 'Withdrawal', 'amount': amount})
                flash(f'Successfully withdrew ${amount:.2f}', 'success')

        # Update the database
        update_database(accounts)
        session['user_accounts'] = [acc for acc in accounts if acc['username'] == session['user']['username']]

    return render_template('dashboard.html', user=current_account, user_accounts=user_accounts)

@app.route('/transactions/<account_number>')
def transactions(account_number):
    if 'user' not in session:
        return redirect('/login')
    
    accounts = read_database()
    account = next(acc for acc in accounts if acc['account_number'] == account_number)
    return render_template('transaction.html', transactions=account['transactions'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_accounts', None)
    flash('Logged out successfully.', 'success')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)


