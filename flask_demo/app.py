from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = "demo123"

USERS = [{"username": "admin", "password": "123456"}]

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        for user in USERS:
            if user["username"] == u and user["password"] == p:
                return redirect("/dashboard")
        flash("登录失败")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        USERS.append({
            "username": request.form["username"],
            "password": request.form["password"]
        })
        flash("注册成功")
        return redirect("/login")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/users")
def users():
    return render_template("users.html", users=USERS)

@app.route("/delete/<name>")
def delete(name):
    global USERS
    USERS = [u for u in USERS if u["username"] != name]
    flash("删除成功")
    return redirect("/users")

@app.route("/iframe")
def iframe():
    return render_template("iframe.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        path = os.path.join("uploads", f.filename)
        os.makedirs("uploads", exist_ok=True)
        f.save(path)
        flash("上传成功")
    return render_template("upload.html")

@app.route("/alert")
def alert():
    return "<script>alert('这是一个JS弹窗')</script>"

if __name__ == "__main__":
    app.run(debug=True)
