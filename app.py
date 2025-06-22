from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory, app
import os
from static.Encrypt_File import encrypt_file
from static.Decrypt_File import decrypt_file
app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration (Adjust as needed)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Root@123'
app.config['MYSQL_DB'] = 'userauth'

mysql = MySQL(app)

# Directories
UPLOAD_DIR = './Uploads'
ENCRYPT_DIR = './Encrypted'
DECRYPT_DIR = './Decrypted'

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ENCRYPT_DIR, exist_ok=True)
os.makedirs(DECRYPT_DIR, exist_ok=True)

# Route for the intro page
@app.route('/intro')
def intro():
    return render_template('intro.html')

# Route for the welcome page
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM Users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user:
            flash('Username already exists!', 'danger')
        else:
            # Hash the password and insert the user into the database
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO Users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()

            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, password_hash FROM Users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to home after login
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

# Route for the home page (user should be logged in)
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Route for the upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle video file upload
        file = request.files['video']
        if file and file.filename.endswith('.mp4'):
            user_id = session['user_id']
            original_file_path = os.path.join(UPLOAD_DIR, file.filename)
            file.save(original_file_path)

            # Encrypt the video
            encrypted_file_path = os.path.join(ENCRYPT_DIR, f'encrypted_{file.filename}')
            encryption_key = encrypt_file(original_file_path, encrypted_file_path)

            # Store details in the database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO Videos (user_id, filename, filepath, encryption_key, encrypted_filepath)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, file.filename, original_file_path, encryption_key, encrypted_file_path))
            mysql.connection.commit()
            cur.close()

            flash('File uploaded and encrypted successfully!', 'success')
            return redirect(url_for('success'))

    return render_template('upload.html')

#Sucess Route 
@app.route('/success', methods=['GET', 'POST'])
def success():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    if request.method == 'POST':
        # Fetch the latest file details from the database
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT encryption_key, encrypted_filepath, filename
            FROM Videos
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        video = cur.fetchone()
        cur.close()

        if video:
            encryption_key, encrypted_file_path, original_filename = video
            decrypted_file_name = f"decrypted_{original_filename}"
            decrypted_file_path = os.path.join(DECRYPT_DIR, decrypted_file_name)

            # Decrypt the file
            decrypt_file(encrypted_file_path, decrypted_file_path, encryption_key)

            flash('File decrypted successfully!', 'success')
            return send_from_directory(DECRYPT_DIR, decrypted_file_name, as_attachment=True)
        else:
            flash('No video found to decrypt!', 'danger')

    return render_template('success.html')


# Route for my account page (just for template)
@app.route('/my_account')
def my_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Fetch username
    cur.execute("SELECT username FROM Users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    username = user[0] if user else 'Unknown User'

    # Fetch video count
    cur.execute("SELECT COUNT(*) FROM Videos WHERE user_id = %s", (user_id,))
    video_count = cur.fetchone()[0]

    # Fetch video details
    cur.execute("SELECT id, filename FROM Videos WHERE user_id = %s", (user_id,))
    videos = cur.fetchall()

    cur.close()

    return render_template('my_account.html', username=username, video_count=video_count, videos=videos)

    


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Route to download the encrypted file
@app.route('/download_encrypted/<filename>')
def download_encrypted(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(ENCRYPT_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(ENCRYPT_DIR, filename, as_attachment=True)
    else:
        flash('File not found!', 'danger')
        return redirect(url_for('my_account'))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    video_id = request.form.get('video_id')
    cur = mysql.connection.cursor()

    # Fetch the filename for the given video ID
    cur.execute("SELECT filename FROM Videos WHERE id = %s", (video_id,))
    video = cur.fetchone()
    cur.close()

    if not video:
        flash('Video not found!', 'danger')
        return redirect(url_for('my_account'))

    encrypted_filename = f'encrypted_{video[0]}'
    encrypted_file_path = os.path.join(ENCRYPT_DIR, encrypted_filename)
    decrypted_filename = f'decrypted_{video[0]}'
    decrypted_file_path = os.path.join(DECRYPT_DIR, decrypted_filename)

    # Automatically fetch the encryption key from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT encryption_key FROM Videos WHERE id = %s", (video_id,))
    key_record = cur.fetchone()
    cur.close()

    if key_record:
        decryption_key = key_record[0]
        decrypt_file(encrypted_file_path, decrypted_file_path, decryption_key)
        return send_from_directory(DECRYPT_DIR, decrypted_filename, as_attachment=True)
    else:
        flash('Decryption key not found!', 'danger')
        return redirect(url_for('my_account'))
    
#Uploads Route 
@app.route('/Uploads/<filename>')
def upload_file(filename):
    return send_from_directory('Uploads', filename)
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
