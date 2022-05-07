import pyzbar.pyzbar as pyzbar
from PIL import Image
img =Image.open('../static/withdraw_cut.png')
barcodes = pyzbar.decode(img)
for barcode in barcodes:
    barcodeData = barcode.data.decode("utf-8")
    print(barcodeData)