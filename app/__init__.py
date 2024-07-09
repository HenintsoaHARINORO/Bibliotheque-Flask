from flask import Flask
from app.controller import *
from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SECRET_KEY

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Define routes
app.add_url_rule('/search_history', view_func=fetch_search_history, methods=['GET'])
app.add_url_rule('/fetch_files/<status>', view_func=fetch_files, methods=['GET'])
app.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
app.add_url_rule('/reject_file/<int:file_id>', view_func=reject_file, methods=['GET'])
app.add_url_rule('/accept_file/<int:file_id>', view_func=accept_file, methods=['GET'])
app.add_url_rule('/download_file_dashboard/<int:file_id>', view_func=download_file_dashboard, methods=['GET'])
app.add_url_rule('/check_login', view_func=check_login, methods=['GET'])
app.add_url_rule('/save_search', view_func=save_search, methods=['POST'])
app.add_url_rule('/remove_history', view_func=remove_history, methods=['POST'])
app.add_url_rule('/download/<filename>', view_func=download_pdf, methods=['GET'])
app.add_url_rule('/<filename>', view_func=serve_image, methods=['GET'])
app.add_url_rule('/upload', view_func=upload_file, methods=['POST'])
app.add_url_rule('/signup', view_func=signup, methods=['GET', 'POST'])
app.add_url_rule('/search_theme', view_func=search_theme, methods=['POST'])
app.add_url_rule('/search_mention', view_func=search_mention, methods=['POST'])
app.add_url_rule('/signup2', view_func=signup2, methods=['POST'])
app.add_url_rule('/login2', view_func=login2, methods=['GET', 'POST'])
app.add_url_rule('/save', view_func=save_file_data, methods=['POST'])
app.add_url_rule('/save2', view_func=save_file_data_2, methods=['POST'])
app.add_url_rule('/search', view_func=search, methods=['POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout, methods=['GET'])
app.add_url_rule('/submit_student_info', view_func=submit_student_info, methods=['POST'])
app.add_url_rule('/profile', view_func=profile, methods=['GET'])
app.add_url_rule('/index', view_func=index, methods=['GET', 'POST'])
app.add_url_rule('/', view_func=start, methods=['GET', 'POST'])
app.add_url_rule('/login22', view_func=login22, methods=['GET'])

# Import other necessary modules and register blueprints if any
