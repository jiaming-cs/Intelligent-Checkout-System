from wtforms.fields import SubmitField
from wtforms.form import Form


class PostForm(Form):
    submit = SubmitField(label ="Submit")