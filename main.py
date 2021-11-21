import os, sys
from flask import Flask, flash, request, redirect, url_for, send_file, render_template
from werkzeug.utils import secure_filename
import logging
import bomconverter
from tutocn import convert as tutocn
import configparser

config = configparser.ConfigParser()
config.read("/home/alex/Документы/myprojects/module_site/config_linux.ini")
path_eri = config["BASE_PATH"]["eri_base"]
path_con = config["BASE_PATH"]["connector_base"]
path_upload_folder = config["PROJECT_PATH"]["file_upload_folder"]
path_log = config["PROJECT_PATH"]["log_file"]

bom = bomconverter.Convertbomfile()
sys.path.append(path_upload_folder)
UPLOAD_FOLDER = path_upload_folder
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
            render_template("bomfileconverter.html", text='Загружаем базу')
            bom.loadBase(path_eri, path_con)
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(file.filename, filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                stat, bomFilePath = bom.convert_cn(path_upload_folder+file.filename)
                print(bomFilePath)
                if stat:
                    render_template("success.html")
                    return send_file(bomFilePath, as_attachment=True)
                else:
                    print(bomFilePath)
    return render_template("bomfileconverter.html", text = bomFilePath)

@app.route('/pickandplace', methods=['GET', 'POST'])
def pickandplace():
    if request.method == 'POST':
        print(request.files, request.url)
        if (request.files['fileBomPick']) and (request.files['fileBrdPick']):
            fileBomPick = request.files['fileBomPick']
            fileBomPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileBomPick.filename))
            fileBrdPick = request.files['fileBrdPick']
            fileBrdPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileBrdPick.filename))
            try:
                fileZamPick = request.files['fileZamPick']
                fileZamPick.save(os.path.join(app.config['UPLOAD_FOLDER'], fileZamPick.filename))
                zam_file = path_upload_folder+fileZamPick.filename
            except:
                zam_file = ''
            if request.form.get("checkDb"):
                checkdbval = True
            else:
                checkdbval = False
            bom.convertpick(checkdbval, path_upload_folder+fileBomPick.filename, path_upload_folder+fileBrdPick.filename, zam_file)
    return render_template("pickandplace.html")
@app.route('/start', methods=['GET', 'POST'])
def start():
    print('start')
    return render_template("index.html")

@app.route('/cadencename', methods=['GET', 'POST'])
def cadencename():
    print('start')
    return render_template("cadencename.html")

@app.route('/serverstats', methods=['GET', 'POST'])
def stats():
    app.logger.warning()
    app.logger.error()
    app.logger.info()

@app.route('/success')
def success():
   return render_template("success.html")
    
if __name__ == '__main__':
    app.run(debug = True)
    print(tutocn("ddss"))
