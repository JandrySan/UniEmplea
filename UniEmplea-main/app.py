from flask import Flask, redirect, render_template, url_for
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.director_routes import director_bp
from routes.estudiante_routes import estudiante_bp
from routes.decano_routes import decano_bp


app = Flask(__name__)
app.secret_key = "uniemplea_secret"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(decano_bp)
app.register_blueprint(director_bp, url_prefix="/director")
app.register_blueprint(estudiante_bp, url_prefix="/estudiante")




@app.route("/")
def home():
    return render_template("dashboards/login.html")





if __name__ == "__main__":
    app.run(debug=True)
