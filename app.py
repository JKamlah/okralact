### File Upload
###TODO: Training Status Query
###TODO: Trained Model Request
###TODO: Stop Training Manually (optional)

# -*- coding: utf-8 -*-
import os
import time
import hashlib

from flask import Flask, render_template, redirect, url_for, request
from flask_uploads import UploadSet, configure_uploads, ARCHIVES, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_ARCHIVES_DEST'] = os.getcwd() + '/static/data'
app.config['DOWNLOAD_MODELS_DEST'] = os.getcwd() + '/static/model'

archive_data = UploadSet('archives', ARCHIVES)
# archive_data.default_dest = app.config['UPLOADED_ARCHIVES_DEST']
configure_uploads(app, archive_data)
patch_request_class(app, size=16 * 1024 * 1024)  # set maximum file size, default is 16MB


class UploadForm(FlaskForm):
    data = FileField(validators=[FileAllowed(archive_data, u'Archives Only!'), FileRequired(u'Choose a file!')])
    submit = SubmitField(u'Upload')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('data'):
            name = hashlib.md5(('admin' + str(time.time())).encode('utf-8')).hexdigest()[:15]
            archive_data.save(filename, name=name + '.')
            print(name)
        success = True
    else:
        success = False
    return render_template('index.html', form=form, success=success)


@app.route('/manage')
def manage_file():
    files_list = os.listdir(app.config['UPLOADED_ARCHIVES_DEST'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
def open_file(filename):
    file_url = archive_data.url(filename)
    return render_template('browser.html', file_url=file_url)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = archive_data.path(filename)
    os.remove(file_path)
    return redirect(url_for('manage_file'))


if __name__ == '__main__':
    app.run(debug=True)
