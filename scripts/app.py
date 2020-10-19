#!venv/bin/python
import os
from flask import Flask, url_for, redirect, render_template, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
import cv2

from face_recog.face_id import FaceId
from anti_spoofing.anti_spoofing import check_authenticity
from utility.user_info_form import UserInfoForm

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    face_encoding = db.Column(db.PickleType())
    balance = db.Column(db.Float())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255))
    product_unit_price = db.Column(db.Float())
    product_code = db.Column(db.String(255))
    product_discount = db.Column(db.Float())

    def __str__(self):
        return self.product_name


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list

class ProductView(MyModelView):
    column_editable_list = ['product_name', 'product_unit_price', 'product_code', 'product_discount']
    column_searchable_list = column_editable_list
    # form_excluded_columns = column_exclude_list
    column_filters = column_editable_list


class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        # url来源见我上一篇博客
        self.video = cv2.VideoCapture("../data/test_video_spoofing.mp4")
        self.faceid = FaceId()
        self.faceid.encode_faces() 
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        is_real, frame_auth = check_authenticity(image.copy())
            
        if is_real:
            frame = self.faceid.match_faces(image.copy())     
            image = frame
        else:
            image = frame_auth
        # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()


class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')

    def gen(self, camera):
        while True:
            frame = camera.get_frame()
            # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    @expose('/video_feed')  # 这个地址返回视频流响应
    def video_feed(self):
        return Response(self.gen(VideoCamera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')   



from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Required


class AssessmentView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        
        form = UserInfoForm(request.form)
        if request.method == 'POST' and form.validate():
            
            user_id = session['_user_id']
            user = db.session.query(User).filter(User.id == user_id).first()
            user_first_name = user['first_name']
            user_last_name = user['last_name']
            user_email = user['email']
            
            survey_user = db.session.query(Survey).filter(Survey.email == user_email)
            score = 0

            suggestions_dict = {}
            for i, filed in enumerate(form):
                if i < 5:
                    score += SCORE_MAP[filed.data]
                else:
                    max_score, category = SCORE_CATEGORY_DICT[i+60]
                    if SCORE_MAP[filed.data] < max_score:
                        suggestions_dict[category] = suggestions_dict.get(category, 0) + max_score - SCORE_MAP[filed.data]
                    else:
                        score += SCORE_MAP[filed.data]

            # score = int((score / TOTAL_SCORE) * 100)

            rank = db.session.query(Survey).filter((Survey.current_score > score) & (Survey.email != user_email)).count()+1

            suggestion = "\n".join(list(suggestions_dict.keys()))
            if survey_user.count() == 0:
                survey_user = Survey(first_name = user_first_name, last_name = user_last_name, email = user_email, current_score = score, history_scores = str(score), rank = rank, active = False, suggestion = suggestion)  
            else:
                survey_user = survey_user.first()
                survey_user.current_score = score
                survey_user.history_scores += ", "+str(score)
                survey_user.rank = rank
                survey_user.suggestion = suggestion
            db.session.add(survey_user)
            db.session.commit()
            
            # renew rank for every one:
            for user in db.session.query(Survey).all():
                rank = db.session.query(Survey).filter((Survey.current_score > user.current_score) & (Survey.email != user.email)).count()+1
                user.rank = rank
                db.session.add(user)
                db.session.commit()

            es = EmailSender()
            es.send_score(user_first_name, user_email, score, suggestions_dict)
            flash("You have successfully submitted your assessment!", "success")

            return self.render('admin/assessment_done_index.html')

        return self.render('admin/assessment_index.html', form=AssessmentForm())


# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Create admin
admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(ProductView(Product, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Products"))
admin.add_view(CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=encrypt_password(tmp_pass),
                roles=[user_role, ]
            )
        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.run(debug=True)