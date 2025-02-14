from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from datetime import datetime
import json

# Association table for friendship (Self-referential relationship)
friends_association = db.Table(
    'friends',
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('member.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

    # Relationship to Member
    member = db.relationship('Member', backref=db.backref('user', uselist=False))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True,default="User")
    batch = db.Column(db.String(50), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(255), default='default.jpg')
    contact = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    achievements = db.Column(db.Text, nullable=True,default="NONE")
    experiences = db.Column(db.Text, nullable=True,default="NONE") 
    hobbies = db.Column(db.Text, nullable=True,default="NONE")   

    reviews = db.relationship('Reviews', backref='member', lazy=True, cascade="all, delete")
    projects = db.relationship('Project', backref='member', lazy=True)
    events = db.relationship('Events', backref='member', lazy=True)

    Profile_pic = db.relationship('img',backref='member',lazy=True)

    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='message_sender', lazy=True, cascade="all, delete")
    received_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.receiver_id', backref='message_receiver', lazy=True, cascade="all, delete")

    # Self-referential relationship for friends (many-to-many relationship)
    friends = db.relationship(
        'Member',
        secondary=friends_association,
        primaryjoin=(friends_association.c.member_id == id),
        secondaryjoin=(friends_association.c.friend_id == id),
        backref='friend_of',
        lazy='dynamic'
    )

    def get_list(self, field):
        """Convert a JSON-encoded field to a Python list."""
        field_value = getattr(self, field, "[]")  # Get the field value or use an empty list as default
        if not field_value:  # If field_value is None or empty string, return an empty list
            return []
        try:
            return json.loads(field_value)  # Try parsing the JSON data
        except json.JSONDecodeError:
            return []  # Return an empty list if the JSON is invalid

    def is_friend(self, friend):
        return self.friends.filter_by(id=friend.id).count() > 0

    def toggle_friend(self, friend):
        if self.is_friend(friend):
            self.friends.remove(friend)
            return False  # Removed from friends
        else:
            self.friends.append(friend)
            return True  # Added as a friend

    def get_friends(self):
        """Return a list of all friends."""
        return self.friends.all()
    
class ChatMessage(db.Model):
    __tablename__ = 'chat_message'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('Member', foreign_keys=[sender_id], backref="messages_sent", overlaps="messages_sent,message_sender,sent_messages")
    receiver = db.relationship('Member', foreign_keys=[receiver_id], backref="messages_received", overlaps="messages_received,message_receiver,received_messages")



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

    # Relationship with Member
    author = db.relationship('Member', backref='blogs')

    def __repr__(self):
        return f"<Blog {self.title} by {self.author.name}>"

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(1024), nullable=True, default="N/A")
    organizer = db.Column(db.String(255), nullable=True, default="N/A")
    contact = db.Column(db.String(255), nullable=True, default="N/A")

    member_id = db.Column(db.Integer,db.ForeignKey('member.id'),nullable=False)

class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member_id = db.Column(db.Integer,db.ForeignKey('member.id'),nullable=False)

    # member = db.relationship('Member', backref='reviews')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    lead = db.Column(db.String(100), nullable=True)
    team_members = db.Column(db.String(255), nullable=True)

    member_id = db.Column(db.Integer,db.ForeignKey('member.id'),nullable=False)



class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    Reg_no = db.Column(db.String(50),nullable=False)
    batch = db.Column(db.String(10), nullable=True)
    contact = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    department = db.Column(db.String(100), nullable=True)
    project_work = db.Column(db.String(255), nullable=True, default="N/A")
    achievements = db.Column(db.Text, nullable=True,default="NONE")
    experiences = db.Column(db.Text, nullable=True,default="NONE") 
    hobbies = db.Column(db.Text, nullable=True,default="NONE")

    def __repr__(self):
        return f"<Alumni {self.name}>"
    
    def get_list(self, field):
        #Convert the field's text into a list of items by splitting.
        content = getattr(self, field)
        if content and content != "NONE":
            return content.split("\n")
        return []


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_on = db.Column(db.DateTime, nullable=False)

class img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text,nullable=False)
    mimetype = db.Column(db.Text,nullable=False)

    member_id = db.Column(db.Integer,db.ForeignKey('member.id'),nullable=False)

