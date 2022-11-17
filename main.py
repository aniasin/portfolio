import os
from datetime import date, datetime
from functools import wraps
import random
import smtplib

import utils

from flask import Flask, render_template, redirect, url_for, flash, request
from flask import abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from sqlalchemy.orm import relationship

from forms import RegisterForm, LoginForm, CreatePostForm, CreateCategoryForm, CreateMaximeForm, CommentForm, \
    ContactForm, CreateToDo, CreateProject


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)

# #CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
# Init login manager
login_manager = LoginManager()
login_manager.init_app(app)
# Captcha
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get("CAPTCHA_PRIVATE")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("CAPTCHA_PUBLIC")

gravatar = Gravatar(app, size=40, rating='x', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    projects = relationship("ToDoProject", back_populates="author")
    todo_items = relationship("ToDo", back_populates="author")


tag_link = db.Table("tag_link", db.Model.metadata,
                    db.Column("post_id", db.Integer, db.ForeignKey("blog_posts.id")),
                    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
                    )


class ToDo(db.Model):
    __tablename__ = "todo_list"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the table name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="todo_items")

    title = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("todo_projects.id"))
    project = relationship("ToDoProject", back_populates="parent_todo_list")


class ToDoProject(db.Model):
    __tablename__ = "todo_projects"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the table name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="projects")
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=True)
    parent_todo_list = db.relationship("ToDo", back_populates="project")


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
    header = db.Column(db.Boolean, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("blog_categories.id"))
    category = relationship("BlogCategory", back_populates="parent_posts")
    tags = db.relationship("Tag", secondary=tag_link, backref=db.backref('entries', lazy='dynamic'))
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


class Maxime(db.Model):
    __tablename__ = "maximes"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)


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


def project_owner_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_projects = [project.id for project in current_user.projects]
        if kwargs["project_id"] not in user_projects:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_now():
    maximes = Maxime.query.all()
    if len(maximes) > 0:
        maxime = random.choice(maximes)
    else:
        maxime = Maxime(text="Welcome!")
        db.session.add(maxime)
        db.session.commit()
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = 0
    return dict(now=datetime.now(), user_id=user_id, maxime=maxime)


# -------- Routes ---------
@app.route('/')
def home():
    last_post = db.session.query(BlogPost).order_by(BlogPost.id.desc()).first()
    header_posts = BlogPost.query.filter_by(header=True).order_by(BlogPost.id.desc()).all()
    return render_template("index.html", last_post=last_post, title="Welcome!", header_posts=header_posts)


@app.route('/blog')
def blog_categories():
    categories = BlogCategory.query.all()
    return render_template("blog_categories.html", title="Blog categories", categories=categories)


@app.route("/post/<int:index>", methods=["POST", "GET"])
def show_post(index):
    post = BlogPost.query.get(index)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in!")
            return redirect(url_for('login'))
        comment = Comment(
            text=form.body.data,
            author=current_user,
            parent_post=post,
            date=date.today().strftime("%B %d, %Y")
        )

        db.session.add(comment)
        db.session.commit()
        with smtplib.SMTP("smtp.gmail.com", 587) as connexion:
            connexion.starttls()
            connexion.login(user=os.environ.get("ADMIN_MAIL"), password=os.environ.get("MAIL_PASS"))
            msg = f"subject: from Blog \n\nComment added.\nPost : https://blog-sillikone.herokuapp.com/post/{post.id}"
            connexion.sendmail(from_addr=os.environ.get("ADMIN_MAIL"), to_addrs=os.environ.get("ADMIN_MAIL"),
                               msg=msg.encode("utf8"))
        return redirect(url_for("show_post", post=post, index=post.id))
    return render_template("post.html", post=post, form=form)


@app.route("/category/<int:index>")
def show_category(index):
    category = BlogCategory.query.get(index)
    posts = category.parent_posts
    if category.name == "Nietzsche":
        posts_title = utils.order_title_alphabetically(posts)
        posts = [BlogPost.query.filter_by(title=title).first() for title in posts_title]
    return render_template("category.html", category=category, posts=posts)


@app.route("/tag/<int:index>")
def show_tag(index):
    tag = Tag.query.get(index)
    posts = tag.entries.all()
    return render_template("tag.html", tag=tag, posts=posts)


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
            header=form.header.data,
            category_id=form.category.data,
            date=date.today().strftime("%B %d, %Y")
        )
        tags = form.tags.data.split()
        new_post.tags = []
        for tag in tags:
            if Tag.query.filter_by(name=tag).first():
                new_tag = Tag.query.filter_by(name=tag).first()
            else:
                new_tag = Tag(name=tag)
                db.session.add(new_tag)
            new_post.tags.append(new_tag)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form, title="New Post")


@app.route("/delete-comment/<int:index>", methods=["GET", "POST"])
@admin_only
def delete_comment(index):
    comment = Comment.query.get(index)
    post = comment.parent_post
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("show_post", index=post.id))


@app.route("/edit-post/<int:index>", methods=["GET", "POST"])
@admin_only
def edit_post(index):
    post = BlogPost.query.get(index)
    categories = [(category.id, category.name) for category in BlogCategory.query.all()]
    new_tags = ""
    for tag in post.tags:
        new_tags += f"{tag.name} "
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        tags=new_tags,
        category=post.category_id,
        author=post.author,
        header=post.header,
        body=post.body
    )
    edit_form.category.choices = categories
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.category_id = edit_form.category.data
        post.body = edit_form.body.data
        post.header = edit_form.header.data
        tags = edit_form.tags.data.split()
        post.tags = []
        for tag in tags:
            if Tag.query.filter_by(name=tag).first():
                new_tag = Tag.query.filter_by(name=tag).first()
            else:
                new_tag = Tag(name=tag)
                db.session.add(new_tag)
            if post not in Tag.query.filter_by(name=tag).first().entries.all():
                post.tags.append(new_tag)
        db.session.commit()
        return redirect(url_for("show_post", post=post, index=post.id))
    return render_template("make-post.html", form=edit_form)


@app.route("/delete-post/<int:index>", methods=["GET", "POST"])
@admin_only
def delete_post(index):
    post = BlogPost.query.get(index)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


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
    return render_template("make-category.html", form=form, title="New Category")


@app.route("/edit_category/<int:index>", methods=["GET", "POST"])
@admin_only
def edit_category(index):
    category = BlogCategory.query.get(index)
    form = CreateCategoryForm(name=category.name,
                              description=category.description,
                              img_url=category.img_url,
                              )
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-category.html", form=form, title="Edit Category")


@app.route("/make-maxime", methods=["GET", "POST"])
@admin_only
def add_maxime():
    form = CreateMaximeForm()
    if form.validate_on_submit():
        new_maxime = Maxime(text=form.text.data)
        db.session.add(new_maxime)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-maxime.html", form=form, title="Create Maxime")


@app.route("/edit-maxime/<int:index>", methods=["GET", "POST"])
@admin_only
def edit_maxime(index):
    maxime = Maxime.query.get(index)
    form = CreateMaximeForm(text=maxime.text)
    if form.validate_on_submit():
        maxime.text = form.text.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-maxime.html", form=form, index=index, title="Edit Maxime")


@app.route("/new-project", methods=["POST", "GET"])
def add_project():
    projects_count = len(ToDoProject.query.filter_by(author=current_user).all())
    if projects_count > 9:  # TODO: find a place to store as variable
        return redirect(url_for("show_profile"))
    form = CreateProject()
    if form.validate_on_submit():
        new_project = ToDoProject(
            name=form.name.data,
            description=form.description.data,
            img_url=form.img_url.data,
            author=current_user,
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("show_todo", project_id=new_project.id))
    return render_template("make-project.html", form=form, title="New Project")


@app.route("/new-project/<int:project_id>", methods=["POST", "GET"])
@project_owner_only
def edit_project(project_id):
    project = ToDoProject.query.get(project_id)
    form = CreateProject(
        name=project.name,
        description=project.description,
        img_url=project.img_url
    )
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for("show_todo", project_id=project.id))
    return render_template("make-project.html", form=form, title="Edit Project")


@app.route("/delete-project/<int:project_id>", methods=["GET", "POST"])
@project_owner_only
def delete_project(project_id):
    project = ToDoProject.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("show_profile", items=current_user.projects))


@app.route("/new-todo/<int:project_id>", methods=["POST", "GET"])
@project_owner_only
def add_todo(project_id):
    project = ToDoProject.query.get(project_id)
    form = CreateToDo()
    if form.validate_on_submit():
        new_todo = ToDo(
            title=form.title.data,
            description=form.description.data,
            body=form.body.data,
            author=current_user,
            priority=form.priority_id.data,
            status=1,
            project=project,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("show_todo", project_id=project.id))
    return render_template("make-todo.html", form=form, title="New Task")


@app.route("/edit-todo/<int:index>/<int:project_id>", methods=["GET", "POST"])
@project_owner_only
def edit_todo(index, project_id):
    todo = ToDo.query.get(index)
    edit_form = CreateToDo(
        title=todo.title,
        description=todo.description,
        body=todo.body,
        priority_id=todo.priority,
    )
    if edit_form.validate_on_submit():
        todo.title = edit_form.title.data
        todo.description = edit_form.description.data
        todo.body = edit_form.body.data
        todo.priority = edit_form.priority_id.data
        db.session.commit()
        return redirect(url_for("show_todo", project_id=todo.project_id))
    return render_template("make-todo.html", form=edit_form, title="Edit Task")


@app.route('/transfer_todo/<int:todo_id>/<int:new_project_id>/<int:project_id>', methods=["GET", "POST"])
@project_owner_only
def transfer_todo(todo_id, new_project_id, project_id):
    new_project = ToDoProject.query.get(new_project_id)
    if len(new_project.parent_todo_list) > 99:  # TODO: find a place to store as variable
        flash("Too many tasks in project")
        return redirect(url_for("show_todo", project_id=project_id))
    todo = ToDo.query.get(todo_id)
    current_project_id = todo.project_id
    todo.project = new_project
    db.session.commit()
    return redirect(url_for("show_todo", project_id=current_project_id))


@app.route('/todo-list/<int:project_id>')
@project_owner_only
def show_todo(project_id):
    project = ToDoProject.query.get(project_id)
    projects_count = len(ToDoProject.query.filter_by(author=current_user).all())
    todo_count = len(project.parent_todo_list)
    return render_template("todo-list.html", project=project, projects_count=projects_count, todo_count=todo_count)


@app.route("/delete-todo/<int:index>/<int:project_id>", methods=["GET", "POST"])
@project_owner_only
def delete_todo(index, project_id):
    todo = ToDo.query.get(index)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("show_todo", project_id=todo.project_id))


@app.route("/toggle-todo/<int:index>/<int:project_id>", methods=["GET", "POST"])
@project_owner_only
def toggle_todo_status(index, project_id):
    todo = ToDo.query.get(index)
    if todo.status == 0:
        todo.status = 1
    else:
        todo.status = 0
    db.session.commit()
    return redirect(url_for("show_todo", project_id=todo.project_id))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        with smtplib.SMTP("smtp.gmail.com", 587) as connexion:
            connexion.starttls()
            connexion.login(user=os.environ.get("ADMIN_MAIL"), password=os.environ.get("MAIL_PASS"))
            msg = f"subject: from user {form.name.data} \n\n{form.message.data}\n{form.email.data}"
            connexion.sendmail(from_addr=form.email.data, to_addrs=os.environ.get("ADMIN_MAIL"),
                               msg=msg.encode("utf8"))
        return render_template("contact.html", form=form, title="Successfully sent message!")
    return render_template("contact.html", form=form, title="Contact Me")


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
    return render_template("register.html", form=form, title="Register")


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
    return render_template("login.html", form=form, title="Login")


@app.route("/profile.html")
def show_profile():
    if not current_user.is_authenticated:
        flash("You must be logged in!")
        return redirect(url_for('login'))
    else:
        projects_count = len(ToDoProject.query.filter_by(author=current_user).all())
        return render_template("profile.html", title=current_user.name, projects_count=projects_count)


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
