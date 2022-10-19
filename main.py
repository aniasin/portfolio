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

from forms import RegisterForm, LoginForm, CreatePostForm, CreateCategoryForm
import utils


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)

# #CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)


# #CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


tag_link = db.Table("tag_link", db.Model.metadata,
                    db.Column("post_id", db.Integer, db.ForeignKey("blog_posts.id")),
                    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                    )


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the table name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("blog_categories.id"))
    category = relationship("BlogCategory", back_populates="parent_posts")
    tags = db.relationship("Tag", secondary=tag_link)
    comments = relationship("Comment", back_populates="parent_post")


class BlogCategory(db.Model):
    __tablename__ = "blog_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=True)
    parent_posts = db.relationship("BlogPost", back_populates="category")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------- Routes ---------
@app.route('/')
def home():
    header_posts = []
    last_post = db.session.query(BlogPost).order_by(BlogPost.id.desc()).first()
    if last_post:
        header_posts = [
            category.parent_posts[0] for category in BlogCategory.query.all()
            if category is not last_post.category and len(category.parent_posts > 0)]
    return render_template("index.html", last_post=last_post, user_id=utils.get_user_id(current_user), title="Welcome!",
                           header_posts=header_posts)


@app.route('/blog')
def blog():
    tags = Tag.query.all()
    return render_template("blog.html", user_id=utils.get_user_id(current_user), title="Blog categories", tags=tags)


@app.route("/new-post", methods=["POST", "GET"])
@admin_only
def add_new_post():
    categories = [(category.id, category.name) for category in BlogCategory.query.all()]
    form = CreatePostForm()
    form.category.choices = categories
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            category_id=form.category.data,
            date=date.today().strftime("%B %d, %Y")
        )
        tags = form.tags.data.split()
        for tag in tags:
            new_tag = Tag(name=tag)
            db.session.add(new_tag)
            new_post.tags.append(new_tag)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form, user_id=utils.get_user_id(current_user), title="New Post")


@app.route("/make-category", methods=["POST", "GET"])
@admin_only
def add_category():
    form = CreateCategoryForm()
    if form.validate_on_submit():
        new_category = BlogCategory(name=form.name.data,
                                    description=form.description.data,
                                    img_url=form.img_url.data,
                                    )
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-category.html", user_id=utils.get_user_id(current_user),
                           form=form, title="New Category")


@app.route('/register.html', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        if not User.query.filter_by(email=email).first():
            password = request.form.get("password")
            name = request.form.get("name")
            user = User()
            user.email = email
            user.password = generate_password_hash(password, salt_length=8)
            user.name = name
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash("User already exists.")
    return render_template("register.html", form=form, user_id=utils.get_user_id(current_user), title="Register")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid password or username")
    return render_template("login.html", form=form, user_id=utils.get_user_id(current_user), title="Login")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
    # http_server = WSGIServer(('127.0.0.1', 5000), app)
    # http_server.serve_forever()
