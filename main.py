import os, sys
from flask import Flask, flash, request, redirect, url_for, send_file, render_template
from werkzeug.utils import secure_filename
import logging
import bomconverter

bom = bomconverter.Convertbomfile()
sys.path.append(r"/home/pi/Documents/myprojects/module_site/module_site-main/files_upload")
UPLOAD_FOLDER = r'/home/pi/Documents/myprojects/module_site/module_site-main/files_upload'
ALLOWED_EXTENSIONS = {'html', 'xlsx', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
logging.basicConfig(filename="log.log", level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/converter', methods=['GET', 'POST'])
def upload_file():
    bomFilePath = ''
    if request.method == 'POST':
        print(request.files, request.url)
        # check if the post request has the file part
        if request.files['fileBom']:
            file = request.files['fileBom']
            render_template("main.html", text='Загружаем базу')
            bom.loadBase("/home/pi/Documents/myprojects/module_site/module_site-main/adr_base.txt")
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(file.filename, filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                stat, bomFilePath = bom.convert_cn("/home/pi/Documents/myprojects/module_site/module_site-main/files_upload/"+file.filename)
                print(bomFilePath)
                if stat:
                    return send_file(bomFilePath, as_attachment=True)
                else:
                    print(bomFilePath)
        elif (request.files['fileBomPick']) and (request.files['fileBrdPick']):
            fileBomPick = request.files['fileBomPick']
            fileBomPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileBomPick.filename))
            fileBrdPick = request.files['fileBrdPick']
            fileBrdPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileBrdPick.filename))
            try:
                fileZamPick = request.files['fileZamPick']
                fileZamPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileZamPick.filename))
                zam_file = "/home/pi/Documents/myprojects/module_site/module_site-main/files_upload/"+fileZamPick.filename
            except:
                zam_file = ''
            if request.form.get("checkDb"):
                checkdbval = True
            else:
                checkdbval = False
            bom.convertpick(checkdbval, "/home/pi/Documents/myprojects/module_site/module_site-main/files_upload/"+fileBomPick.filename, "/home/pi/Documents/myprojects/module_site/module_site-main/files_upload/"+fileBrdPick.filename, zam_file)
    return render_template("main.html", text = bomFilePath)
@app.route('/serverstats', methods=['GET', 'POST'])
def stats():
    app.logger.warning()
    app.logger.error()
    app.logger.info()
    
if __name__ == '__main__':
    app.run(debug = True)
