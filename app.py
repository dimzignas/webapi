import os
import uuid
from flask import render_template, session
from config import connex_app, app
from common.database import Database
from views.users import user_blueprint

__author__ = 'dimz'

# Get the application instance
app.secret_key = uuid.uuid4().hex
app.config.update(
    ADMIN=os.environ.get('ADMIN')
)

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('openapi.yml')

app.register_blueprint(user_blueprint, url_prefix='/app/users')


@app.before_first_request
def init_db():
    Database.initialize()


# Create a URL route in our application for "/"
@app.route("/")
def home():
    is_logged_in = False if not session.get('email') else True
    return render_template("home.html", is_logged_in=is_logged_in)


if __name__ == '__main__':
    connex_app.run(host='0.0.0.0', port=61296, debug=True)
