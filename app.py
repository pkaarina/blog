from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    Response,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://blog:blog@localhost/blogdb"
app.config["SECRET_KEY"] = "chave_secreta"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="post", cascade="all, delete-orphan")
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/")
def index():
    user_id = session.get("user_id")

    if user_id == None:
        return redirect(url_for("login"))

    posts = Post.query.all()
    comments_count = {
        post.id: Comment.query.filter_by(post_id=post.id).count() for post in posts
    }
    users = {user.id: user.username for user in User.query.all()}

    enriched_posts = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "comments_amount": comments_count.get(post.id, 0),
            "created_by_username": users.get(post.user_id, "Usuário desconhecido"),
        }
        for post in posts
    ]

    return render_template("home.html", posts=enriched_posts)

@app.route("/posts", methods=["GET", "POST"])
def posts():
    categories = Category.query.all()
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category_id = request.form["category"]
        post = Post(
            title=title,
            content=content,
            category_id=category_id,
            user_id=session["user_id"],
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("posts.html", categories=categories)

@app.route("/post/<int:post_id>", methods=["GET"])
def post_details(post_id):
    user_id = session.get("user_id")

    if user_id == None:
        return redirect(url_for("login"))

    post = Post.query.get(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    users = {user.id: user.username for user in User.query.all()}

    enriched_comments = [
        {
            "id": comment.id,
            "content": comment.content,
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "user_name": users.get(comment.user_id, "Usuário desconhecido"),
        }
        for comment in comments
    ]

    if request.method == "POST" and "user_id" in session:
        content = request.form["content"]
        comment = Comment(content=content, post_id=post_id, user_id=session["user_id"])
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post", post_id=post_id))
    return render_template("post_details.html", post=post, comments=enriched_comments)

@app.route("/post/<int:post_id>/comments", methods=["POST"])
def save_comments(post_id):
    content = request.form["comment"]
    comment = Comment(content=content, post_id=post_id, user_id=session["user_id"])
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for("post_details", post_id=post_id))

@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        flash("Post não encontrado.", "danger")
        return redirect(url_for("home"))

    user_id = session.get("user_id")  # Obtém o ID do usuário autenticado
    print(f"Usuário autenticado: {user_id}, Autor do post: {post.user_id}")  # Debug

    if user_id is None or post.user_id != user_id:
        flash("Não é permitido excluir um post que não criou.", "danger")
        return redirect(url_for("home"))  # Retorna direto sem mostrar a confirmação

    Comment.query.filter_by(post_id=post_id).delete()

    db.session.delete(post)
    db.session.commit()

    flash("Post excluído com sucesso!", "success")
    return redirect(url_for("home"))

@app.route("/category/<int:category_id>")
def category(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=category_id).all()

    enriched_posts = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "comments_amount": Comment.query.filter_by(post_id=post.id).count(),
            "created_by_username": User.query.get(post.user_id).username,
        }
        for post in posts
    ]
    return render_template("category.html", category=category, posts=enriched_posts)

@app.route("/criar-post/<int:category_id>", methods=["GET", "POST"])
def create_post(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        new_post = Post(title=title, content=content, category_id=category.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(f"categoria/{category.id}")
    return render_template("create_post.html", category=category)

if __name__ == "__main__":
    with app.app_context():  
        categories = ["True Crime", "Fanfics", "Autorais"]
        for name in categories:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
                db.session.commit()
                print("Categorias adicionadas com sucesso!")
    app.run(debug=True)