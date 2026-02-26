from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


from app_and_db import db


class User(db.Model, UserMixin):
    """
    User class
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    linkedin = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(300), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def __init__(self, name, linkedin, email, password_hash):
        self.name = name
        self.linkedin = linkedin
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return '<User {}>'.format(self.name)


def create_user(name, email, linkedin, password):
    """
    This function adds a new user to the database
    :param name: name
    :param email: email
    :param linkedin: linkedin
    :param password: password
    :return: None
    """
    new_user = User(name=name, email=email, linkedin=linkedin,
                    password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()


def get_user_by_email(email):
    """
    This function finds the user by email
    :param email: email
    :return: None
    """
    return User.query.filter_by(email=email).first()


def check_password(user, password):
    """
    This function checks whether the password is correct
    :param user: user
    :param password: password
    :return: Bool
    """
    return check_password_hash(user.password_hash, password)
