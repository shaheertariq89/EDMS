from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,session
import pyodbc
import os
from datetime import datetime

app = Flask(__name__)
secret_key = os.urandom(24).hex()
app.secret_key = secret_key
Name =None
# Define the database connection function
def connect_to_database():
    try:
        conn = pyodbc.connect(Driver='{SQL Server};'
                              'Server=DESKTOP-O9I1B8F;'
                              'Database=Kaavish_record;'
                              'Trusted_connection=Yes;', timeout=30)
        print("connected")
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    global Name

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT *, name FROM LoginPage WHERE username = ? AND password = ?", (username, password))

            user = cursor.fetchone()
            if user:
                # Retrieve the name and assign it to the global variable
                Name = user.name  # Assuming the column name is 'name'
                conn.close()
                print('Name of user is :', Name)
                return redirect(url_for('selection_screen'))
            else:
                flash('Invalid username or password. Please try again.', 'error')
        else:
            flash('Error connecting to the database. Please try again later.', 'error')

    return render_template('login.html')


@app.route('/selection_screen', methods=['GET', 'POST'])
def selection_screen():
    if request.method == 'POST':
        if 'gate_pass_type' in request.form:
            gate_pass_type = request.form['gate_pass_type']
            if gate_pass_type == 'outward':
                return redirect(url_for('inward_gatepass_form'))
            elif gate_pass_type == 'inward':
                return redirect(url_for('out'))
            elif gate_pass_type == 'expense':
                return redirect(url_for('expense'))
            elif gate_pass_type == 'donation':
                return redirect(url_for('donation'))
        elif 'record' in request.form:
            record = request.form['record']
            if record == 'expense':
                return redirect(url_for('expense'))
            elif record == 'donation':
                return redirect(url_for('donation'))

    return render_template('selection_screen.html')

# Inward GatePass Form route
@app.route('/inward_gatepass_form', methods=['GET', 'POST'])
def inward_gatepass_form():
    global Name
    if request.method == 'POST':
        # Retrieve form data
        list = request.form['list']
        description = request.form['description']
        amount = request.form['amount']
        project= request.form['project']
        approved_by = request.form['approved_by']
        # Insert data into the database
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Expense (
                                  list,
                                  description,
                                  amount,
                                  project,
                                  approved_by,
                                  date
                              ) VALUES (?, ?, ?, ?, ?, GETDATE())""",
                           (list, description, amount, project, f'{approved_by} by {Name}'))

            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            if affected_rows == 0:
                # Pass the message to the template
                return render_template('inward_gatepass_form.html', message="Data already present")
            else:
                print('Data Saved Successfully :)')
                return render_template('inward_gatepass_form.html', message="Data saved successfully")
        else:
            flash('Error connecting to the database. Please try again later.', 'error')

    else:
        return render_template('inward_gatepass_form.html', message=None )

name1=None
project1=None
# Inward GatePass Form route
@app.route('/donation', methods=['GET', 'POST'])
def donation():
    global Name
    global name1, project1
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        project = request.form['project']

        # Connect to the database
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()

            # Execute SQL query to sum up the amount
            cursor.execute("""SELECT SUM(amount) AS total_amount 
                              FROM donation 
                              WHERE name = ? AND project = ?""", (name, project))
            total_amount = cursor.fetchone()[0]
            name1=name
            project1=project
            conn.close()

            # Check if total_amount is not None
            if total_amount is not None:
                # Pass total_amount to the template
                return render_template('donation.html', total_amount=total_amount)
            else:
                return render_template('donation.html', message="No data found for the given criteria")
        else:
            flash('Error connecting to the database. Please try again later.', 'error')

    else:
        return render_template('donation.html', message=None)


name12=None
@app.route('/expense', methods=['GET', 'POST'])
def expense():
    global Name
    global name12
    if request.method == 'POST':
        # Retrieve form data
        project = request.form['project']

        # Connect to the database
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()

            # Execute SQL query to sum up the amount
            cursor.execute("""SELECT SUM(amount) AS total_amount 
                              FROM Expense 
                              WHERE project = ?""", (project))
            total_amount = cursor.fetchone()[0]
            name12=project
            conn.close()

            # Check if total_amount is not None
            if total_amount is not None:
                # Pass total_amount to the template
                return render_template('expense.html', total_amount=total_amount)
            else:
                return render_template('expense.html', message="No data found for the given criteria")
        else:
            flash('Error connecting to the database. Please try again later.', 'error')

    else:
        return render_template('expense.html', message=None)

@app.route('/get_database_values4', methods=['GET'])
def get_database_values4():
    # Fetch all records from the GatePass table
    global name12
    print(name12)
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT list, amount FROM Expense WHERE project = ?",(name12))
        rows = cursor.fetchall()
        conn.close()

        # Convert the records to a list of dictionaries
        records = []
        for row in rows:
            record = {
                'list': row[1],
                'amount': row[0]
            }
            records.append(record)
        # Return the records as JSON
        return jsonify(records)
    else:
        flash('Error connecting to the database. Please try again later.', 'error')


# Inward GatePass Form route
@app.route('/out', methods=['GET', 'POST'])
def out():
    global Name
    if request.method == 'POST':
        # Retrieve form data

        name = request.form['name']

        details = request.form['details']
        amount = request.form['amount']
        entered_by = request.form['entered_by']

        project = request.form['project']
        # Insert data into the database
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO donation (
                                  name,
                                  details,
                                  amount,
                                  entered_by,
                                  project,
                                  date
                              ) VALUES (?, ?, ?, ?, ?, GETDATE())""",
                           (name,details,amount,f'{entered_by} by {Name}',project))
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            if affected_rows == 0:
                # Pass the message to the template
                return render_template('out.html', message="Data already present")
            else:
                print('Data Saved Successfully :)')
                return render_template('out.html', message="Data saved successfully")
        else:
            flash('Error connecting to the database. Please try again later.', 'error')

    else:
        return render_template('out.html', message=None )
@app.route('/get_database_values3', methods=['GET'])
def get_database_values3():
    # Fetch all records from the GatePass table
    global name1, project1
    print(name1,project1)
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, amount, project FROM donation WHERE name = ? AND project = ?", (name1, project1))
        rows = cursor.fetchall()
        conn.close()

        # Convert the records to a list of dictionaries
        records = []
        for row in rows:
            record = {
                'name': row[1],
                'amount': row[0],
                'project': row[2]
            }
            records.append(record)
        # Return the records as JSON
        return jsonify(records)
    else:
        flash('Error connecting to the database. Please try again later.', 'error')

# Get Database Values route
@app.route('/get_database_values2', methods=['GET'])
def get_database_values2():
    # Fetch all records from the GatePass table
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, amount, project FROM donation")
        rows = cursor.fetchall()
        conn.close()

        # Convert the records to a list of dictionaries
        records = []
        for row in rows:
            record = {
                'name': row[1],
                'amount': row[0],
                'project': row[2]
            }

            records.append(record)
        # Return the records as JSON
        return jsonify(records)
    else:
        flash('Error connecting to the database. Please try again later.', 'error')

# Get Database Values route
@app.route('/get_database_values', methods=['GET'])
def get_database_values():
    # Fetch all records from the GatePass table
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT list, amount, project FROM Expense")
        rows = cursor.fetchall()
        conn.close()

        # Convert the records to a list of dictionaries
        records = []
        for row in rows:
            record = {
                'list': row[1],
                'amount': row[0],
                'project': row[2]
            }

            records.append(record)
        # Return the records as JSON
        return jsonify(records)
    else:
        flash('Error connecting to the database. Please try again later.', 'error')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4055, debug=True)
