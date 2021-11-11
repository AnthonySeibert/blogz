from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog2:GKA0jISGERlsHNDy@localhost:8889/build-a-blog2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body 

@app.route('/add-blog')
def index():
    return render_template('blogs.html', title="Build a Blog")

@app.route('/add-blog', methods=['POST'])
def add_blog():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""
        if blog_title == "":
            title_error = "Please fill the title"

        if blog_body == "":
            body_error = "Please fill the title"
        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
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
    return render_template('blog_list.html',title="Build a Blog", blogs=blogs)

@app.route('/individual', methods=["GET"])
def link():
    
    id2 = request.args.get('id')
    blog = Blog.query.filter_by(id = id2).all()
    return render_template('individual.html', blogs = blog)


if __name__ == '__main__':
    app.run()