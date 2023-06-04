
from app import app
# from flask import Flask

# app = Flask(__name__)


# @app.route('/',methods=['POST','GET'])
# def index():
#     if request.method=='POST':
#         task_content=request.form['content']
#         new_task=Todo(content=task_content)

#         try:
#             db.session.add(new_task)
#             db.session.commit()
#             return redirect('/')

#         except:
#             return 'There is an issue'
#     else:
#         tasks= Todo.query.order.by(Todo.date_created).all()
#         return render_template('home.html',tasks=tasks)
#     #  else:
#     # #    tasks= Todo.query.order.by(Todo.date_created).all()
#     #      return render_template('home.html',tasks=tasks)
# #@app.route("/home")
# #@app.route("/home")
# # def home():
# #     return render_template('home.html')

# #@app.route("/about")
# #@app.route("/home")
# #def about():
#     #return "<h1>About Page!</h1>"


# if __name__== '__main__':
#     app.run(debug=True)

# if __name__== '__main__':
#     with app.app_context():


if __name__== '__main__':
    app.run(debug=True)
    