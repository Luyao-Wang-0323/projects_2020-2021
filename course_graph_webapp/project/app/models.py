# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Create an User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    userpsw = db.Column(db.String(128))
    existingskills = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.userpsw = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.userpsw, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Job(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    jobname = db.Column(db.String(100))
    requirement = db.Column(db.String(200))
    

    def __repr__(self):
        return '<Job: {}>'.format(self.jobname)


class Knowledge(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'knowledges'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100))
    prereq = db.Column(db.String(200))
    skills = db.Column(db.String(200))

    def __repr__(self):
        return '<Knowledge: {}>'.format(self.topic)


class Resource(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(100))
    link = db.Column(db.String(200))
    knowledge = db.Column(db.String(128))
    

    def __repr__(self):
        return '<Resource: {}>'.format(self.course)


# class Department(db.Model):
#     """
#     Create a Department table
#     """

#     __tablename__ = 'departments'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(60), unique=True)
#     description = db.Column(db.String(200))
#     employees = db.relationship('Employee', backref='department',
#                                 lazy='dynamic')

#     def __repr__(self):
#         return '<Department: {}>'.format(self.name)


# class Role(db.Model):
#     """
#     Create a Role table
#     """

#     __tablename__ = 'roles'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(60), unique=True)
#     description = db.Column(db.String(200))
#     employees = db.relationship('Employee', backref='role',
#                                 lazy='dynamic')

#     def __repr__(self):
#         return '<Role: {}>'.format(self.name)