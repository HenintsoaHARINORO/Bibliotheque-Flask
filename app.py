# app.py
from flask import Flask

from app.controller import *
from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SECRET_KEY
from app.controller import submit_student_info, save_file_data_2

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


@app.route('/search_history', methods=['GET'])
def fetch_search_history_route():
    return fetch_search_history()

@app.route('/fetch_files/<status>')
def fetch_files_route(status):
    return fetch_files(status)

@app.route('/dashboard')
def dashboard_route():
    return dashboard()
@app.route('/reject_file/<int:file_id>', methods=['GET'])
def reject_file_route(file_id):
    return reject_file(file_id)
@app.route('/accept_file/<int:file_id>', methods=['GET'])
def accept_file_route(file_id):
    return accept_file(file_id)
@app.route('/download_file_dashboard/<int:file_id>')
def download_file_dashboard_route(file_id):
    return download_file_dashboard(file_id)
@app.route('/check_login')
def check_login_route():
    return check_login()


@app.route('/save_search', methods=['POST'])
def save_search_route():
    return save_search()


@app.route('/remove_history', methods=['POST'])
def remove_history_route():
    return remove_history()


@app.route('/download/<filename>')
def download_pdf_route(filename):
    return download_pdf(filename)


@app.route('/<filename>')
def serve_image_route(filename):
    return serve_image(filename)


""" 
@app.route('/upload', methods=['POST'])
def upload_file_route():
    return upload_file()


@app.route('/signup', methods=['GET', 'POST'])
def signup_route():
    return signup()"""


@app.route('/search_theme', methods=['POST'])
def search_theme_route():
    return search_theme()


@app.route('/search_mention', methods=['POST'])
def search_mention_route():
    return search_mention()


@app.route('/signup2', methods=['POST'])
def signup2_route():
    return signup2()


@app.route('/login2', methods=['GET', 'POST'])
def login2_route():
    return login2()

"""
@app.route('/save', methods=['POST'])
def save_file_data_route():
    return save_file_data()"""


@app.route('/save2', methods=['POST'])
def save_file_data_2_route():
    return save_file_data_2()


@app.route('/search', methods=['POST'])
def search_route():
    return search()

"""
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    return login()"""


@app.route('/logout')
def logout_route():
    return logout()


@app.route('/submit_student_info', methods=['POST'])
def submit_student_info_route():
    return submit_student_info()


@app.route('/profile')
def profile_route():
    return profile()


@app.route('/index', methods=['GET', 'POST'])
def index_route():
    return index()


@app.route('/', methods=['GET', 'POST'])
def start_route():
    return start()


@app.route('/login22')
def login22_route():
    return login22()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5100)
