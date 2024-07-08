import base64
import io

import random
import secrets
import smtplib
import ssl
from email.message import EmailMessage

import flask
from openpyxl.utils.protection import hash_password
from psycopg2 import IntegrityError
from sqlalchemy import create_engine, and_, func, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from werkzeug.utils import secure_filename

from app.models import UploadedFile, User
from app.new_models import Student, File, SearchHistory, Download
from script.similarity_search import find_top_filenames
from script.extraction_with_predicted import extract_and_predict
from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SECRET_KEY, SQLALCHEMY_DATABASE_URI, MAIL_SERVER, MAIL_PORT, \
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_USE_TLS, MAIL_USE_SSL

from flask import Flask, render_template, send_file, abort, send_from_directory, url_for, redirect, flash, session

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
# Add these to your Flask app configuration
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME  # Replace with your email
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD  # Replace with your app password
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL

# Connect to the database
engine = create_engine(SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def send_email(to_email, subject, body):
    from_email = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    smtp_server = app.config['MAIL_SERVER']
    smtp_port = app.config['MAIL_PORT']

    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(from_email, password)
        server.send_message(message)


"""def fetch_search_history():
    user_id = request.args.get('user_id')

    search_type = request.args.get('search_type')  # Assuming you also pass search type
    if not user_id or not search_type:
        return jsonify({'error': 'User ID or search type not provided'}), 400
    try:

        search_history = db_session.query(SearchHistory). \
            join(User, User.id == SearchHistory.user_id). \
            filter(User.fullname == user_id, SearchHistory.search_type == search_type). \
            order_by(SearchHistory.timestamp.desc()).limit(5).all()
        print(search_history)
        search_history_json = [
            {'id': item.id, 'query': item.query, 'search_type': item.search_type, 'timestamp': item.timestamp} for item
            in search_history]
        print(search_history_json)
        return jsonify(search_history_json)
    except Exception as e:
        db_session.rollback()  # Roll back the transaction if an error occurs
        return jsonify({'error': str(e)}), 500"""


def fetch_search_history():
    user_id = request.args.get('user_id')
    print(user_id)
    search_type = request.args.get('search_type')

    if not user_id or not search_type:
        return jsonify({'error': 'User ID or search type not provided'}), 400

    try:
        print("start")
        # Assuming db_session is your SQLAlchemy session object
        search_history = db_session.query(SearchHistory). \
            join(Student, Student.id == SearchHistory.user_id). \
            filter(Student.name == user_id, SearchHistory.search_type == search_type). \
            order_by(desc(SearchHistory.timestamp)).limit(5).all()
        print("end")
        search_history_json = [
            {'id': item.id, 'query': item.query, 'search_type': item.search_type, 'timestamp': item.timestamp} for item
            in search_history]

        return jsonify(search_history_json)

    except Exception as e:
        db_session.rollback()  # Roll back the transaction if an error occurs
        return jsonify({'error': str(e)}), 500


def save_search():
    data = request.get_json()
    username = data['user_id']
    search_type = data['search_type']
    search_query = data['search_query']
    if search_query and search_type and username:
        try:
            with db_session as session:  # Ensure session context
                user = session.query(Student).filter_by(name=username).first()
                if not user:
                    return jsonify({'error': 'User not found'}), 404

                user_id = user.id
                print(user_id)
                print(search_query)
                print(search_type)
                search_history = SearchHistory(
                    query=search_query,
                    search_type=search_type,
                    timestamp=datetime.utcnow(),
                    user_id=user_id
                )
                session.add(search_history)
                session.commit()
                print(search_history)
                print("Saved")
                # Commit transaction
            return jsonify({'message': 'Search history saved successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Missing query or search_type parameter'}), 400


def check_login():
    logged_in = session.get('logged_in', False)
    return jsonify({'logged_in': logged_in})


def download_pdf(filename):
    user_id = session.get('user_id')

    file_record = db_session.query(File).filter_by(thesis_file_name=filename).first()
    if not file_record:
        abort(404)  # File not found

    # Check if the file has not been previously downloaded by the user
    if user_id:
        download_record = db_session.query(Download).filter_by(filename=filename, user_id=user_id).first()
        if not download_record:
            print(f"Creating new download record for file {filename} by user {user_id}")
            download_record = Download(filename=filename, user_id=user_id, download_count=1)
            db_session.add(download_record)
        else:
            print(f"User {user_id} has already downloaded file {filename}")
            download_record.download_count += 1
    else:
        download_record = db_session.query(Download).filter_by(filename=filename, user_id=None).first()
        if not download_record:
            print(f"Creating new download record for file {filename} by an anonymous user")
            download_record = Download(filename=filename, download_count=1)
            db_session.add(download_record)
        else:
            print(f"Incrementing download count for file {filename} by an anonymous user")
            download_record.download_count += 1

    db_session.commit()
    print("Download record committed to the database")

    return send_file(io.BytesIO(file_record.file),
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name=filename)


def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Create a new user with hashed password
            new_user = User(fullname=fullname, email=email, password=hashed_password)
            db_session.add(new_user)
            db_session.commit()
            return redirect(url_for('login_route'))
        else:
            return "Passwords do not match", 400
    return render_template('login.html')


from flask import request, jsonify


# updated
def search_theme():
    data = request.json
    print(data)
    search_query = data.get('search_query')

    # Add filter for approved status
    query = db_session.query(File).filter(
        File.theme.ilike(f'%{search_query}%'),
        File.status == 'approved'
    )

    books = query.all()
    book_list = []
    for book in books:
        book_info = {
            'id': book.id,
            'filename': book.thesis_file_name,
            'title': book.title,
            'author': book.author,
            'date': book.date,
            'university': book.university,
            'theme': book.theme,
            'ecole': book.ecole,
            'mention': book.mention,
            'cover_image_base64': base64.b64encode(book.cover_image).decode('utf-8') if book.cover_image else None,
            'download_link': url_for('download_pdf_route', filename=book.thesis_file_name)
        }
        book_list.append(book_info)
    return jsonify(book_list)


def search_mention():
    data = request.json
    search_query = data.get('search_query')

    # Add filter for approved status
    query = db_session.query(File).filter(
        File.mention.ilike(f'%{search_query}%'),
        File.status == 'approved'
    )

    books = query.all()

    # Randomly select 5 books from the fetched list
    random_books = random.sample(books, min(5, len(books)))

    book_list = []
    for book in random_books:
        book_info = {
            'id': book.id,
            'filename': book.thesis_file_name,
            'title': book.title,
            'author': book.author,
            'date': book.date,
            'university': book.university,
            'theme': book.theme,
            'ecole': book.ecole,
            'mention': book.mention,
            'cover_image_base64': base64.b64encode(book.cover_image).decode('utf-8') if book.cover_image else None,
            'download_link': url_for('download_pdf_route', filename=book.thesis_file_name)
        }
        book_list.append(book_info)
    return jsonify(book_list)


def search():
    data = request.json
    search_type = data.get('search_type')
    search_query = data.get('search_query')
    result_list = []
    query = None
    try:
        with DBSession() as session:
            # Execute queries using the session
            if search_type == 'Nom':
                query = session.query(File).filter(File.author.ilike(f'%{search_query}%'), File.status == 'approved')
            elif search_type == 'Titre':
                query = session.query(File).filter(File.title.ilike(f'%{search_query}%'), File.status == 'approved')
            elif search_type == 'Date':
                query = session.query(File).filter(File.date.ilike(f'%{search_query}%'), File.status == 'approved')
            else:
                top_filenames = find_top_filenames(search_query)
                print(top_filenames)
                for filename in top_filenames:
                    # Find the book corresponding to the filename in the database
                    book = session.query(File).filter_by(thesis_file_name=filename, status='approved').first()

                    if book:
                        # Construct result dictionary for the book
                        result_dict = {
                            'id': book.id,
                            'filename': book.thesis_file_name,
                            'title': book.title,
                            'author': book.author,
                            'mention': book.mention,
                            'theme': book.theme,
                            'date': book.date,
                            'university': book.university,
                            'ecole': book.ecole,
                            'cover_image_base64': base64.b64encode(book.cover_image).decode(
                                'utf-8') if book.cover_image else None,
                            'download_link': url_for('download_pdf_route', thesis_file_name=book.thesis_file_name)
                        }
                        result_list.append(result_dict)
                        print(result_list)
            if query:
                results = query.all()

                for result in results:
                    result_dict = {
                        'id': result.id,
                        'filename': result.thesis_file_name,
                        'title': result.title,
                        'author': result.author,
                        'mention': result.mention,
                        'date': result.date,
                        'theme': result.theme,
                        'university': result.university,
                        'ecole': result.ecole,
                        'cover_image_base64': base64.b64encode(result.cover_image).decode(
                            'utf-8') if result.cover_image else None,
                        'download_link': url_for('download_pdf_route', filename=result.thesis_file_name)
                    }
                    result_list.append(result_dict)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    user_id = flask.session.get('user_id')
    downloaded_files = []
    if user_id:
        try:
            with DBSession() as session:
                downloaded_files = session.query(Download).filter_by(user_id=user_id).all()
                downloaded_files = [download.filename for download in downloaded_files]
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    print(result_list)
    if not result_list:
        return jsonify(result_list=[], downloaded_files=downloaded_files)
    else:
        return jsonify(result_list=result_list, downloaded_files=downloaded_files)


def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db_session.query(User).filter_by(email=email).first()
        print("User:", user)
        print("Password Hash (Database):", user.password)
        print("Password (Input):", password)
        all_books = db_session.query(UploadedFile).all()

        for book in all_books:
            # Process each book as before
            book.cover_image_base64 = base64.b64encode(book.cover_image).decode('utf-8') if book.cover_image else None
            book.download_link = url_for('download_pdf_route', filename=book.filename)
            # Get the associated Download object and retrieve the download count
            download_count = db_session.query(func.sum(Download.download_count)).filter_by(
                filename=book.filename).scalar()
            book.download_count = download_count if download_count else 0
            print(f"Title: {book.title}, Download Count: {book.download_count}")

        # Sort the books based on download count in descending order
        sorted_books = sorted(all_books, key=lambda x: x.download_count, reverse=True)
        # Select the top 5 books
        top_5_books = sorted_books[:5]
        logged_in = session.get('logged_in', False)
        username = session.get('username', None)

        if user and check_password_hash(user.password, password):
            print("here 2")
            session['user_id'] = user.id
            print("here")
            session['logged_in'] = True
            session['username'] = user.fullname
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for('index_route', username=user.fullname))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    else:
        # Handling the GET request to ensure top_5_books, logged_in, and username are defined
        all_books = db_session.query(UploadedFile).all()

        for book in all_books:
            # Process each book as before
            book.cover_image_base64 = base64.b64encode(book.cover_image).decode('utf-8') if book.cover_image else None
            book.download_link = url_for('download_pdf_route', filename=book.filename)
            # Get the associated Download object and retrieve the download count
            download_count = db_session.query(func.sum(Download.download_count)).filter_by(
                filename=book.filename).scalar()
            book.download_count = download_count if download_count else 0
            print(f"Title: {book.title}, Download Count: {book.download_count}")

        # Sort the books based on download count in descending order
        sorted_books = sorted(all_books, key=lambda x: x.download_count, reverse=True)
        # Select the top 5 books
        top_5_books = sorted_books[:5]
        logged_in = session.get('logged_in', False)
        username = session.get('username', None)

    return render_template('login.html', books=top_5_books, logged_in=logged_in, username=username)


def remove_history():
    data = request.json
    fullname = data.get('user_id')
    query = data.get('query')
    search_type = data.get('search_type')

    try:
        # Fetch the user based on fullname
        user = db_session.query(Student).filter(Student.name == fullname).first()
        print(user)
        if not user:
            return jsonify(success=False, message="User not found"), 404

        # Find the corresponding history item to delete
        history_item = db_session.query(SearchHistory).filter(
            SearchHistory.user_id == user.id,
            SearchHistory.query == query,
            SearchHistory.search_type == search_type
        ).first()

        if history_item:
            db_session.delete(history_item)
            db_session.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False, message="History item not found"), 404

    except Exception as e:
        db_session.rollback()
        return jsonify(success=False, message=str(e)), 500


def logout():
    # Clear the session and log the user out
    session.pop('logged_in', None)
    return redirect(url_for('index_route'))


def profile():
    logged_in = session.get('logged_in', False)
    username = session.get('username')  # Ensure the username is stored in the session
    print(username)
    return render_template('index.html', logged_in=logged_in, username=username)


def start():
    return render_template('start.html')


def dashboard():
    if not session.get('logged_in') or not session.get('student_number'):
        return redirect(url_for('login2_route'))
    student_number = session.get('student_number')

    # Query the Student table to get the student's name
    student = DBSession().query(Student).filter_by(student_number=student_number).first()
    username = student.name
    logged_in = True
    files = DBSession().query(File).all()
    return render_template('dashboard.html', files=files, username=username, logged_in=logged_in)


def fetch_files(status):
    try:
        # Create a new session
        session = DBSession()

        # Query the database for files with the given status
        files = session.query(File).filter_by(status=status).all()
        print(len(files))
        print(status)
        if files:
            # Return a JSON response with the file data
            file_data = []
            for file in files:
                file_dict = {
                    'id': file.id,
                    'student_name': file.student.name,
                }
                if file.correction_file:
                    file_dict['correction_file'] = url_for('download_file_dashboard_route', file_id=file.id,
                                                           file_type='correction')
                if file.thesis_file:
                    file_dict['thesis_file'] = url_for('download_file_dashboard_route', file_id=file.id,
                                                       file_type='thesis')
                file_data.append(file_dict)
            return jsonify({'files': file_data})
        else:
            return jsonify({'error': 'File not found'}), 404

    except Exception as e:
        # Roll back the session in case of an error
        session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        # Close the session
        session.close()


def accept_file(file_id):
    db_session = DBSession()
    try:
        file = db_session.query(File).filter_by(id=file_id).first()
        if file:
            file.status = 'approved'
            db_session.commit()
            student = file.student
            email = student.email
            name = student.name  # Assuming you have the user's name

            # Send email to the user
            subject = "Statut votre demande de publication de livre sur Hai-karoka"
            body = f"Bonjour {name},\n\n" \
                   f"Votre demande de publication pour le livre '{file.thesis_file_name}' a été approuvé sur Hai-karoka.\n\n" \
                   "Cordialement,\nL'équipe Hai-karoka"
            try:
                send_email(email, subject, body)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
                return jsonify(message='Erreur lors de l\'envoi de l\'email. Veuillez réessayer.', popup=True), 500

            return redirect(url_for('dashboard_route'))
    except Exception as e:
        db_session.rollback()
        # Handle error, perhaps return a JSON response with the error message
    finally:
        db_session.close()


def reject_file(file_id):
    db_session = DBSession()
    try:
        file = db_session.query(File).filter_by(id=file_id).first()
        if file:
            file.status = 'refused'
            db_session.commit()
            student = file.student
            email = student.email
            name = student.name  # Assuming you have the user's name

            # Send email to the user
            subject = "Statut votre demande de publication de livre sur Hai-karoka"
            body = f"Bonjour {name},\n\n" \
                   f"Votre demande de publication pour le livre '{file.thesis_file_name}' a été refusé sur Hai-karoka.\n\n" \
                   "Cordialement,\nL'équipe Haikaroka"
            try:
                send_email(email, subject, body)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
                return jsonify(message='Erreur lors de l\'envoi de l\'email. Veuillez réessayer.', popup=True), 500

            return redirect(url_for('dashboard_route'))
    except Exception as e:
        db_session.rollback()
        # Handle error, perhaps return a JSON response with the error message
    finally:
        db_session.close()


def download_file_dashboard(file_id):
    db_session = DBSession()

    try:
        file_type = request.args.get('file_type')
        file = db_session.query(File).get(file_id)
        if file:
            if file_type == 'correction' and file.correction_file:
                return send_file(io.BytesIO(file.correction_file), mimetype='application/pdf')
            elif file_type == 'thesis' and file.thesis_file:
                return send_file(io.BytesIO(file.thesis_file), mimetype='application/pdf')
            else:
                return jsonify({'error': 'No file found'}), 404
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()


def login2():
    if request.method == 'POST':
        student_number = request.form['etudiant']
        password = request.form['password']
        try:
            db_session = DBSession()
            existing_student = db_session.query(Student).filter_by(student_number=student_number).first()
            print(existing_student)
            if existing_student:
                if check_password_hash(existing_student.password, password):
                    print("True")
                    session['logged_in'] = True
                    session['student_number'] = existing_student.student_number
                    print(session['student_number'])
                    if 'student_number' in session and session['student_number'] == 'admin':
                        session['logged_in'] = True
                        session['student_number'] = existing_student.student_number
                        return redirect('/dashboard')
                    else:
                        return redirect(url_for('index_route'))
                else:
                    flash('Mot de passe invalide. Veuillez réessayer.', 'error')
            else:
                flash('Numéro étudiant invalide. Veuillez réessayer.', 'error')
        except Exception as e:
            flash('Une erreur est survenue lors de la connexion. Veuillez réessayer.', 'error')
            print(e)

    return render_template('login_new.html')


def login22():
    if session.get('logged_in'):
        return redirect(url_for('dashboard_route' if session['student_number'] == 'admin' else 'index_route'))
    return render_template('login_new.html')


def signup2():
    if request.method == 'POST':
        student_number = request.form['N']
        school = request.form['ecole']
        name = request.form['nom']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirm_password']
        try:
            db_session = DBSession()
            if password != confirmpassword:
                flash('Passwords do not match. Please try again.', 'error')
                return render_template('login_new.html')

            # Check if student_number already exists
            existing_student = db_session.query(Student).filter_by(student_number=student_number).first()
            if existing_student:
                flash('User with this student number already exists. Please use a login.', 'error')
                return render_template('login_new.html')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

            # Save new student to the database
            new_student = Student(student_number=student_number, school=school, name=name, email=email,
                                  password=hashed_password)
            db_session.add(new_student)
            db_session.commit()

            flash('Signup successful. Please login.', 'success')
            return redirect(url_for('login2_route'))

        except Exception as e:
            print(f'Error during signup: {str(e)}')
            flash('Error during signup. Please try again later.', 'error')
            return render_template('login_new.html')
    return render_template('login_new.html')


def index():
    if 'logged_in' in session:
        type_name = 'Environnement et Ressources Naturelles'
        books_types = db_session.query(File).filter(File.theme == type_name, File.status == 'approved').limit(6).all()
        username = session.get('student_number')
        print(username)
        user_info = None
        if username:
            user_info = db_session.query(Student).filter_by(student_number=username).first()
            print(user_info)
        # Load all books if no search query is provided
        all_books = db_session.query(File).filter(File.status == 'approved').all()

        for book in all_books:
            # Process each book as before
            book.cover_image_base64 = base64.b64encode(book.cover_image).decode('utf-8') if book.cover_image else None
            book.download_link = url_for('download_pdf_route', filename=book.thesis_file_name)
            # Get the associated Download object and retrieve the download count
            download_count = db_session.query(func.sum(Download.download_count)).filter_by(
                filename=book.thesis_file_name).scalar()
            book.download_count = download_count if download_count else 0
            print(f"Title: {book.title}, Download Count: {book.download_count}")

        # Sort the books based on download count in descending order
        sorted_books = sorted(all_books, key=lambda x: x.download_count, reverse=True)
        # Select the top 5 books
        top_5_books = sorted_books[:5]
        print(top_5_books)
        logged_in = session.get('logged_in', False)
        username = user_info.name  # Get the username from the session if logged in

        user_id = user_info.id
        print(user_id)
        downloaded_files = []
        if user_id:
            downloaded_files = db_session.query(Download).filter_by(user_id=user_id).all()
            downloaded_files = [download.filename for download in downloaded_files]
        print("Index")
        return render_template('index.html', books=top_5_books, books_types=books_types, logged_in=logged_in,
                               username=username,
                               downloaded_files=downloaded_files, user_info=user_info)
    else:
        print("Not logged in")
        return redirect(url_for('login2_route'))


COVER_IMAGE_FOLDER = 'images'


def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


import os
import fitz  # PyMuPDF

# Assuming pdf_folder and image_folder are already defined
pdf_folder = 'uploads'  # Specify the folder where PDFs are uploaded
image_folder = 'images'  # Specify the folder where images will be saved


def submit_student_info():
    session = None  # Initialize session here
    try:
        student_number = request.form.get('student_number')
        school = request.form.get('school')
        name = request.form.get('name')
        email = request.form.get('email')

        session = DBSession()

        # Check if student_number already exists
        existing_student = session.query(Student).filter_by(student_number=student_number).first()
        if existing_student:
            # Student already exists, continue with file upload
            memoir_files = request.files.get('memoir_files')
            correction_attestation = request.files.get('correction_attestation')

            if memoir_files and correction_attestation:
                max_file_size = 30 * 1024 * 1024  # 10MB limit (adjust as needed)
                if memoir_files.content_length > max_file_size or correction_attestation.content_length > max_file_size:
                    return jsonify({'error': 'File size exceeded the maximum limit'}), 413

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], memoir_files.filename)
                existing_file = session.query(File).filter(
                    File.thesis_file_name == memoir_files.filename).first()

                if existing_file:
                    return jsonify(message='Le fichier existe déjà', popup=True), 409

                memoir_files.save(file_path)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], memoir_files.filename)
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)  # Load the first page only
                pix = page.get_pixmap()
                image_name = os.path.splitext(memoir_files.filename)[0] + ".png"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
                pix.save(image_path)
                doc.close()

                # Extract text and other metadata from the PDF
                extracted_data = extract_and_predict(file_path)
                with open(image_path, 'rb') as img_file:
                    cover_image_data_memoire = img_file.read()
                with open(file_path, 'rb') as pdf_file:
                    pdf_content_memoire = pdf_file.read()

                correction_file_data = correction_attestation.read()

                memoir_file_name = memoir_files.filename
                correction_file_name = correction_attestation.filename

                file_record = File(
                    student_id=existing_student.id,  # Use existing student's ID
                    title=extracted_data.get('title'),
                    author=extracted_data.get('name'),
                    mention=extracted_data.get('mapped_classes'),
                    theme=extracted_data.get('theme'),
                    date=extracted_data.get('date'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    thesis_file_name=memoir_file_name,
                    thesis_file=pdf_content_memoire,
                    correction_file_name=correction_file_name,
                    correction_file=correction_file_data,  # Add this line
                    cover_image=cover_image_data_memoire,
                    status="pending"
                )
                session.add(file_record)
                session.commit()  # Commit the file record
                # Remove the uploaded PDF file and cover image file
                os.remove(file_path)
                os.remove(image_path)

                return jsonify(
                    message='File successfully uploaded',
                    date=extracted_data.get('date'),
                    title=extracted_data.get('title'),
                    theme=extracted_data.get('theme'),
                    name=extracted_data.get('name'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    mention=extracted_data.get('mapped_classes')
                ), 200
            else:
                return jsonify({'error': 'Both memoir files and correction attestation are required'}), 400

        else:
            new_password = secrets.token_urlsafe(12)
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)

            # Student does not exist, create new student and upload files
            new_student = Student(student_number=student_number, school=school, name=name, email=email,
                                  password=hashed_password)
            session.add(new_student)
            session.commit()  # Commit the student first to get the student ID
            subject = "Vos identifiants de compte Haikaroka"
            body = f"Bonjour {name},\n\n" \
                   f"Depuis que vous avez téléchargé votre mémoire sur Haikaroka, vous êtes maintenant membre.\n" \
                   f"Voici vos identifiants :\n\n" \
                   f"Numéro d'étudiant : {student_number}\nMot de passe : {new_password}\n\n" \
                   "Cordialement,\nL'équipe Haikaroka"
            try:
                send_email(email, subject, body)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email: {e}")
                return jsonify(message='Erreur lors de l\'envoi de l\'email. Veuillez réessayer.', popup=True), 500

            memoir_files = request.files.get('memoir_files')
            correction_attestation = request.files.get('correction_attestation')

            if memoir_files and correction_attestation:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], memoir_files.filename)
                existing_file = session.query(File).filter(
                    File.thesis_file_name == memoir_files.filename).first()

                if existing_file:
                    return jsonify(message='Le fichier existe déjà', popup=True), 409

                memoir_files.save(file_path)
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], memoir_files.filename)
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)  # Load the first page only
                pix = page.get_pixmap()
                image_name = os.path.splitext(memoir_files.filename)[0] + ".png"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
                pix.save(image_path)
                doc.close()

                # Extract text and other metadata from the PDF
                extracted_data = extract_and_predict(file_path)
                with open(image_path, 'rb') as img_file:
                    cover_image_data_memoire = img_file.read()
                with open(file_path, 'rb') as pdf_file:
                    pdf_content_memoire = pdf_file.read()

                correction_file_data = correction_attestation.read()

                memoir_file_name = memoir_files.filename
                correction_file_name = correction_attestation.filename

                file_record = File(
                    student_id=new_student.id,  # Use new student's ID
                    title=extracted_data.get('title'),
                    author=extracted_data.get('name'),
                    mention=extracted_data.get('mapped_classes'),
                    theme=extracted_data.get('theme'),
                    date=extracted_data.get('date'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    thesis_file_name=memoir_file_name,
                    thesis_file=pdf_content_memoire,
                    correction_file_name=correction_file_name,
                    correction_file=correction_file_data,  # Add this line
                    cover_image=cover_image_data_memoire,
                    status="pending"
                )
                session.add(file_record)
                session.commit()  # Commit the file record
                # Remove the uploaded PDF file and cover image file
                os.remove(file_path)
                os.remove(image_path)

                return jsonify(
                    message='File successfully uploaded',
                    date=extracted_data.get('date'),
                    title=extracted_data.get('title'),
                    theme=extracted_data.get('theme'),
                    name=extracted_data.get('name'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    mention=extracted_data.get('mapped_classes')
                ), 200
            else:
                return jsonify({'error': 'Both memoir files and correction attestation are required'}), 400

    except IntegrityError as e:
        if session:
            session.rollback()
        return jsonify(
            {'error': 'Integrity Error: Duplicate student number or other database constraint violated'}), 400

    except Exception as e:
        if session:
            session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if session:
            session.close()


def upload_file():
    try:
        file = request.files['file']
        username = request.form.get('username')
        if file and username:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            user = db_session.query(User).filter(User.fullname == username).first()
            existing_file = db_session.query(UploadedFile).filter(
                and_(UploadedFile.filename == filename, UploadedFile.uploader_id == user.id)).first()

            if existing_file:
                return jsonify(message='Le fichier existe déjà', popup=True), 409

            file.save(file_path)

            print("Saved")
            # Extract first page of the PDF and save as image
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)  # Load the first page only
            pix = page.get_pixmap()
            image_name = os.path.splitext(filename)[0] + ".png"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            pix.save(image_path)
            doc.close()

            # Extract text and other metadata from the PDF
            extracted_data = extract_and_predict(file_path)
            print(extracted_data)
            # Read the cover image as binary data
            with open(image_path, 'rb') as img_file:
                cover_image_data = img_file.read()
            with open(file_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            # Query the user based on the provided username
            user = db_session.query(User).filter(User.fullname == username).first()
            if user:
                # Save data to the database, including the cover image as binary data
                new_file = UploadedFile(
                    filename=filename,
                    title=extracted_data.get('title'),
                    author=extracted_data.get('name'),
                    mention=extracted_data.get('mapped_classes'),
                    theme=extracted_data.get('theme'),
                    date=extracted_data.get('date'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    uploader_id=user.id,  # Assign the uploader_id
                    file=pdf_content,  # Save the file content as binary
                    cover_image=cover_image_data  # Save the cover image as binary data
                )
                db_session.add(new_file)
                db_session.commit()

                # Remove the uploaded PDF file and cover image file
                os.remove(file_path)
                os.remove(image_path)

                return jsonify(
                    message='File successfully uploaded',
                    date=extracted_data.get('date'),
                    title=extracted_data.get('title'),
                    theme=extracted_data.get('theme'),
                    name=extracted_data.get('name'),
                    university=extracted_data.get('university'),
                    ecole=extracted_data.get('ecole'),
                    mention=extracted_data.get('mapped_classes')
                ), 200
            else:
                return jsonify(message='User not found'), 404

    except Exception as e:
        # Handle exceptions
        db_session.rollback()  # Rollback the transaction
        error_message = "An error occurred while uploading the file."
        return jsonify(message=error_message, popup=True), 500


def save_file_data():
    data = request.json
    filename = data['filename']
    title = data['title']
    author = data['author']
    mention = data['mention']
    theme = data['theme']
    date = data['date']
    university = data['university']
    ecole = data['ecole']

    # Find the corresponding file by filename
    file_record = db_session.query(UploadedFile).filter_by(filename=filename).first()
    if file_record:
        # Update the record with the form data
        file_record.title = title
        file_record.author = author
        file_record.mention = mention
        file_record.date = date
        file_record.theme = theme
        file_record.university = university
        file_record.ecole = ecole
        db_session.commit()

        return jsonify(
            message='File data successfully saved',
            class_name='success'  # Class for styling
        ), 200
    else:
        # Return error message with error class for styling
        return jsonify(
            message='File not found',
            class_name='error'  # Class for styling
        ), 404


def save_file_data_2():
    data = request.json
    filename = data['filename']
    title = data['title']
    author = data['author']
    mention = data['mention']
    theme = data['theme']
    date = data['date']
    university = data['university']
    ecole = data['ecole']

    # Find the corresponding file by filename
    file_record = db_session.query(File).filter_by(thesis_file_name=filename).first()
    if file_record:
        # Update the record with the form data
        file_record.title = title
        file_record.author = author
        file_record.mention = mention
        file_record.date = date
        file_record.theme = theme
        file_record.university = university
        file_record.ecole = ecole
        db_session.commit()

        return jsonify(
            message='File data successfully saved',
            class_name='success'  # Class for styling
        ), 200
    else:
        # Return error message with error class for styling
        return jsonify(
            message='File not found',
            class_name='error'  # Class for styling
        ), 404
