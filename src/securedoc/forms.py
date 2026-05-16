"""WTForms with CSRF protection (Flask-WTF)."""
from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(r"^[\w.\-]+$", message="Alphanumeric, dot, hyphen only."),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class DocumentUploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    file = FileField("File", validators=[FileRequired()])
    submit = SubmitField("Upload")


class ShareForm(FlaskForm):
    grantee_username = StringField(
        "Username to share with",
        validators=[DataRequired(), Length(max=80)],
    )
    role = SelectField(
        "Role",
        choices=[
            ("VIEW", "View / download"),
            ("COMMENT", "Comment"),
            ("EDIT", "Edit / new version"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Share")


class CommentForm(FlaskForm):
    body = TextAreaField("Comment", validators=[DataRequired(), Length(max=4000)])
    submit = SubmitField("Post")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Search")
