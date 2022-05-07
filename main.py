import os
import qrcode
import base64
from flask import Flask, render_template, request, url_for, jsonify
from PIL import Image
import pyzbar.pyzbar as pyzbar

import util

app = Flask(__name__)
from flask_request_id import RequestID

requestIdTool = RequestID(app)

# app.config['SERVER_NAME'] = 'flask.dev:5000'
basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/',methods=['GET'])
def hello_world():
    return render_template('index.html')

@app.route('/transToEmbed',methods=['POST'])
def transToEmbed():
    userPath = "static/userInfo/" + requestIdTool.id+'/'
    if not os.path.exists(userPath):
        os.makedirs(userPath)
    img = request.files.get('baseImg')
    file_path = userPath + img.filename
    img.save(file_path)
    print('上传图片成功', img.filename)
    text = request.form.get('text')
    print('接受到的水印信息：', text)
    # 实例化QRCode生成qr对象
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1
    )
    # 传入数据
    qr.add_data(text)
    qr.make()
    # 生成二维码
    img = qr.make_image()
    # 保存二维码
    qrcodePath = userPath + 'qrcode.png'
    img.save(qrcodePath)
    util.func_new(file_path,qrcodePath)
    return jsonify({
        "success": 200,
        "id":str(requestIdTool.id),
    })

@app.route('/transToExtraction',methods=['POST'])
def transToExtraction():
    userPath = "static/userInfo/" + requestIdTool.id + '/'
    if not os.path.exists(userPath):
        os.makedirs(userPath)
    img = request.files.get('waterMarkedImg')
    file_path = userPath + img.filename
    img.save(file_path)
    print('上传要提取水印的图片成功', img.filename)
    key = request.files.get('key')
    file_path2 = userPath + key.filename
    key.save(file_path2)
    print('上传密钥成功',key.filename)
    util.func_withdraw(file_path,file_path2)
    img = Image.open(userPath+'withdraw.png')
    barcodes = pyzbar.decode(img)
    barcodeData = ''
    for barcode in barcodes:
        barcodeData += barcode.data.decode("utf-8")
    print(barcodeData)
    return jsonify({
        "success": 200,
        "val":barcodeData,
    })

if __name__=='__main__':
    app.run()