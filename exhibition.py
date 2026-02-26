from app_and_db import db


class Exhibition(db.Model):
    """
    Exhibition class
    """
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(300), nullable=False)  # planned / ongoing / finished

    def __init__(self, name, organizer_id, location, description, status):
        self.name = name
        self.organizer_id = organizer_id
        self.location = location
        self.description = description
        self.status = status

    def __repr__(self):
        return '<Exhibition {}>'.format(self.name)


class ExhibitionUser(db.Model):
    """
    ExhibitionUser class that helps to contain user information that depends on the exhibition
    """
    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_goals = db.Column(db.String(300), nullable=False)
    exhibition_name = db.Column(db.String(300), nullable=False)

    def __init__(self, exhibition_id, user_id, user_goals, exhibition_name):
        self.exhibition_id = exhibition_id
        self.user_id = user_id
        self.user_goals = user_goals
        self.exhibition_name = exhibition_name

    def __repr__(self):
        return '<ExhibitionUser {}>'.format(self.exhibition_name)


def create_exhibition(name, organizer_id, location, description):
    """
    This function adds a new exhibition to the database
    :param name: name
    :param organizer_id: organizer_id
    :param location: location
    :param description: description
    :return: None
    """
    new_exhibition = Exhibition(name=name, organizer_id=organizer_id, location=location, description=description)
    db.session.add(new_exhibition)
    db.session.commit()


def get_ongoing_exhibition_by_user_id(user_id):
    """
    This function finds  the exhibition ongoing by user id. We assume
    that user can have only one exhibition ongoing at the same time
    :param user_id: user_id
    :return: Exhibition or None
    """
    user_exhibitions = ExhibitionUser.query.filter_by(user_id=user_id).all()
    ongoing_user_exhibition = None
    for exhibition in user_exhibitions:
        if exhibition.status == "ongoin":
            ongoing_user_exhibition = exhibition
            break
    return ongoing_user_exhibition

