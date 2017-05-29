from flask_wtf import Form
from wtforms import (StringField, PasswordField,
                     TextAreaField, DateTimeField)
from wtforms.validators import (DataRequired, Length,
                                EqualTo)


class RegistrationForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=2),
                                         EqualTo(
                                            'password2',
                                            message='Passwords must match')])
    password2 = PasswordField('Confirm password',
                              validators=[DataRequired()])


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class BlogForm(Form):
    title = StringField("Title", validators=[DataRequired()])
    date = DateTimeField("Enter date ex. 12/25/2016",
                         format='%m/%d/%Y',
                         validators=[DataRequired()])
    time_spent = StringField("Time it took ex 2 hours",
                             validators=[DataRequired()])
    learned = TextAreaField("What did you learn?", validators=[DataRequired()])
    resources = TextAreaField("Are there any resources to save?")
    tags = StringField("Tags (seperate by a coma)")
