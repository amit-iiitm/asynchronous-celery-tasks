import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import foo
app= Flask(__name__)




# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'csvfiles/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


APP_ROOT= os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
	return render_template("upload.html")

@app.route("/upload", methods=['POST'])

def upload():
	# Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
	# target=os.path.join(APP_ROOT,"images/")
	# print (target)
	# if not os.path.isdir(target):
	# 	os.mkdir(target)

	# for file in request.files.getlist("file"):
	# 	print file
	# 	filename=file.filename
	# 	destination ="/".join([target,filename])
	# 	print destination
	# 	file.save(destination)
	return render_template("complete.html")


@app.route("/task",methods=["POST"])
def task_do():
    if request.method == 'POST':
        if request.form['submit'] == 'start_a_long_process':
            print 'long task running'
            foo.foo(1,1000000)
            # out=foo.foo(1,1000)
            # print out
   
    return render_template('task_complete.html')

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("6379"),
        debug=True
    )


