from flask import Flask, request, redirect, url_for, render_template, flash, session
import pyodbc
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

def get_db_connection():
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=YOUSSEF-ATEF\SQLEXPRESS;'
        'DATABASE=HMS;'
        'Trusted_Connection=yes;'
    )
    conn = pyodbc.connect(connection_string)
    return conn

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    gender = request.form.get('gender')
    email = request.form.get('email')
    contact = request.form.get('contact')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    if password != cpassword:
        return 'Passwords do not match!'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (first_name, last_name, gender, email, contact, password, role, specialization) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (first_name, last_name, gender, email, contact, password, 'Patient', ''))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

@app.route('/login_doctor', methods=['POST'])
def login_doctor():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ? AND role = ?', (email, password, 'Doctor'))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user[0]  # Assuming the first column is the user ID
        session['role'] = user[7]
        return redirect(url_for('doctor'))  # Replace with actual doctor dashboard route
    else:
        return render_template('index.html', error_message_doctor='Wrong Email/Password')

@app.route('/login_admin', methods=['POST'])
def login_admin():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ? AND role = ?', (email, password, 'Admin'))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['role'] = user[7]
        return redirect(url_for('admin'))  # Replace with actual admin dashboard route
    else:
        return render_template('index.html', error_message_admin='Wrong Email/Password')

@app.route('/admin-panel1.html')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DoctorList")
    doctors = cursor.fetchall()

    cursor.execute("PatientList")
    patients = cursor.fetchall()

    cursor.execute("AppointmentDetails")
    appointments = cursor.fetchall()

    cursor.execute("PrescriptionList")
    prescriptions = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin-panel1.html', doctors=doctors, patients=patients, appointments=appointments, prescriptions=prescriptions)

@app.route('/delete-doctor', methods=['POST'])
def delete_doctor():
    email = request.form['demail']

    if not email:
        flash('Email is required!')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM Users WHERE email = ? AND role = ?', (email, 'Doctor'))
        conn.commit()

        if cursor.rowcount == 0:
            flash('No doctor found with that email address.')
        else:
            flash('Doctor deleted successfully.')

    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}')

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin'))

@app.route('/admin-panel1.html', methods=['POST'])
def add_doctor():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    gender = request.form.get('gender')
    email = request.form.get('email')
    contact = request.form.get('contact')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    specialization = request.form.get('specialization')

    if password != confirm_password:
        return 'Passwords do not match!'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Users (first_name, last_name, gender, email, contact, password, role, specialization) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (first_name, last_name, gender, email, contact, password, 'Doctor', specialization))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE email = ? AND password = ? AND role = ?', (email, password, 'Patient'))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user[0]  # Assuming the first column is the user ID
        session['role'] = user[7]
        return redirect(url_for('patient'))  # Redirect to the patient panel
    else:
        flash('Invalid email or password', 'error')
        return redirect(url_for('index1'))  # Redirect back to login page

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/index1.html')
def index1():
    return render_template('index1.html')

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['txtName']
            email = request.form['txtEmail']
            phone = request.form['txtPhone']
            message = request.form['txtMsg']
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """
            INSERT INTO ContactMessages (name, Contact, email, message, date)
            VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(query, (name, phone, email, message, date))
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending your message: {e}', 'danger')
            print(e)
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')


@app.route('/services.html')
def services():
    return render_template('services.html')

@app.route('/doctor-panel.html')
def doctor():
    doctor_id = session['user_id']   # Replace this with the actual doctor ID from the session
    Role = session['role']
    if doctor_id and Role == 'Doctor':
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('EXEC AppointmentDetailsFromDoctor ?',doctor_id)
        app_list = cursor.fetchall()

        cursor.execute("SELECT concat(first_name , ' ' , last_name) FROM USERS WHERE user_id = ?" , doctor_id)
        username = cursor.fetchone()

        cursor.execute('EXEC PrescriptionsDetailsFromDoctor ?',doctor_id)
        pr_list = cursor.fetchall()
    
        
        
        conn.close()
        return render_template('doctor-panel.html', app_list=app_list, username=username, pr_list=pr_list )
    else:
        return redirect(url_for('index'))
@app.route('/prescribe.html')
def prescribe():
    doctor_id = session['user_id']   # Replace this with the actual doctor ID from the session
    Role = session['role']
    if doctor_id and Role == 'Doctor':
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT concat(first_name , ' ' , last_name) FROM USERS WHERE user_id = ?" , doctor_id)
        username = cursor.fetchone()

        
        cursor.close()
        conn.close()
    else:
       return redirect(url_for('index1')) 
    return render_template('prescribe.html' , username=username)
    
@app.route('/patient-panel.html')
def patient():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    patientId = session['user_id']
    Role = session['role']
    if patientId and Role == 'Patient':
        cursor.execute("EXEC AppointmentHistoryForSpecificPatient ?", patientId)
        appointments = cursor.fetchall() 

        cursor.execute("EXEC ViewPrescriptionForSpecificPatient ?", patientId)
        prescription = cursor.fetchall()

        cursor.execute("SELECT concat(first_name , ' ' , last_name) FROM USERS WHERE user_id = ?" , patientId)
        username = cursor.fetchone()

        cursor.execute("SELECT DISTINCT specialization FROM USERS WHERE specialization != ''")
        spec = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template('patient-panel.html', appointments=appointments , prescription=prescription , username=username , spec=spec)
    else:
        cursor.close()
        conn.close()

        return redirect(url_for('index1'))
    
@app.route('/select-doctor' , methods=['post'])
def select_doctor():
    conn = get_db_connection()
    cursor = conn.cursor()
    patientId = session['user_id']
    Role = session['role']
    if patientId and Role == 'Patient':
        SelectedSpec = request.form['SelectSpecilization']
        cursor.execute("SELECT concat(first_name , ' ' , last_name) AS DocName FROM USERS WHERE specialization = ? AND role = ? " , (SelectedSpec, 'Doctor'))
        doctorList = cursor.fetchall()

        cursor.close()
        conn.close()
    return redirect(url_for('patient',doctorList=doctorList))


@app.route('/logout.html')
def logout():
    session['user_id'] =  0
    session['role'] = ''
    return render_template('logout.html')

@app.route('/logout1.html')
def logout1():
    session['user_id'] =  0
    session['role'] = ''
    return render_template('logout1.html')

if __name__ == '__main__':
    app.run(debug=True)
