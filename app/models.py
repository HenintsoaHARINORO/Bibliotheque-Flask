from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define database credentials
DATABASE_URL = "postgresql://postgres:ADMIN123@localhost:5432/postgres"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# Define SQLAlchemy model for uploaded_files table
class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    __table_args__ = {'schema': 'books'}
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False, unique=True)
    title = Column(String)
    theme = Column(String)
    author = Column(String)
    date = Column(String)
    university = Column(String)
    ecole = Column(String)
    mention = Column(String)
    file = Column(LargeBinary, nullable=False)
    cover_image = Column(LargeBinary)
    uploader_id = Column(Integer, ForeignKey('books.users.id'))  # Foreign key to users table
    uploader = relationship('User', back_populates='uploads')  # Relationship definition
    downloads = relationship('Download', back_populates='file')  # Relationship definition


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'books'}
    id = Column(Integer, primary_key=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    uploads = relationship('UploadedFile', back_populates='uploader')  # Relationship definition
    searches = relationship('SearchHistory', back_populates='user')

    def __repr__(self):
        return f'<User {self.email}>'


class SearchHistory(Base):
    __tablename__ = 'search_history'
    __table_args__ = {'schema': 'books'}
    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    search_type = Column(String, nullable=False)  # Value, Tout, Nom, Titre, Date
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('books.users.id'))  # Foreign key to users table
    user = relationship('User', back_populates='searches')


# Define SQLAlchemy model for downloads table
class Download(Base):
    __tablename__ = 'downloads'
    __table_args__ = {'schema': 'books'}
    id = Column(Integer, primary_key=True)
    filename = Column(String, ForeignKey('books.uploaded_files.filename'))
    user_id = Column(Integer, ForeignKey('books.users.id'))  # Foreign key to users table
    download_count = Column(Integer, default=0)
    file = relationship('UploadedFile', back_populates='downloads')
    user = relationship('User')  # Relationship to User for tracking who downloaded the file


# Create tables with the updated schema
Base.metadata.create_all(engine)

# Commit changes
session.commit()

# Close session
session.close()

print("Tables created successfully")
