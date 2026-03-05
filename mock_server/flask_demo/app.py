from flask import Flask, render_template, request, redirect, flash, jsonify
import os

app = Flask(__name__)
app.secret_key = "demo123"

# 用 list 模拟数据库
USERS = [{"username": "admin", "password": "123456"}]


@app.route("/")
def index():
    return redirect("/login")


# ========== UI ==========
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        for user in USERS:
            if user["username"] == u and user["password"] == p:
                return redirect("/dashboard")
        flash("登录失败")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
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
def users_page():
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


@app.route("/upload", methods=["GET", "POST"])
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


# ========== API ==========
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "no json data"}), 400

    username = data.get("username")
    password = data.get("password")

    for u in USERS:
        if u["username"] == username and u["password"] == password:
            return jsonify({"msg": "login success"}), 200

    return jsonify({"msg": "login failed"}), 401


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "no json data"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "missing param"}), 400

    USERS.append({"username": username, "password": password})
    return jsonify({"msg": "register success"}), 200


@app.route("/api/users")
def api_users():
    return jsonify({"users": [u["username"] for u in USERS]}), 200


@app.route("/api/delete/<username>")
def api_delete(username):
    global USERS
    before = len(USERS)
    USERS = [u for u in USERS if u["username"] != username]

    if len(USERS) < before:
        return jsonify({"msg": "delete success"}), 200
    return jsonify({"msg": "user not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)