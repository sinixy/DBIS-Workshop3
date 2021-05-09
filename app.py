from flask import Flask, flash, session, render_template, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:nanidafuq56@localhost:5432/lab3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y8F"F4#8z\n\xec]/'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):

	uid = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(128), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	blogposts = db.relationship('BlogPost', backref='user_post', passive_deletes=True)
	comments = db.relationship('Comment', backref='user_comment', passive_deletes=True)

	def __repr__(self):
		return f'<User {self.uid}>'


class BlogPost(db.Model):
	blogid = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)
	title = db.Column(db.String(128), nullable=False)
	text = db.Column(db.Text, nullable=False)
	date = db.Column(db.DateTime, default=datetime.now)
	comments = db.relationship('Comment', backref='blogpost', passive_deletes=True)

	def __repr__(self):
		return f'<BlogPost {self.blogid}>'


class Comment(db.Model):
	comid = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.Text, nullable=False)
	date = db.Column(db.DateTime, default=datetime.now)
	blog = db.Column(db.Integer, db.ForeignKey(BlogPost.blogid, ondelete="CASCADE"), nullable=False)
	user = db.Column(db.Integer, db.ForeignKey(User.uid, ondelete="CASCADE"), nullable=False)

	def __repr__(self):
		return f'<Comment {self.comid}>'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['uid'] is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
	return render_template('home.html')


@app.route('/signup', methods=('GET', 'POST'))
def signup():
	if request.method == 'POST':
		email = request.form['email']
		login = request.form['login']
		password = request.form['password']
		password_repeat = request.form['password-repeat']
		valid = True

		if password != password_repeat:
			flash('Pass dame')
			valid = False

		user_login = User.query.filter_by(login=login).first()
		user_email = User.query.filter_by(email=email).first()
		if user_login:
			flash('Login dame')
			valid = False
		if user_email:
			flash('Email dame')
			valid = False

		if valid:
			new_user = User(login=login, password=password, email=email)
			db.session.add(new_user)
			db.session.commit()
			flash('Success!')

		return render_template('signup.html')
	else:
		return render_template('signup.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		login = request.form['login']
		password = request.form['password']
		user = User.query.filter_by(login=login, password=password).first()
		if user:
			session['uid'] = user.uid
			session['username'] = login
			return redirect('/')
		else:
			flash('Invalid login or password!')
			return render_template('login.html')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('uid', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/profile/<int:profid>')
def profile(profid):
	user = User.query.get_or_404(profid)
	blogs = BlogPost.query.filter_by(author=profid)
	return render_template('profile.html', user=user, blogs=blogs)


@app.route('/blog')
def blog_listing():
	blogs = BlogPost.query.all()
	return render_template('blog_listing.html', blogs=blogs)


@app.route('/blog/<int:blogid>')
def blog_index(blogid):
	blog = BlogPost.query.get_or_404(blogid)
	comments = Comment.query.filter_by(blog=blogid)
	return render_template('blog.html', blog=blog, comments=comments)


@app.route('/create-blog', methods=['GET', 'POST'])
@login_required
def create_blog():
	if request.method == 'POST':

		title = request.form['title']
		text = request.form['text']
		author = User.query.get_or_404(session['uid'])
		new_blogpost = BlogPost(title=title, text=text, author=author.uid)
		db.session.add(new_blogpost)
		db.session.commit()
		return redirect(f'/blog/{new_blogpost.blogid}')

	else:
		return render_template('create_blog.html')

@app.route('/blog/<int:blogid>/add-comment', methods=['GET', 'POST'])
@login_required
def add_comment(blogid):
	if request.method == 'POST':
		author = User.query.get_or_404(session['uid'])
		blog = BlogPost.query.get_or_404(blogid)
		text = request.form['text']
		new_comment = Comment(text=text, blog=blog.blogid, user=author.uid)
		db.session.add(new_comment)
		db.session.commit()
	return redirect(f'/blog/{blogid}')


@app.route('/profile/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
def profile_update(uid):
	user = User.query.get_or_404(uid)
	if session['uid'] != uid and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	if request.method == 'POST':
		login = request.form['login']
		password = request.form['password']
		email = request.form['email']

		user.login = login
		user.password = password
		user.email = email
		
		db.session.commit()
		return redirect(f'/profile/{uid}')
	else:
		return render_template('user_update.html', user=user)


@app.route('/blog/<int:blogid>/edit', methods=['GET', 'POST'])
@login_required
def blog_update(blogid):
	blog = BlogPost.query.get_or_404(blogid)
	if session['uid'] != blog.author and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	if request.method == 'POST':
		blog.title = request.form['title']
		blog.text = request.form['text']
		if 'author' in request.form:
			author = User.query.get_or_404(request.form['author'])
			blog.author = request.form['author']
			date = request.form['date']
			if date:
				blog.date = date
		
		db.session.commit()
		return redirect(f'/blog/{blogid}')
	else:
		users = User.query.all()
		return render_template('blogpost_update.html', users=users, blog=blog)


@app.route('/comment/<int:comid>/edit', methods=['GET', 'POST'])
@login_required
def comment_edit(comid):
	comment = Comment.query.get_or_404(comid)
	blog = BlogPost.query.get_or_404(comment.blog)
	if session['uid'] != comment.user and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	if request.method == 'POST':
		comment.text = request.form['text']
		if 'user' in request.form:
			user = User.query.get_or_404(request.form['user'])
			blog = BlogPost.query.get_or_404(request.form['blog'])
			comment.user = user.uid
			comment.blog = blog.blogid
			date = request.form['date']
			if date:
				comment.date = date
			
		db.session.commit()
		return redirect(f'/blog/{blog.blogid}')
	else:
		users = User.query.all()
		blogs = BlogPost.query.all()
		return render_template('comment_update.html', users=users, blogs=blogs, comment=comment)


def entry_delete(entry):
	db.session.delete(entry)
	db.session.commit()

@app.route('/profile/<int:uid>/delete')
@login_required
def user_delete(uid):
	user = User.query.get_or_404(uid)
	if session['uid'] != uid and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	entry_delete(user)
	return redirect('/')

@app.route('/blog/<int:blogid>/delete')
@login_required
def blog_delete(blogid):
	blog = BlogPost.query.get_or_404(blogid)
	if session['uid'] != blog.author and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	entry_delete(blog)
	return redirect('/')

@app.route('/comment/<int:comid>/delete')
@login_required
def comment_delete(comid):
	comment = Comment.query.get_or_404(comid)
	if session['uid'] != comment.user and session['username'] != 'admin':
		return render_template('error.html', error="Access denied!")
	blog = comment.blog
	entry_delete(comment)
	return redirect(f'/blog/{blog}')


@app.template_filter('get_user')
def get_user_filter(uid):
	user = User.query.get_or_404(uid)
	return user

@app.template_filter('get_description')
def get_description(text):
	words = text.split(' ')
	if len(words) < 20:
		return ' '.join(words) + '...'
	return ' '.join(words[:20]) + '...'

if __name__ == "__main__":
	app.run(debug=True)