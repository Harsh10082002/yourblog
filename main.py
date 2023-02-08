from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, SubmitField, PasswordField
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///collections.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

# class of flask-new-blog-form
class Create_form(FlaskForm):
    title_name = StringField("Title")
    sub_title_name = StringField("Sub Title")
    image_url = StringField("Image Url")
    content = StringField("Content")
    submit = SubmitField("Submit")

# class of flask-login-form
class Login_form(FlaskForm):
    user_name = StringField("Username")
    password = PasswordField("Password")
    submit = SubmitField("Submit")

# class of database
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    posts = relationship("BlogPost", back_populates="author")

# db.create_all()

class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(250), unique=True, nullable=False)
    sub_title = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
# db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    login_form = Login_form()
    return render_template('home.html', form=login_form)

@app.route("/contact")
def contact():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["email"]
        number = request.form["number"]
        msg = request.form["message"]
        print(username, password1, number, msg)
    return render_template('contact.html')

@app.route("/bloghome")
@login_required
def bloghome():
    all_blogs = db.session.query(BlogPost).all()
    # return render_template("index.html", all_blog=all_blogs, name=name")
    # for i in all_blogs:
    #     print(i.author_id)
    #     print(current_user.id)
    return render_template("index.html", all_blog=all_blogs)

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('bloghome'))
            else:
                print('wrong pswrd')
                return redirect(url_for('home'))
        else:
            print('not having this username')
            return redirect(url_for('home'))
    return render_template('home.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        add_users = User(name=name, username=username, password=password)
        db.session.add(add_users)
        db.session.commit()

        login_user(add_users)
        return redirect(url_for('bloghome', name=name))

    return render_template("signup.html")


@app.route("/index-content/<int:id>")
def index_content(id):
    particular_blog = BlogPost.query.get(id)
    return render_template("index-content.html", all_blog=particular_blog)


@app.route("/create_blog_form", methods=["POST", "GET"])
def create_blog_form():
    create_form = Create_form()
    if create_form.is_submitted():
        title_data = create_form.title_name.data
        sub_title_data = create_form.sub_title_name.data
        image_url = create_form.image_url.data
        content = create_form.content.data

        blog_collection = BlogPost(title=title_data,
                                   sub_title=sub_title_data,
                                   url=image_url, content=content,
                                   author_id=current_user.id)
        db.session.add(blog_collection)
        db.session.commit()

        return redirect(url_for("bloghome"))
    return render_template("create_blog_form.html", form=create_form)

@app.route("/delete_blog/<int:id>")
def delete_blog(id):
    print("deleteblog",id)
    print("currentid", current_user.id)

    # blog_tables = db.session.query(BlogPost).all()
    blog_to_delete = BlogPost.query.get(id)

    # return render_template("index.html", all_blog=all_blogs, name=name")
    if current_user.id == blog_to_delete.author_id:
        blog_to_delete = BlogPost.query.get(id)
        db.session.delete(blog_to_delete)
        db.session.commit()
        return redirect(url_for("bloghome"))
    else:
        print("not have")

@app.route("/edit/<int:id>")
def edit(id):
    d = BlogPost.query.get(id)
    return redirect('create_blog_form')



if __name__ == "__main__":
    app.secret_key = "mykey"
    app.run(debug=True)