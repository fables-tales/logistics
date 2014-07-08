import subprocess
import os
import tempfile
import json
import uuid

from shutil import move

from flask import Flask, render_template, request, session, flash, redirect

app = Flask(__name__)
def base_path():
    return os.path.dirname(os.path.abspath(__file__))

def copy_for(event):
    return json.loads(open(os.path.join(base_path(), "strings.json")).read())[event]


@app.route("/")
def index():
    rendered = render_template("index.html")
    if "zip_url" in session:
        del session["zip_url"]
    return rendered


@app.route("/export", methods=["POST"])
def export_project():
    git_url = request.form["git_url"]
    dir_to_work_in = tempfile.mkdtemp()
    user_code_dir = os.path.join(dir_to_work_in, "user_code")

    wanted_return_type = request.accept_mimetypes.best_match(["application/json", "text/html", "text/plain"])

    try:
        subprocess.check_call(["git", "clone", git_url, user_code_dir])
    except Exception as e:
        if wanted_return_type == "text/html":
            flash(copy_for("EXPORT_FAIL"), "failure")
            return redirect("/")
        elif wanted_return_type == "text/json":
            return json.dumps({"errors": ["EXPORT_FAIL"]}), 400
        else:
            return "EXPORT_FAIL", 400


    zip_path = os.path.join(dir_to_work_in, "robot.zip")

    subprocess.check_call(["./pyenv/make-zip", "--no-strip", "--remove-gunk", user_code_dir, zip_path])

    zip_url = os.path.join("static", "zips", str(uuid.uuid4()), "robot.zip")
    static_zip_path = os.path.join(base_path(), zip_url)

    os.makedirs(os.path.dirname(static_zip_path))


    move(zip_path, static_zip_path)

    if wanted_return_type == "text/html":
        flash(copy_for("EXPORT_SUCCESS"), "success")
        session["zip_url"] = "/%s" % (zip_url,)
        return redirect("/")
    elif wanted_return_type == "text/json":
        return json.dumps({"zip_url": zip_url})
    else:
        return zip_url

app.secret_key = 'qowiefjqwoeifjqeoirgjasodfjasidofpqjwefioqwjef'

if __name__ == "__main__":
    app.debug = True
    app.run()
