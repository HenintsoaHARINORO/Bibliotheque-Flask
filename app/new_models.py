from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from datetime import datetime
from dotenv import load_dotenv
import os

#load_dotenv()
# Define database credentials
DATABASE_URL = os.getenv('DATABASE_URL')
# DATABASE_URL = os.environment.get('DATABASE_URL')
#Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# Define SQLAlchemy model for student table
class Student(Base):
    __tablename__ = 'student'
    __table_args__ = {'schema': 'thesis'}
    id = Column(Integer, primary_key=True)
    student_number = Column(String(50), unique=True, nullable=False)
    school = Column(String(100))
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(200), nullable=False)
    searches = relationship('SearchHistory', backref='student', lazy=True)


class SearchHistory(Base):
    __tablename__ = 'search_history'
    __table_args__ = {'schema': 'thesis'}
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    search_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('thesis.student.id'))


class File(Base):
    __tablename__ = 'file'
    __table_args__ = (
        UniqueConstraint('thesis_file_name'),
        {'schema': 'thesis'}
    )
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('thesis.student.id'), nullable=False)
    thesis_file_name = Column(String(255), unique=True)
    thesis_file = Column(LargeBinary)
    correction_file_name = Column(String(255))
    correction_file = Column(LargeBinary)
    upload_date = Column(DateTime, default=func.current_timestamp())
    title = Column(String)
    theme = Column(String)
    author = Column(String)
    date = Column(String)
    university = Column(String)
    ecole = Column(String)
    mention = Column(String)
    status = Column(String)
    cover_image = Column(LargeBinary)
    student = relationship('Student', backref=backref('file', lazy=True))



class Download(Base):
    __tablename__ = 'downloads'
    __table_args__ = {'schema': 'thesis'}
    id = Column(Integer, primary_key=True)
    filename = Column(String, ForeignKey(
        'thesis.file.thesis_file_name'))
    user_id = Column(Integer, ForeignKey('thesis.student.id'))
    download_count = Column(Integer, default=0)
    file = relationship('File', backref='downloads')
    student = relationship('Student')

# Create tables with the updated schema
Base.metadata.create_all(engine)

# Commit changes
session.commit()

# Close session
session.close()

print("Tables created successfully")
