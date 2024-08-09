from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError
from .validators import email_validator #import the customer email validation

auth = Blueprint('auth', __name__)

class RegistrationForm(Form):
    email = StringField('Email', [validators.DataRequired(), email_validator])
    first_name = StringField('First Name', [validators.DataRequired(), validators.Length(min=2, max=150)])
    last_name = StringField('Last Name', [validators.DataRequired(), validators.Length(min=2, max=150)])
    password_1 = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=7, max=150)
    ])
    password_2 = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password_1', message='Passwords must match')
    ])
    
@auth.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        try: 
            email_validator(email)
        except ValidationError as e: 
            flash(str(e), category='error')
            return render_template("sign-up.html", user=current_user)
        if user:
            if check_password_hash(user.password, password): 
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else: 
                flash('Incorrect password, try again.', category='error')
        else: 
            flash('Email does not exist!', category='error')
    
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up',methods=['GET', 'POST'])
def sign_up(): 
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate(): 
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password_1 = form.password_1.data
        
        user = User.query.filter_by(email=email).first()
        if user: 
            flash('Email already exists', category='error')
        else: 
            new_user = User(email=email, first_name = first_name, last_name = last_name, password=generate_password_hash(password_1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))
    return render_template("sign-up.html", user=current_user)