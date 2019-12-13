import os
import uuid
from flask import render_template
from config import connex_app, app
from common.database import Database

__author__ = 'dimz'

# Get the application instance
app.secret_key = uuid.uuid4().hex
app.config.update(
    ADMIN=os.environ.get('ADMIN')
)

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('openapi.yml')


@app.before_first_request
def init_db():
    Database.initialize()


# Create a URL route in our application for "/"
@app.route("/")
def home():
    return render_template("home.html")


from views.users import user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/app/users')
