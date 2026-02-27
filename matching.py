import torch


from app_and_db import db
from device import get_user_by_device_rfid
from exhibition import Exhibition, ExhibitionUser, find_current_simultaneous_visit, \
    get_exhibition_user_by_exhibition_id_and_user_id
from user import model


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


def create_match(first_user_id, second_user_id, exhibition_id, matching_score, success):
    """
    This function adds a new match to the database
    :param first_user_id: first_user_id
    :param second_user_id: second_user_id
    :param exhibition_id: exhibition_id
    :param matching_score: matching_score
    :param success: success
    :return: None
    """
    new_match = UsersMatch(
        first_user_id=first_user_id,
        second_user_id=second_user_id,
        exhibition_id=exhibition_id,
        matching_score=matching_score,
        success=success
    )
    db.session.add(new_match)
    db.session.commit()


def add_match(rfid1, rfid2):
    """
    This function returns True if the users are matched successfully
    (so can send their contacts to each other) and False if the users don't match, or if
    the users don't have a simultaneous event they both are currently at, or if
    they have already been matched before (successfully or not) (cuz there is no need to
    send contacts again)
    :param rfid1: first user's device's rfid
    :param rfid2: second user's device's rfid
    :return: Bool
    """
    user1 = get_user_by_device_rfid(rfid1)
    user2 = get_user_by_device_rfid(rfid2)
    match = find_match(user1, user2)
    if match:
        return False
    else:
        exhibition = find_current_simultaneous_visit(user1.id, user2.id)
        if not exhibition:
            return False
        else:
            exhibition_user1 = get_exhibition_user_by_exhibition_id_and_user_id(exhibition.id, user1.id)
            exhibition_user2 = get_exhibition_user_by_exhibition_id_and_user_id(exhibition.id, user2.id)

            user1_goals = exhibition_user1.user_goals
            user2_goals = exhibition_user2.user_goals

            user1_embedding_resume = user1.get_embedding_tensor()
            user2_embedding_resume = user2.get_embedding_tensor()

            with torch.no_grad():
                user1_goals_embeddings = torch.tensor(model.encode(user1_goals))
                user2_goals_embeddings = torch.tensor(model.encode(user2_goals))

            combined1 = torch.cat([user1_embedding_resume, user1_goals_embeddings])
            combined2 = torch.cat([user2_embedding_resume, user2_goals_embeddings])

            similarity = torch.cosine_similarity(combined1.unsqueeze(0), combined2.unsqueeze(0)).item()

            match_threshold = 0.54

            success = similarity >= match_threshold

            create_match(user1.id, user2.id, exhibition.id, similarity, success)

            return success
