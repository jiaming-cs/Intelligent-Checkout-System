#!venv/bin/python
import os
from flask import url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin import helpers as admin_helpers

from app import app, db
from app.views import MyModelView, UserView, ProductView, RegisteredUserView, CheckoutView, UserRegistrationView, ObjectDetectionView
from app.database import Role, User, Product, RegisteredUser

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def get_product_num():
    return db.session.query(Product).count()

def get_registereduser_num():
    return db.session.query(RegisteredUser).count()

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

@app.context_processor
def inject_paths():
    return dict(product_num = get_product_num(),
                registereduser_num = get_registereduser_num())

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
admin.add_view(RegisteredUserView(RegisteredUser, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Registered User"))
admin.add_view(CheckoutView(name="Checkout", endpoint='checkout', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
admin.add_view(UserRegistrationView(name="User Registration", endpoint='user_registration', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
admin.add_view(ObjectDetectionView(name="Object Detection", endpoint='obj_detection', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

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
        
        product_names = ['coca', 'coca_cola_light_05', 'avocado', 'banana_bundle', 'banana_single', 'kiwi', 'pear', 'carrot', 'cucumber', 'lettuce', 'roma_vine_tomatoes', 'zucchini']
        product_price = [2.5, 2.5, 2, 2, 0.5, 0.99, 1, 1.5, 0.5, 2.5, 3, 0.8]
        product_discount = [1]*12
        for i, product_name in enumerate(product_names):
            product = Product(product_name = product_name,
                              product_unit_price = product_price[i],
                              product_discount = product_discount[i],
                              product_code = i+1)
            db.session.add(product)
            db.session.commit()
        
                 
    return

if __name__ == '__main__':
    # Define models
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, 'app',  app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    
    # Start app
    app.run(debug=True)
    
    # from utility.mask_rcnn import MaskRCNN
    # import cv2
    
    # model = MaskRCNN()
    # for i in range(1, 9):
    #     img = cv2.imread(f"../images/{i}.jpg")
    #     # print(model.get_subtotal_text([5, 4]))
    #     img = model.detect(img)
    #     cv2.imshow("out", img)
    #     # cv2.imwrite(f"../{i}_pred.jpg", img)
    #     cv2.waitKey(0)