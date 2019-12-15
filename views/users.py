from flask import Blueprint, request, session, render_template
from models.user import requires_login

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login')
def login_user():
    is_logged_in = False if not session.get('email') else True
    return render_template("users/login.html", is_logged_in=is_logged_in)


@user_blueprint.route('/register')
def register_user():
    is_logged_in = False if not session.get('email') else True
    return render_template("users/register.html", is_logged_in=is_logged_in)


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@requires_login
def profile():
    is_logged_in = False if not session.get('email') else True
    if request.method == 'POST':
        uname = request.form['uname']
        api_key = request.form['key']
        return render_template("users/profile.html", uname=uname, api_key=api_key, is_logged_in=is_logged_in)

    return render_template("users/login.html", is_logged_in=is_logged_in)


@user_blueprint.route('/logout')
@requires_login
def logout():
    session.pop('email')
    return render_template("home.html", is_logged_in=False)
