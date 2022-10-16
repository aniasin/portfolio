import datetime
import os
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request
from flask import abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from gevent.pywsgi import WSGIServer
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)


@app.route('/')
def get_all_posts():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
    # http_server = WSGIServer(('127.0.0.1', 5000), app)
    # http_server.serve_forever()
