from flask_login import LoginManager, login_user, login_required, current_user

from app_and_db import app, db
from user import User, create_user, check_password_hash, get_user_by_email


login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """
    Function that finds the user by id
    :param user_id: id
    :return: User
    """
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
