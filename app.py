from flask import Flask, render_template, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "")

@app.route("/")
def index():
    return serve_page("index.html")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_page(path):
    if os.path.exists(os.path.join(static_path, path)):
        return send_from_directory(static_path, path)

    html_path = path + ".html"
    if os.path.exists(os.path.join(static_path, html_path)):
        return send_from_directory(static_path, html_path)

    return render_template("error.html", error_code=404, error_message="Страница не найдена"), 404

# error handlers

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("error.html", error_code=500, error_message="Внутренняя ошибка сервера"), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", error_code=403, error_message="Доступ запрещен"), 403

@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", error_code=400, error_message="Неверный запрос"), 400

@app.errorhandler(401)
def unauthorized(error):
    return render_template("error.html", error_code=401, error_message="Неавторизован"), 401

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error_code=404, error_message="Страница не найдена"), 404

limiter = Limiter(app, default_limits=["1/minute"])

@app.errorhandler(429)
@limiter.exempt
def too_many_requests(error):
    return render_template("error.html", error_code=429, error_message="Слишком много запросов"), 429

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return render_template("error.html", error_code=429, error_message="Превышен лимит запросов"), 429

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
