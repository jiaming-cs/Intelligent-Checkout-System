from wtforms.fields import SubmitField, StringField
from wtforms.form import Form
from wtforms.validators import DataRequired, Email

class UserInfoForm(Form):
    first_name = StringField(label="Fist Name", validators=[DataRequired()])
    last_name = StringField(label="Last Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[Email(), DataRequired()])
    submit = SubmitField(label ="Submit")