from flask import Blueprint, request, session, render_template
from models.user import User, UserErrors

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login')
def login_user():
    return render_template("users/login.html")  # Send the user an error if their login was invalid


@user_blueprint.route('/register')
def register_user():
    return render_template("users/register.html")  # Send the user an error if their login was invalid


# @user_blueprint.route('/profile')
# def profile():
#     return render_template("users/profile.html")  # Send the user an error if their login was invalid

