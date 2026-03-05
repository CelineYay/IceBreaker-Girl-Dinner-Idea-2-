from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask import render_template, request, redirect, url_for, flash, current_app, abort, send_file
from werkzeug.utils import secure_filename
import os
import datetime

from app_and_db import app, db
from user import User, create_user, check_password, get_user_by_email, get_user_by_id
from exhibition import Exhibition, ExhibitionUser, create_exhibition, get_exhibition_user_by_exhibition_id_and_user_id, \
    get_exhibition_by_id, get_exhibitions_by_user, create_exhibition_user
from device import get_devices_by_user, delete_device_by_device_id, get_device_by_device_id
from matching import UsersMatch


login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    # db.drop_all()
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """
    Function that finds the user by id
    :param user_id: id
    :return: User
    """
    return User.query.get(int(user_id))


# @app.errorhandler(Exception)
# def handle_exception(e):
#     """
#     Returns error page
#     :param e: error
#     :return: html
#     """
#     return render_template('error.html', error=str(e).split()[0])


@app.route('/')
def index():
    """
    Returns index page
    :return: html
    """
    return render_template('index.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """
    Function for user registration
    :return: html
    """
    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        repeat_password = request.form.get('repeating')
        resume = request.files.get('resume')

        if not (name and email and phone and password and repeat_password):
            flash("Please, don't leave empty fields")
            return redirect(url_for('sign_up'))

        if password != repeat_password:
            flash("Passwords are different.")
            return redirect(url_for('sign_up'))

        if get_user_by_email(email):
            flash("User already exists.")
            return redirect(url_for('sign_up'))

        linkedin_path = ""

        if resume and resume.filename != '':
            if not resume.filename.lower().endswith(".pdf"):
                flash("Resume must be PDF")
                return redirect(url_for('sign_up'))

            filename = secure_filename(resume.filename)

            upload_folder = os.path.join(current_app.root_path, "static/uploads")
            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)
            resume.save(file_path)

            linkedin_path = file_path

        create_user(
            name=name,
            phone_number=phone,
            email=email,
            password=password,
            linkedin_path=linkedin_path
        )

        return redirect(url_for('sign_in'))

    return render_template('sign_up.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    """
    Function that allows existing user to log in into their account
    :return: html
    """
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        curr_user = get_user_by_email(email)

        if not curr_user:
            flash("There is no user with this email.")
            return redirect(url_for('sign_in'))

        if not check_password(curr_user, password):
            flash("Wrong password or email")
            return redirect(url_for('sign_in'))

        if check_password(curr_user, password):
            login_user(curr_user)
            return redirect(url_for('account'))

    return render_template('sign_in.html')


@app.route('/account/organise_new_event', methods=['GET', 'POST'])
def organise_new_event():
    """
    Function for the event organisation
    :return: html
    """
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        location = request.form.get('location')
        description = request.form.get('description')

        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        print([event_name, location, description, start_date_str, end_date_str])

        if not all([event_name, location, description, start_date_str, end_date_str]):
            flash('All fields are required')
            return render_template('organise_new_event.html')

        try:
            start_date = datetime.datetime.fromisoformat(start_date_str)
            end_date = datetime.datetime.fromisoformat(end_date_str)

        except ValueError:
            flash('Invalid date format')
            return render_template('organise_new_event.html')

        now = datetime.datetime.now()

        if end_date <= start_date:
            flash('End date must be after start date')
            return render_template('organise_new_event.html')

        if end_date < now:
            flash('Cannot organise for past dates')
            return render_template('organise_new_event.html')

        create_exhibition(name=event_name, organizer_id=current_user.id, location=location,
                          description=description, start_date=start_date, end_date=end_date)

        return redirect(url_for('account'))

    return render_template('organise_new_event.html')


@app.route('/account')
@login_required
def account():
    """
    Returns user's account page
    :return: html
    """
    user = current_user

    plan_events = get_exhibitions_by_user(user)

    registered_event_ids = [event.id for event in plan_events]

    all_events = Exhibition.query.all()

    organised_events = Exhibition.query.filter_by(organizer_id=user.id).all()
    devices = get_devices_by_user(user)

    visit_dates = {}
    for eu in ExhibitionUser.query.filter_by(user_id=user.id).all():
        visit_dates[eu.exhibition_id] = {
            'start': eu.visit_start_date,
            'end': eu.visit_end_date,
            'goals': eu.user_goals
        }

    return render_template('account.html',
                           user=user,
                           plan_events=plan_events,
                           all_events=all_events,
                           organised_events=organised_events,
                           devices=devices,
                           registered_event_ids=registered_event_ids,
                           visit_dates=visit_dates)


@app.route('/sign_out')
@login_required
def sign_out():
    """
    Logs out the current user and redirects to the home page
    :return: html
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/account//delete_link_sling/<int:device_id>', methods=['POST'])
@login_required
def delete_link_sling(device_id):
    """
    Deletes the link Sling chosen from the database
    :return: html
    """
    device = get_device_by_device_id(device_id)

    if device.owner_id != current_user.id:
        abort(403)

    delete_device_by_device_id(device_id)
    return redirect(url_for('account'))


@app.route('/account/event_registration/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_registration(event_id):
    """
    Function for the event registration
    :param event_id: event_id
    :return: html
    """
    event = get_exhibition_by_id(event_id)

    user = current_user

    existing_registration = get_exhibition_user_by_exhibition_id_and_user_id(event_id, user.id)
    if existing_registration:
        flash('You are already registered for this event')
        return render_template('event_registration.html', event=event)

    if request.method == 'POST':
        try:
            goals = request.form.get('goals')
            visit_start_date_str = request.form.get('visit_start_date')
            visit_end_date_str = request.form.get('visit_end_date')

            print([goals, visit_start_date_str, visit_end_date_str])

            if not all([goals, visit_start_date_str, visit_end_date_str]):
                flash('All fields are required')
                return render_template('event_registration.html', event=event)

            try:
                visit_start_date = datetime.datetime.fromisoformat(visit_start_date_str)
                visit_end_date = datetime.datetime.fromisoformat(visit_end_date_str)
            except ValueError:
                flash('Invalid date format')
                return render_template('event_registration.html', event=event)

            now = datetime.datetime.now()

            if visit_start_date < event.start_date or visit_start_date > event.end_date:
                flash('Visit start date must be within the exhibition dates')
                return render_template('event_registration.html', event=event)

            if visit_end_date < event.start_date or visit_end_date > event.end_date:
                flash('Visit end date must be within the exhibition dates')
                return render_template('event_registration.html', event=event)

            if visit_end_date <= visit_start_date:
                flash('End date must be after start date')
                return render_template('event_registration.html', event=event)

            if visit_end_date < now:
                flash('Cannot register for past dates')
                return render_template('event_registration.html', event=event)

            overlapping_visits = ExhibitionUser.query.filter(
                ExhibitionUser.user_id == user.id,
                ExhibitionUser.visit_start_date < visit_end_date,
                ExhibitionUser.visit_end_date > visit_start_date
            ).first()

            if overlapping_visits:
                flash('This visit overlaps with another exhibition you are registered for')
                return render_template('event_registration.html', event=event)

            create_exhibition_user(
                exhibition_id=event_id,
                user_id=user.id,
                user_goals=goals,
                exhibition_name=event.name,
                visit_start_date=visit_start_date,
                visit_end_date=visit_end_date
            )

            return redirect(url_for('account'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}')
            return render_template('event_registration.html', event=event)

    return render_template('event_registration.html', event=event)


@app.route('/account/matches')
@login_required
def matches():
    """
    Returns matches page
    :return: html
    """
    user = current_user

    all_exhibitions = Exhibition.query.all()

    matches_by_exhibition = {}

    for exhibition in all_exhibitions:
        exhibition_id = exhibition.id

        current_user_exhibition = get_exhibition_user_by_exhibition_id_and_user_id(
            exhibition_id, user.id
        )
        current_user_goals = current_user_exhibition.user_goals if current_user_exhibition else None

        matches_as_first = UsersMatch.query.filter_by(
            first_user_id=user.id,
            exhibition_id=exhibition_id,
            success=True
        ).all()

        matches_as_second = UsersMatch.query.filter_by(
            second_user_id=user.id,
            exhibition_id=exhibition_id,
            success=True
        ).all()

        all_matches = []

        for match in matches_as_first:
            other_user = get_user_by_id(match.second_user_id)
            if other_user:
                other_user_exhibition = get_exhibition_user_by_exhibition_id_and_user_id(
                    exhibition_id, other_user.id
                )
                goals = other_user_exhibition.user_goals if other_user_exhibition else "No goals specified"

                all_matches.append({
                    'match': match,
                    'other_user': {
                        'id': other_user.id,
                        'name': other_user.name,
                        'email': other_user.email,
                        'phone_number': other_user.phone_number,
                        'linkedin_path': other_user.linkedin_path,
                        'has_resume': bool(other_user.linkedin_path),
                        'goals': goals
                    },
                    'role': 'first'
                })

        for match in matches_as_second:
            other_user = get_user_by_id(match.first_user_id)
            if other_user:
                other_user_exhibition = get_exhibition_user_by_exhibition_id_and_user_id(
                    exhibition_id, other_user.id
                )
                goals = other_user_exhibition.user_goals if other_user_exhibition else "No goals specified"

                all_matches.append({
                    'match': match,
                    'other_user': {
                        'id': other_user.id,
                        'name': other_user.name,
                        'email': other_user.email,
                        'phone_number': other_user.phone_number,
                        'linkedin_path': other_user.linkedin_path,
                        'has_resume': bool(other_user.linkedin_path),
                        'goals': goals
                    },
                    'role': 'second'
                })

        if all_matches:
            all_matches.sort(key=lambda x: x['match'].matching_score, reverse=True)

            matches_by_exhibition[exhibition.name] = {
                'exhibition': exhibition,
                'matches': all_matches,
                'current_user_goals': current_user_goals
            }

    sorted_exhibitions = dict(sorted(matches_by_exhibition.items()))

    return render_template('matches.html', matches_by_exhibition=sorted_exhibitions, user=user)


@app.route('/download_resume/<int:user_id>')
@login_required
def download_resume(user_id):
    """
    Allow users to download resume of their matches
    :param user_id: id of the user who's cv to download
    :return: file download
    """
    current_user_id = current_user.id

    match_exists = UsersMatch.query.filter(
        ((UsersMatch.first_user_id == current_user_id) & (UsersMatch.second_user_id == user_id) |
         (UsersMatch.first_user_id == user_id) & (UsersMatch.second_user_id == current_user_id)) &
        (UsersMatch.success is True)
    ).first()

    print(match_exists)

    # if not match_exists:
    #     abort(403, "You don't have permission to view this user's resume")

    user = get_user_by_id(user_id)
    # if not user or not user.linkedin_path:
    #     abort(404, "Resume not found")
    #
    # if not os.path.exists(user.linkedin_path):
    #     abort(404, "Resume file not found")

    return send_file(
        user.linkedin_path,
        as_attachment=True,
        download_name=f"{user.name}_resume.pdf",
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
