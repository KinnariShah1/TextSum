import os
import secrets
from flask import render_template,url_for,flash,redirect,request
from app import app,db,bcrypt
app.app_context().push()
db.create_all()
from app.forms import RegistrationForm,LoginForm, UpdateAccountForm,ContactForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user,login_required

# Import your text summarization code here
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import re

# Import your text summarization code here
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize, sent_tokenize
# from nltk.probability import FreqDist


posts=[
    {
        'content':''
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',posts=posts)

# @app.route("/index")
# def index():
#     return render_template('index.html',posts=posts)

# @app.route("/about")
# def about():
#     return render_template('about.html',title='About')

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in','success')
        return redirect( url_for('login') )
    return render_template('register.html',title='Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password','danger')
    return render_template('login.html',title='Login',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file,form=form)


# @app.route('/', methods=['POST'])
# def result():
#     # form=PostSummary()
#     # text=form.content.data
#     # if form.validate_on_submit():
#     #     return redirect(url_for('home'))
#     text = request.form['text']
#     sentences = sent_tokenize(text)
#     words = word_tokenize(text)

#     # Remove stopwords
#     stop_words = set(stopwords.words('english'))
#     filtered_words = [word for word in words if not word.lower() in stop_words]

#     # Calculate word frequency
#     word_freq = nltk.FreqDist(filtered_words)

#     # Calculate sentence scores based on word frequency
#     sentence_scores = {}
#     for sentence in sentences:
#         for word in word_tokenize(sentence.lower()):
#             if word in word_freq.keys():
#                 if len(sentence.split(' ')) < 30: #30 words 
#                     if sentence not in sentence_scores.keys():
#                         sentence_scores[sentence] = word_freq[word]
#                     else:
#                         sentence_scores[sentence] += word_freq[word]

#     # Get top sentences based on scores
#     summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:3]

#     # Join the top sentences into a summary
#     summary = ' '.join(summary_sentences)
#     return render_template('home.html' , summary=summary,text=text,posts=posts)

def tokenize(text):
    sentences=[]
    sentences = nltk.sent_tokenize(text)
    unique_sentences=list(set(sentences))
    
    return unique_sentences

# Create vectors and calculate cosine similarity b/w two sentences
def ss(s1,s2,stop_words=None):
    if stop_words is None:
        stop_words=[]

    s1 = [w.lower() for w in s1]
    s2 = [w.lower() for w in s2]
    all_words = list(set(s1+s2))

    v1=[0]*len(all_words)
    v2=[0]*len(all_words)

    for w in s1:
        if not w in stop_words:
            v1[all_words.index(w)]=1+v1[all_words.index(w)]

    for w in s2:
        if not w in stop_words:
            v2[all_words.index(w)]=1+v2[all_words.index(w)]

    return 1-cosine_distance(v1,v2)

# Create similarity matrix among all sentences
def sm(sentences,stop_words):
     #create an empty similarity matrix
    similarity_matrix= np.zeros((len(sentences),len(sentences)))

    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i!=j:
                similarity_matrix[i][j]=ss(sentences[i],sentences[j],stop_words)

       
    return similarity_matrix

@app.route('/', methods=['POST'])
def result():
    text = request.form['text']
    summarize_text=[]
    sentences = tokenize(text)

    # Remove stopwords and punctuation
    stop_words = stopwords.words('english') 
   
    # Create a similarity matrix based on word overlap between sentences
    similaritymatrix = sm(sentences,stop_words)
    graph=nx.from_numpy_array(similaritymatrix)
    scores=nx.pagerank(graph)

    #Step4: sort the rank and place top sentences
    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)),reverse=True)

     # Step 5: get the top n number of sentences based on rank    
    m=len(sentences)
    n=int(0.25*m)
    for i in range(n):
        summarize_text.append(ranked_sentences[i][1])
    
    # Step 6 : outpur the summarized version
    summary= " ".join(summarize_text)
    return render_template('home.html', summary=summary,text=text,posts=posts)


@app.route("/contact", methods=['GET', 'POST'])
@login_required
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(user)
        db.session.commit()
        flash('Your query has been sent!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', title='Contact Us',form=form, legend='Contact Us')