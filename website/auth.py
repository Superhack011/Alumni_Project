from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Member

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash("Successfully logged in!", category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash("Incorrect email or password.", category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", category='success')
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('dept')
        specialization = request.form.get('specialzation')
        batch = request.form.get('batch')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("User already exists!", category='error')
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category='error')
        elif email.find('cuk.ac.in') == -1:
            flash("You are not able to acess! Use a Valid cuk email.",category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category='error')
        else:
            new_member = Member(name=name,           
                batch=batch,             
                specialization=specialization,    
                department=department,        
                contact="N/A",           
                email=email              
            )

            try:
                db.session.add(new_member)
                db.session.flush()

                new_user = User(
                    email=email,
                    password=generate_password_hash(password1),
                    member_id=new_member.id 
                )

                db.session.add(new_user)
                db.session.commit() 

                login_user(new_user, remember=True)
                flash("Account created successfully!", category='success')
                return redirect(url_for('views.home'))

            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", category='error')

    return render_template('signup.html', user=current_user)


@auth.route('/contact',methods=['GET','POST'])
def help_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        flash('Your request has been submitted. We will get back to you soon.', 'success')

        return redirect(url_for('auth.help_us'))

    return render_template('help_desk.html',user=current_user)
