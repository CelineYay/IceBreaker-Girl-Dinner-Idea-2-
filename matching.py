from app_and_db import db
from device import get_user_by_device_rfid


class UsersMatch(db.Model):
    """
    Matching class
    """
    id = db.Column(db.Integer, primary_key=True)
    first_user_id = db.Column(db.Integer, nullable=False)
    second_user_id = db.Column(db.Integer, nullable=False)
    exhibition_id = db.Column(db.Integer, nullable=False)
    matching_score = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False)

    def __init__(self, first_user_id, second_user_id, exhibition_id, matching_score, success):
        self.first_user_id = first_user_id
        self.second_user_id = second_user_id
        self.exhibition_id = exhibition_id
        self.matching_score = matching_score
        self.success = success

    def __repr__(self):
        return '<User Matching {}>'.format(self.id)


# if this function returns some match, that means that the users have already been matched
# (successfully or not) => there is no need to match them again
def find_match(user1, user2):
    """
    this function returns match (class UsersMatch) or None if users have never been matched
    :param user1: first user
    :param user2: second user
    :return: UsersMatch or None
    """
    match = UsersMatch.query.filter_by(first_user_id=user1.id, second_user_id=user2.id).first()
    if not match:
        match = UsersMatch.query.filter_by(first_user_id=user1.id, second_user_id=user2.id).first()
        if not match:
            return None

    return match


def add_match(rfid1, rfid2):
    """
    This function returns True if the users are matched successfully
    (so can send their contacts to each other) and False if the users don't match or if
    they have already been matched before (successfully or not) (cuz there is no need to
    send contacts again)
    :param rfid1: first user's device's rfid
    :param rfid2: second user's device's rfid
    :return:
    """
    user1 = get_user_by_device_rfid(rfid1)
    user2 = get_user_by_device_rfid(rfid2)
    match = find_match(user1, user2)
    if match:
        return False
    else:
        pass
