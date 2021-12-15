from flask import Flask, request, redirect, render_template, session, flash
import bcrypt

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body 
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'link', 'dynamic']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        if password == verify:
            if len(password) > 3:
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    new_user = User(username, hashed)
                    db.session.add(new_user)
                    db.session.commit()
                    session['usernme'] = username
                    return redirect('/blog')
                else:
                    flash('Duplicate Username')
            else:
                flash('Password must be longer than 3 characters')
        else:
            flash('Passwords do not match.')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/newpost')
def newpost():
    return render_template('blogs.html', title="Build a Blog")

@app.route('/newpost', methods=['POST'])
def add_blog():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""
        owner = User.query.filter_by(username=session['username']).first()
        if blog_title == "":
            title_error = "Please fill the title"

        if blog_body == "":
            body_error = "Please fill the title"
        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            print("\n\n\n")
            print(new_blog.id)
            print("\n\n\n")
            # blog = Blog.query.order_by(desc(Blog.id)).first()
            blog=new_blog
            return redirect(f'/individual?id={blog.id}')
        else:
            return render_template('blogs.html', title="Build a Blog", title_error= title_error, body_error= body_error, blog_title=blog_title, blog_body=blog_body)

@app.route('/blog')
def blog():

    
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blog_list.html',title="Build a Blog", blogs=blogs, users=users)

    
@app.route('/individual', methods=["GET"])
def link():
    
    id2 = request.args.get('id')
    blog = Blog.query.filter_by(id = id2).all()
    users = User.query.all()
    return render_template('individual.html', blogs = blog, users=users)

@app.route('/', methods=["GET"])
def index():
    user = User.query.all()
    return render_template('index.html', users = user)

@app.route('/blogs', methods=["GET"])
def dynamic():
    id2 = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id = id2).all()
    users = User.query.all()
    return render_template('blog_list.html', title="Specific Blogs", blogs=blogs, users=users)



if __name__ == '__main__':
    app.run()