# System modules
import os
import uuid
import datetime
import functools
from dataclasses import dataclass, field
from typing import Dict, Union, Callable
from binascii import hexlify

# 3rd party modules
from flask import make_response, abort, session, current_app

# local modules
from config import ma
from models.model import Model
from common.utils import Utils
import models.user.errors as UserErrors
# from models.user.decorators import requires_admin, requires_login

__author__ = 'dimz'


# ----------- function as decorator -----------
def requires_login(f: Callable) -> Callable:
    @functools.wraps(f)
    def decorated_function(api_key: str = None, *args, **kwargs):
        if not session.get('email'):
            if api_key and api_key != '':
                try:
                    User.is_api_key_valid(api_key)
                except UserErrors.UserError as e:
                    abort(e.status_code, e.message)
            else:
                # abort(400, 'Anda memerlukan API_KEY untuk dapat mengakses ini')
                abort(403, 'Anda perlu login untuk dapat mengakses ini')
        User.update_logging_user()
        return f(*args, **kwargs)

    return decorated_function


def requires_admin(f: Callable) -> Callable:
    @functools.wraps(f)
    def decorated_function(api_key: str = None, *args, **kwargs):
        if session.get('email') != current_app.config.get('ADMIN', ''):
            abort(403, 'Anda perlu menjadi Administrator untuk dapat mengakses ini')
        return f(*args, **kwargs)

    return decorated_function


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("username", "password", "nama_lengkap", "email", "last_login", "api_key", "hits")


@dataclass(eq=False)
class User(Model):
    collection: str = field(init=False, default="users")
    username: str
    password: str
    nama_lengkap: str
    email: str
    hits: int = field(default=0)
    last_login: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    api_key: str = field(default_factory=lambda: hexlify(os.urandom(40)).decode())
    _id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def json(self) -> Dict:
        user_schema = UserSchema()
        return user_schema.dump(self)

    @classmethod
    def get_by_name(cls, username: str) -> Union["User", None]:
        try:
            return cls.find_one_by("username", username)
        except TypeError:
            return None

    @classmethod
    def find_by_email(cls, email: str) -> "User":
        try:
            return cls.find_one_by('email', email)
        except TypeError:
            raise UserErrors.UserNotFoundError(404, 'A user with this e-mail was not found.')

    @classmethod
    def find_by_api_key(cls, api_key: str) -> "User":
        try:
            return cls.find_one_by('api_key', api_key)
        except TypeError:
            raise UserErrors.UserNotFoundError(404, 'A user with this API_KEY was not found.')

    @classmethod
    def is_login_valid(cls, email: str, password: str) -> bool:
        """This method verifies that an e-mail/password combo (as sent by the site forms) is valid or not.
        Checks that the e-mail exists, and that the password associated to that e-mail is correct.
        @param email: The user's email
        @param password: The password
        @return: user model if valid, an exception otherwise
        """
        user = cls.find_by_email(email)

        if not Utils.check_hashed_password(password, user.password):
            # Tell the user that their password is wrong
            raise UserErrors.IncorrectPasswordError(400, "Your password was wrong.")
        return True

    @staticmethod
    def is_api_key_valid(api_key: str) -> bool:
        """This method verifies that an api_key (as sent by the site forms) is valid or not.
        Checks that the api_key exists.
        @param api_key: The api_key
        @return: user model if valid, an exception otherwise
        """
        user = User.find_by_api_key(api_key)

        if user is None:
            # Tell the user that their api_key is wrong
            raise UserErrors.InvalidApiKeyError(400, "API_KEY tidak valid")
        session['email'] = user.email
        return True

    @staticmethod
    def update_logging_user():
        user_now = User.find_by_email(session.get('email'))
        user_now.last_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        user_now.hits = user_now.hits + 1
        user_now.save_to_mongo()

    # ----------- function to answer API endpoint -----------
    @classmethod
    def register_user(cls, user: Dict):
        """This method registers a user using e-mail and password.
        @param user: user dengan parameter e-mail dan password
        @return: 201 if registered successfully, or 400 or 409 otherwise (exceptions can also be raised)
        """
        username = user.get('username')
        password = user.get('password')
        nama_lengkap = user.get('nama_lengkap')
        email = user.get('email')

        try:
            if not Utils.email_is_valid(email):
                raise UserErrors.InvalidEmailError(400, "Format email tidak sesuai.")
        except UserErrors.UserError as e:
            abort(e.status_code, e.message)

        try:
            cls.find_by_email(email)
            raise UserErrors.UserAlreadyRegisteredError(409, "Email untuk registrasi sudah pernah dipakai.")
        except UserErrors.UserAlreadyRegisteredError as e:
            abort(e.status_code, e.message)
        except UserErrors.UserNotFoundError:
            nu = User(username, Utils.hash_password(password), nama_lengkap, email)
            nu.save_to_mongo()
            data = nu.json()
            data.pop('password')
            session['email'] = email
            return data, 201
        except UserErrors.UserError as e:
            abort(e.status_code, e.message)

    @staticmethod
    def login_user(user: Dict):
        try:
            if User.is_login_valid(user.get('email'), user.get('password')):
                session['email'] = user.get('email')
                User.update_logging_user()
                return make_response("Anda berhasil login dengan email: {}.".format(user.get('email')), 200)
        except UserErrors.UserError as e:
            abort(e.status_code, e.message)

    @staticmethod
    @requires_login
    @requires_admin
    def read_all(api_key: str = None):
        """Fungsi ini merespon API pada endpoint /api/v1.0/user/{username}, yaitu menghapus pengguna dengan username
        dari database.
        @param api_key: String API_KEY
        @return: JSON hasil pencarian user
        """
        # Create the list of stores from our data
        user = User.all()

        if user is None:
            # Bila tidak ditemukan sama sekali
            return make_response("Tidak ditemukan user dengan parameter yang telah diberikan.", 204)
        else:
            # Serialize the data for the response
            user_schema = UserSchema(many=True)
            data = user_schema.dump(user)
            for d in data:
                d.pop('password')
            return data

    @staticmethod
    @requires_login
    def read_one(username: str, api_key: str = None):
        """Fungsi ini merespon API pada endpoint /api/v1.0/user/{username}, yaitu dengan mencari satu pengguna dengan
        parameter username.
        @param username: String id sebagai acuan pencarian toko pada database
        @param api_key: String API_KEY
        @return: Data Pengguna sebagai hasil pencarian
        """
        # Build the initial query
        try:
            user = User.get_by_name(username)
        except TypeError:
            user = None

        # Did we find a user?
        if user is not None:
            # Serialize the data for the response
            user_schema = UserSchema()
            data = user_schema.dump(user)
            data.pop('password')
            return data

        # Otherwise, nope, didn't find that person
        else:
            abort(404, 'Pengguna dengan username {} tidak ditemukan.'.format(username))

    @staticmethod
    @requires_login
    def update(username: str, user: Dict, api_key: str = None):
        """Fungsi ini merespon API pada endpoint /api/v1.0/user/{username}, yaitu untuk melakukan update data pengguna
        pada parameter username, nama_lengkap, dan email
        @param username: String id sebagai acuan pencarian toko pada database
        @param user: Data mengenai toko yang hendak diperbarui sesuai schema
        @param api_key: String API_KEY
        @return: 200 on success, 404 on not found, 409 on email used by other user
        """
        # Get the user requested from the db into session
        try:
            update_user = User.get_by_name(username)
        except TypeError:
            update_user = None

        # Try to find an existing user with the same name as the update
        email = user.get("email")
        try:
            existing_user = User.find_by_email(email)
        except UserErrors.UserNotFoundError:
            # berarti email yang siperbarui tidak dipakai oleh user yang lain
            # sehingga ambil user dengan email dari session
            existing_user = User.find_by_email(session.get('email'))

        # Are we trying to find a user that does not exist?
        if update_user is None:
            abort(404, "Pengguna dengan username {} tidak ditemukan.".format(username))

        # Would our update create a duplicate of another user already existing?
        elif existing_user is not None and existing_user.username != username:
            abort(409, "Email {} telah digunakan oleh pengguna lain.".format(email))

        # Otherwise go ahead and update!
        else:
            # Set the updated fields to the user we want to update
            update_user.username = user.get("username")
            update_user.nama_lengkap = user.get("nama_lengkap")
            update_user.email = user.get("email")

            # merge the new object into the old and commit it to the db
            update_user.save_to_mongo()
            session['email'] = user.get('email')

            # return updated user in the response
            data = update_user.json()
            data.pop('password')
            return data, 200

    @staticmethod
    @requires_login
    def delete(username: str, api_key: str = None):
        """Fungsi ini merespon API pada endpoint /api/v1.0/user/{username}, yaitu menghapus pengguna dengan username
        dari database.
        @param username: String username sebagai acuan pencarian pengguna pada database
        @param api_key: String API_KEY
        @return: 200 on success, 404 on not found
        """
        # Get the user requested
        try:
            user = User.get_by_name(username)
        except TypeError:
            user = None

        # Did we find a user?
        if user is not None:
            user.remove_from_mongo()
            if session.get('email') == user.email:
                session.pop('email')
            return make_response("Pengguna dengan username {} berhasil dihapus.".format(username), 200)

        # Otherwise, nope, didn't find that person
        else:
            abort(404, "Pengguna dengan username {} tidak ditemukan.".format(username))

    @staticmethod
    @requires_login
    def reset_password(username: str, user: Dict, api_key: str = None):
        """Fungsi ini merespon API pada endpoint /api/v1.0/user/{username}/reset_password, yaitu melakukan reset
        password pengguna.
        @param username: String id sebagai acuan pencarian toko pada database
        @param user: Data mengenai toko yang hendak diperbarui sesuai schema
        @param api_key: String API_KEY
        @return: 200 on success, 404 on not found
        """
        # Get the user requested from the db into session
        try:
            update_user = User.get_by_name(username)
        except TypeError:
            update_user = None

        # Try to find an existing user with the same name as the update
        User.find_by_email(session.get('email'))

        # Are we trying to find a user that does not exist?
        if update_user is None:
            abort(404, "Pengguna dengan username {} tidak ditemukan.".format(username))

        # Otherwise go ahead and update!
        else:
            # Set the updated fields to the user we want to update
            update_user.password = Utils.hash_password(user.get("password"))

            # merge the new object into the old and commit it to the db
            update_user.save_to_mongo()

            # return updated user in the response
            data = update_user.json()
            data.pop('password')
            User.update_logging_user()
            return data, 200
