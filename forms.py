from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Username", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL")
    category = SelectField("Category", choices=[])
    tags = StringField("Tags")
    header = BooleanField("Header")
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CreateCategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Submit Category")


class CreateMaximeForm(FlaskForm):
    text = TextAreaField("Text", validators=[DataRequired()])
    submit = SubmitField("Submit Maxime")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment")
    submit = SubmitField("Comment")


class CreateToDo(FlaskForm):
    title = StringField("ToDo Title", validators=[DataRequired()])
    description = StringField("Description")
    priority_id = SelectField("Priority", choices=[(0, "Normal"), (1, "Important"), (2, "Critical")])
    body = CKEditorField("Body")
    submit = SubmitField("Submit")


class CreateProject(FlaskForm):
    name = StringField("project name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    img_url = StringField("Image URL")
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    name = StringField("Enter your name...", validators=[DataRequired()])
    email = EmailField("Enter your email...", validators=[DataRequired()])
    message = CKEditorField("Message")
    recaptcha = RecaptchaField()
    submit = SubmitField("Send")
