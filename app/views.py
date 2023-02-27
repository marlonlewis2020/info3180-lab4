import os
from app import app, db, login_manager
from flask import render_template, request, redirect, send_from_directory, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html', current_user=current_user)


@app.route('/about/')
@login_required
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route("/uploads/<filename>")
@login_required
def get_image(filename):
    uploads = get_uploaded_images()
    for file, file_dir in uploads:
        if filename == file:
            return send_from_directory(file_dir, file)
    return page_not_found("Image File Not Found!")

@app.route("/files")
@login_required
def files():
    files = get_uploaded_images()
    return render_template("files.html", files=files)

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    photoForm = UploadForm()
    # Validate file upload on submit
    if photoForm.validate_on_submit() or request.method == "POST":
        photoForm.validate()
        print("****************************",photoForm.errors.keys())
        if len(photoForm.errors) == 0:
            # Get file data and save to your uploads folder
            photo = request.files['pic'] or photoForm.pic.data
            file_path = app.config['UPLOAD_FOLDER']
            file_name = secure_filename(photo.filename)
            photo.save(os.path.join(file_path,file_name))
            flash('File Saved', 'success')
            return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files
    flash_errors(photoForm)
    return render_template('upload.html', form=photoForm, error_fields=photoForm.errors.keys())


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    
    # change this to actually validate the entire form submission
    if form.validate_on_submit or request.method=="POST":
        # form.validate()
        print(form.errors.items())
        if len(form.errors) == 0:
            username = form.username.data
            password = form.password.data
            
            user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()
            if user is not None and check_password_hash(user.password, password):
                login_user(user)
                user = load_user(user.id)
                # Remember to flash a message to the user
                flash(f"%s, you've successfully logged in!" % user.first_name, "info")
                return redirect(url_for('upload'))  # The user should be redirected to the upload form instead
            flash("Invalid username or password","warning")
        flash_errors(form)
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

def get_uploaded_images():
    photos = []
    for dir, subdirs, files in os.walk(os.getcwd()+app.config['UPLOAD_FOLDER']):
        for file in files:
            photos.append([file, dir])
    return photos
            

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
