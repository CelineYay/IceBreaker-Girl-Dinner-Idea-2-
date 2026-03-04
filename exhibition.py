import datetime

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
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, organizer_id, location, description, start_date, end_date):
        self.name = name
        self.organizer_id = organizer_id
        self.location = location
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

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
    visit_start_date = db.Column(db.DateTime, nullable=False)
    visit_end_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, exhibition_id, user_id, user_goals, exhibition_name, visit_start_date, visit_end_date):
        self.exhibition_id = exhibition_id
        self.user_id = user_id
        self.user_goals = user_goals
        self.exhibition_name = exhibition_name
        self.visit_start_date = visit_start_date
        self.visit_end_date = visit_end_date

    def __repr__(self):
        return '<ExhibitionUser {}>'.format(self.exhibition_name)


def create_exhibition_user(exhibition_id, user_id, user_goals, exhibition_name, visit_start_date, visit_end_date):
    """
    Adds new ExhibitionUser
    :param exhibition_id: exhibition_id
    :param user_id: user_id
    :param user_goals: user_goals (interests)
    :param exhibition_name: exhibition_name
    :param visit_start_date: date of visit (start)
    :param visit_end_date: date of visit (end)
    :return: None
    """
    new_exhibition_user = ExhibitionUser(exhibition_id=exhibition_id, user_id=user_id, user_goals=user_goals,
                                         exhibition_name=exhibition_name, visit_start_date=visit_start_date,
                                         visit_end_date=visit_end_date)
    db.session.add(new_exhibition_user)
    db.session.commit()


def create_exhibition(name, organizer_id, location, description, start_date, end_date):
    """
    This function adds a new exhibition to the database
    :param name: name
    :param organizer_id: organizer_id
    :param location: location
    :param description: description
    :param start_date: start_date
    :param end_date: end_date
    :return: None
    """
    new_exhibition = Exhibition(name=name, organizer_id=organizer_id, location=location, description=description,
                                start_date=start_date, end_date=end_date)
    db.session.add(new_exhibition)
    db.session.commit()


def get_exhibition_by_id(id):
    """
    This function finds the exhibition by its id
    :param id: id
    :return: Exhibition
    """
    return Exhibition.query.filter_by(id=id).first()


def get_exhibitions_by_user(user):
    """
    :param user: User
    :return: list of items of the class Exhibition
    """
    exhibitions_user = ExhibitionUser.query.filter_by(user_id=user.id).all()
    exhibitions = []
    print(exhibitions_user)
    for exhibition_user in exhibitions_user:
        # You need to use .first() to get the actual object, not the query
        exhibition = Exhibition.query.filter_by(id=exhibition_user.exhibition_id).first()
        if exhibition:  # Check if exhibition exists
            exhibitions.append(exhibition)
            print(f"Found exhibition: {exhibition.name}")
    print(f"Total exhibitions: {len(exhibitions)}")
    return exhibitions


def get_exhibition_user_by_exhibition_id_and_user_id(exhibition_id, user_id):
    """
    This function finds the exhibition by its id
    :param exhibition_id: exhibition_id
    :param user_id: user_id
    :return: ExhibitionUser
    """
    return ExhibitionUser.query.filter_by(exhibition_id=exhibition_id, user_id=user_id).first()


def find_current_simultaneous_visit(user1_id, user2_id):
    """
    This function finds the event users visit at the same time and returns
    the current simultaneous exhibition or None. We assume that the visit times of the exhibitions
    for the same user cannot overlap
    :param user1_id: user1_id
    :param user2_id: user2_id
    :return: ExhibitionUser or None
    """
    now = datetime.datetime.now()

    # Find current visit for user1
    user1_current_visit = ExhibitionUser.query.filter(
        ExhibitionUser.user_id == user1_id,
        ExhibitionUser.visit_start_date <= now,
        ExhibitionUser.visit_end_date >= now
    ).first()

    # Find current visit for user2
    user2_current_visit = ExhibitionUser.query.filter(
        ExhibitionUser.user_id == user2_id,
        ExhibitionUser.visit_start_date <= now,
        ExhibitionUser.visit_end_date >= now
    ).first()

    if user1_current_visit.exhibition_id == user2_current_visit.exhibition_id:
        exhibition = get_exhibition_by_id(user1_current_visit.exhibition_id)
        return exhibition.id
    else:
        return None
