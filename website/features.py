from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import Member,User,Job, ChatMessage
import json
from datetime import datetime

features = Blueprint('features', __name__)

@features.route('/jobs',methods=['GET','POST'])
@login_required
def job_portal():
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')

        if title and company and location and description:
            new_job = Job(title=title, company=company, location=location, description=description, posted_on=datetime.utcnow())
            db.session.add(new_job)
            db.session.commit()
            flash('Job posted successfully!', 'success')
        else:
            flash('All fields are required!', 'danger')

        return redirect(url_for('features.job_portal'))

    jobs = Job.query.order_by(Job.posted_on.desc()).all()
    return render_template('job_portal.html', jobs=jobs, user=current_user)

@features.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_details.html', job=job, user = current_user)


@features.route('/chat/<int:member_id>', methods=['GET', 'POST'])
@login_required
def chat(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            new_message = ChatMessage(
                sender_id=current_user.member.id,  # Fetch from linked Member
                receiver_id=member_id,
                message=message,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_message)
            db.session.commit()
        return jsonify({"status": "success"})

    # Fetch messages between the two users
    messages = ChatMessage.query.filter(
    ((ChatMessage.sender_id == current_user.member.id) & (ChatMessage.receiver_id == member_id)) |
    ((ChatMessage.sender_id == member_id) & (ChatMessage.receiver_id == current_user.member.id))
    ).order_by(ChatMessage.timestamp.asc()).all()


    return render_template('chat.html', user=current_user, member=member, messages=messages)
