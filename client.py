import os
import random
import time
from flask import Flask, request, render_template, session, flash, redirect,url_for, jsonify
from werkzeug import secure_filename
from flask.ext.mail import Mail, Message
from celery import Celery
app=Flask(__name__)

app.config['SECRET_KEY'] = 'top-secret!'
#setup config for celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'flask@example.com'

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'csvfiles/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


APP_ROOT= os.path.dirname(os.path.abspath(__file__))




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    # send the email
    msg = Message('Hello from Flask',
                  recipients=[request.form['email']])
    msg.body = 'This is a test email sent from a background Celery task.'
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(msg)
        flash('Sending email to {0}'.format(email))
    else:
        # send in one minute
        send_async_email.apply_async(args=[msg], countdown=60)
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('index'))

#route to handle the file upload
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

@celery.task(bind=True)
def long_task(self,arg1,arg2):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    print "inside long task"
    print arg1, arg2
    """
    print "arguments submitted to long task"
    print arg1, arg2
    result=arg1+arg2"""
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': arg1+arg2}

@celery.task(bind=True)
def my_background_task(self,arg1, arg2):
	# some long running task here
	print "inside dummy function"
	print arg1, arg2
	return arg1+arg2

@app.route('/longtask', methods=['POST','GET'])
def longtask():
	#res=my_background_task.s(12,14).apply_async()
	#print res
	
	"""form=request.form
	arg1=int(form["arg1"])
	arg2=int(form["arg2"])
	print "printing the arguments for longtask"
	print arg1, arg2
	print type(arg1)"""
	task=long_task.s(1,2).apply_async()
	print "in longtask handler"
	return jsonify({}), 202, {'Location':url_for('taskstatus', task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        #job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
