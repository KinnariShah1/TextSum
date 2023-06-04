from app import db,login_manager
from flask import Flask
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

app = Flask(__name__)

class User(db.Model, UserMixin):
        id=db.Column(db.Integer,primary_key=True)
        username=db.Column(db.String(20),nullable=False,unique=True)
        email=db.Column(db.String(120),nullable=False,unique=True)
        image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
        password=db.Column(db.String(60),nullable=False)
        #posts=db.relationship('Post',backref='author',lazy=True)

    #     # date_created=db.Column(db.DateTime,default=datetime.utcnow)

        def __repr__(self):
            return f"User('{self.username}','{self.email}','{self.image_file}')"

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    content=db.Column(db.Text, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return f"Post('{self.content}')"
    
# with app.app_context():
#      db.create_all()