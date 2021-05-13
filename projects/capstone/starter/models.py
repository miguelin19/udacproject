from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
# from sqlalchemy.dialects.postgresql import ENUM

db=SQLAlchemy()

database_path = os.environ['DATABASE_URL']

#setup db

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

#Models
#-----------------------------------------------------

class Movie(db.Model):
    __tablename__ = 'Movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120),nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    actors = db.relationship('Casting', back_populates='_movie', cascade="all, delete")

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def info(self):
        return {
            'title' : self.title,
            'release_date' : self.release_date
        }

class Actor(db.Model):
    __tablename__ = 'Actor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Enum('female', 'male', name='gender_enum', create_type=False), nullable=False)
    movies = db.relationship('Casting', back_populates='_actor', cascade="all, delete")

    def insert(self):
        db.session.add(self)
        db.session.commit()
  
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def info(self):
        return {
            'name' : self.name,
            'age' : self.age,
            'gender' : self.gender
        }