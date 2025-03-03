### Creating the bluprints
from flask import Flask, Blueprint,render_template, request, jsonify, flash, redirect, url_for
from . import db
from datetime import datetime, timedelta
from math import ceil
from flask_login import login_required, current_user
from .models import Blog,User, Events, Reviews, Project, Member,Alumni,img
import json
from .utils import allowed_file,UPLOAD_FOLDER
from .features import features
import os
from werkzeug.utils import secure_filename
import random

views = Blueprint('views',__name__)

###Create the routes 

##Home Page route
@views.route('/')
def home():
    top_reviews = db.session.query(Reviews, img.img).join(img, Reviews.member_id == img.member_id, isouter=True)\
        .order_by(Reviews.created_at.desc()).limit(4).all()

    reviews_with_images = []
    for review, member_image in top_reviews:
        reviews_with_images.append({
            "id": review.id,
            "name": review.name,
            "stars": review.stars,
            "review_text": review.review_text,
            "created_at": review.created_at,
            "member_image_path": member_image if member_image else "default_profile.jpg"
        })

    upcoming_events = Events.query.filter(Events.date >= datetime.utcnow()).order_by(Events.date.asc()).limit(5).all()

    story_blogs = Blog.query.filter(Blog.title.ilike("%story%")).order_by(Blog.created_at.desc()).all()

    selected_stories = random.sample(story_blogs, min(len(story_blogs), 4))
    return render_template(
        'about.html', 
        user=current_user, 
        reviews=reviews_with_images, 
        upcoming_events=upcoming_events,
        stories = selected_stories
    )


@views.route('/profile')
@login_required
def profile():
    user_member = current_user.member
    member_image = img.query.filter_by(member_id=user_member.id).first()

    if member_image:
        member_image_path = member_image.img 
    else:
        member_image_path = "default_profile.jpg"

    return render_template(
        'profile.html', user=current_user, member=user_member, member_image_path=member_image_path
    )


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@views.route('/editprofile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    member = current_user.member 

    if request.method == 'POST':
        member.name = request.form.get('name', member.name)
        member.batch = request.form.get('batch', member.batch)
        member.specialization = request.form.get('specialization', member.specialization)
        member.department = request.form.get('department', member.department)
        member.contact = request.form.get('contact', member.contact)
        member.email = request.form.get('email', member.email)

        if 'pic' in request.files:
         file = request.files['pic']
         if file and allowed_file(file.filename):
             filename = secure_filename(file.filename)
             file_path = os.path.join(UPLOAD_FOLDER, filename)
             file.save(file_path)
     
             relative_path = os.path.join("uploads", filename).replace("\\", "/") 
     
             existing_img = img.query.filter_by(member_id=member.id).first()
             
             if existing_img:
                 existing_img.img = relative_path 
                 existing_img.name = filename
                 existing_img.mimetype = file.mimetype 
             else:
                 new_image = img(img=relative_path, name=filename, mimetype=file.mimetype, member_id=member.id)
                 db.session.add(new_image)
             
        new_reviews = request.form.getlist('reviews')
        for review in new_reviews:
            if review.strip(): 
                member.reviews.append(Reviews(content=review, member_id=member.id))

        new_projects = request.form.getlist('projects')
        for project in new_projects:
            if project.strip():
                member.projects.append(Project(title=project, member_id=member.id))

        new_events = request.form.getlist('upcoming_events')
        for event in new_events:
            if event.strip():
                member.events.append(Events(event_name=event, member_id=member.id))

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('views.edit_profile'))

    member_image = img.query.filter_by(member_id=member.id).first()

    return render_template('editprofile.html', user=current_user, member=member, member_image=member_image)

@views.route('/Profile/<int:member_id>')
@login_required
def show_profile(member_id):
    alumni = Member.query.get_or_404(member_id)
    member_image = img.query.filter_by(member_id=alumni.id).first()

    if member_image:
        member_image_path = member_image.img 
    else:
        member_image_path = "default_profile.jpg"
    return render_template('show_member.html',user = current_user, member = alumni,features=features, member_image_path=member_image_path)


@views.route('/toggle_friend/<int:member_id>', methods=['POST'])
@login_required
def toggle_friend(member_id):
    current_member = current_user.member

    friend = Member.query.get_or_404(member_id)

    if current_member.id == friend.id:
        flash("You cannot add yourself as a friend!", category="error")
        return redirect(url_for('views.show_profile', member_id=member_id))

    if current_member.is_friend(friend):
        current_member.friends.remove(friend)
        db.session.commit()
        flash(f"Removed {friend.name} from your friends list.", category="success")
    else:
        current_member.friends.append(friend)
        db.session.commit()
        flash(f"Added {friend.name} to your friends list.", category="success")

    return redirect(url_for('views.show_profile', member_id=member_id))


@views.route('/blogs', methods=['GET', 'POST'])
@login_required
def blogs():
    search_query = request.args.get('search', '') 
    
    if search_query:
        all_blogs = Blog.query.join(Member).filter(
            (Blog.title.ilike(f'%{search_query}%')) |
            (Member.name.ilike(f'%{search_query}%'))
        ).order_by(Blog.created_at.desc()).all()
    else:
        all_blogs = Blog.query.order_by(Blog.created_at.desc()).all()

    return render_template('blog.html', user=current_user, 
                           blogs=all_blogs, search_query=search_query)

@views.route('/blog/<int:blog_id>')
@login_required
def blog_details(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog_detail.html', user=current_user, blog=blog)

@views.route('/upload_blog', methods=['GET', 'POST'])
@login_required
def upload_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Both title and content are required!', category='error')
        else:
            new_blog = Blog(title=title, content=content, author_id=current_user.member.id)
            db.session.add(new_blog)
            db.session.commit()
            flash('Blog uploaded successfully!', category='success')
            return redirect(url_for('views.blogs'))

    return render_template('upload_blog.html', user=current_user)


##Member page routing 
@views.route('/members')
@login_required
def alumni():
    current_year = datetime.now().year
    
    query = Member.query.filter(Member.batch <= current_year - 4)

    # Get filter parameters from query string
    batch_year = request.args.get('batch')
    department = request.args.get('department')
    project_work = request.args.get('project_work')

    if batch_year:
        query = query.filter(Member.batch == int(batch_year))
    if department:
        query = query.filter(Member.department.ilike(f'%{department}%'))
    if project_work:
        query = query.filter(Member.project_work.ilike(f'%{project_work}%'))

    ### Pagination Logic
    per_page = 10
    page = request.args.get('page', default=1, type=int)
    paginated_alumni = query.paginate(page=page, per_page=per_page, error_out=False)

    user_member = current_user.member

    ### Render the template with paginated data
    return render_template(
        'member.html',
        user=current_user,
        alumni=paginated_alumni.items,
        current_page=page,
        total_pages=paginated_alumni.pages,
        member=user_member
    )


@views.route('/events')
@login_required
def events_page():
    current_date = datetime.now()

    upcoming_events = Events.query.filter(Events.date > current_date).all()
    ongoing_events = Events.query.filter(
        Events.date <= current_date, 
        Events.date > (current_date - timedelta(days=7))
    ).all()
    past_events = Events.query.filter(Events.date < current_date - timedelta(days=7)).all()

    return render_template(
        'event.html', user=current_user,upcoming_events=upcoming_events, ongoing_events=ongoing_events, past_events=past_events)

@views.route('/events/addEvent',methods=['GET','POST'])
@login_required
def add_event():
    if request.method == 'POST':
        name = request.form.get('event_name')
        date = request.form.get('event_date')
        description = request.form.get('event_description')
        location = request.form.get('event_location')
        organizer = current_user.member.name

        if not name or not date or not location :
            flash("Name, Date and location must be require.!","danger")
            return redirect(url_for('views.add_event'))
        
        try:
            date = datetime.strptime(date, '%Y-%m-%d')  ###format: YYYY-MM-DD
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('views.add_event'))
        
        new_event = Events(title = name, location = location,
                           date = date, description = description, 
                           organizer=organizer, member_id=current_user.id)
        
        db.session.add(new_event)
        db.session.commit()
        flash("Event added succesfully!")
        return redirect(url_for('views.events_page'))
    
    return render_template('event.html',user=current_user)


@views.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Events.query.get(event_id)
    
    if not event:
        return "Event not found", 404

    return render_template('eventsdetail.html', event=event,user=current_user)


import random

##About Us page route
@views.route('/about')
def aboutus():
    story_blogs = Blog.query.filter(Blog.title.ilike("%story%")).order_by(Blog.created_at.desc()).all()

    selected_stories = random.sample(story_blogs, min(len(story_blogs), 4))

    return render_template('aboutuspage.html', user=current_user, stories=selected_stories)


@views.route('/reviews')
@login_required
def reviews():
    page = request.args.get('page', 1, type=int) 

    if request.method == 'POST':
        ### Get data from the form
        member_id = request.form.get('member_id')  
        stars = request.form.get('stars')
        review_text = request.form.get('review_text')

        member = Member.query.get(int(member_id))

        if not stars or not review_text:
            flash("Both stars and review text are required!", "danger")
            return redirect(url_for('views.reviews'))

        # Add the new review
        new_review = Reviews(
            stars=int(stars),
            review_text=review_text,
            member_id=int(member_id),
            name=member.name
        )
        db.session.add(new_review)
        db.session.commit()
        flash("Review added successfully!", "success")
        return redirect(url_for('views.reviews'))

    reviews_paginated = db.session.query(Reviews, img.img).join(img, Reviews.member_id == img.member_id, isouter=True)\
        .order_by(Reviews.created_at.desc()).paginate(page=page, per_page=5)

    reviews_with_images = []
    for review, member_image in reviews_paginated.items:
        reviews_with_images.append({
            "id": review.id,
            "name": review.name,
            "stars": review.stars,
            "review_text": review.review_text,
            "created_at": review.created_at,
            "member_image_path": member_image if member_image else "default_profile.jpg"
        })

    return render_template('reviews.html', 
                           reviews=reviews_with_images,
                           user=current_user, 
                           pagination=reviews_paginated)


@views.route('/load_reviews', methods=['GET'])
def load_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    reviews_paginated = Reviews.query.order_by(Reviews.created_at.desc()).paginate(page=page, per_page=per_page)

    reviews_data = []
    for review in reviews_paginated.items:
        member_image = img.query.filter_by(member_id=review.member_id).first()
        member_image_path = member_image.img if member_image else "default_profile.jpg"

        reviews_data.append({
            "name": review.name,
            "stars": review.stars,
            "review_text": review.review_text,
            "created_at": review.created_at.strftime('%Y-%m-%d'),
            "member_image_path": member_image_path
        })

    return jsonify({"reviews": reviews_data})

@views.route('/resources', methods=['GET'])
@login_required
def resources_page():
    page = request.args.get('page', 1, type=int)
    items_per_page = 10

    total_items = Project.query.count()
    total_pages = ceil(total_items / items_per_page)

    projects = Project.query.order_by(Project.id).offset((page - 1) * items_per_page).limit(items_per_page).all()

    return render_template('resource.html', projects=projects, page=page, total_pages=total_pages, user=current_user)


@views.route('/resources/addProject', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        description = request.form.get('description')
        technologies = request.form.get('technologies')
        duration = request.form.get('duration')
        lead = request.form.get('lead')
        team_members = request.form.get('team_members')
        member_id = current_user.id

        if not project_name or not description or not technologies or not duration:
            flash("All required fields must be filled out.", "danger")
            return redirect(url_for('views.add_project'))

        new_project = Project(
            project_name=project_name,
            description=description,
            technologies=technologies,
            duration=duration,
            lead=lead,
            team_members=team_members,
            member_id=member_id
        )

        db.session.add(new_project)
        db.session.commit()

        flash("Project added successfully!", "success")
        return redirect(url_for('views.resources_page')) 

    return render_template('add_project.html',user=current_user)


@views.route('/resources/<int:project_id>', methods=['GET'])
def project_details(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_details.html', project=project,user=current_user)


@views.route('/alumni', methods=['GET'])
@login_required
def alumnis():
    batch = request.args.get('batch', '')
    department = request.args.get('department', '')
    project_work = request.args.get('project_work', '')

    ###Build the query based on the search filters
    alumni_query = Alumni.query
    if batch:
        alumni_query = alumni_query.filter(Alumni.batch.ilike(f'%{batch}%'))
    if department:
        alumni_query = alumni_query.filter(Alumni.department.ilike(f'%{department}%'))
    if project_work:
        alumni_query = alumni_query.filter(Alumni.project_work.ilike(f'%{project_work}%'))

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    pagination = alumni_query.paginate(page=page, per_page=10)
    alumni = pagination.items
    total_pages = pagination.pages
    current_page = pagination.page

    return render_template('alumni.html', alumni=alumni, total_pages=total_pages, current_page=current_page,user=current_user)

@views.route('/alumni/profile/<int:member_id>', methods=['GET'])
def show_profiles(member_id):
    alumni_member = Alumni.query.get_or_404(member_id)
    return render_template('show_member.html', member=alumni_member,user=current_user,features=features)

