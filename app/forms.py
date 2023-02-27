from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm): 
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    
    
class UploadForm(FlaskForm):
    pic = FileField("Photo", validators=[FileRequired(), FileSize(max_size=4000000), FileAllowed(["jpg", "png"], message="Image Files Only!")])