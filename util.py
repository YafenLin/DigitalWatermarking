from PIL import Image, ImageDraw, ImageFont,ImageTk
import math
import cv2
import os

# 从0，0开始嵌入 判断原图和像素和水印的像素是否一致，如果一致 就不修改。如果不一致，将水印信息二值化，嵌入原图r通道的最后一位。
# 同时创建0，1的库  0表示没修改 1表示修改了  作为密钥返回

# ww = 0
# hh = 0
# arr = []
# 动态改变

def to_bytes(data):    #data为字符串
    b = bytearray()      #使用bytearray存储转换结果
    end_length = len(data) % 8      #获取最后不足8位的长度
    l = len(data)
    print('l:',l,'end:',end_length)
    for i in range(0, l - end_length, 8):
        b.append(int(data[i:i + 8], 2))    #通过附加参数‘2’使用int函数处理8位字符串
    if end_length != 0:
        b.append(int(data[len(data) - end_length:len(data)], 2))  # 写入最后不足8位的二进制
        b.append(int(bin(end_length), 2))  # 写入最后字节有效二进制的长度
    else:
        b.append(int(bin(0),2))
        b.append(int(bin(0),2))
    return bytes(b)    #返回bytearray

def func_new(baseImg, watermark):
    (userPath, filename) = os.path.split(baseImg)
    # E:/folder t2333.py
    print('开始嵌入水印信息')
    baseImg = Image.open(baseImg)
    watermark = Image.open(watermark)
    watermark_w = watermark.size[0]
    watermark_h = watermark.size[1]
    # 这里是 在原图中截取水印长度的像素比较
    arr = []
    for w in range(0,watermark_w):
        for h in range(0,watermark_h):
            b_pixel = baseImg.getpixel((w,h))
            b_r = b_pixel[0]
            b_g = b_pixel[1]
            b_b = b_pixel[2]
            # print('载体图像的pixel rgb:')
            # print(b_pixel)
            w_pixel = watermark.getpixel((w,h))
            if w_pixel==255:
                if  b_r == 255 & b_g == 255 & b_b == 255:
                    arr.append('0')
                else:
                    arr.append('1')
                    b_r = b_r - b_r % 2
            else:
                if b_r == 255 & b_g == 255 & b_b == 255:
                    arr.append('1')
                    b_r = b_r - b_r % 2 + 1
                else:
                    arr.append('0')
            baseImg.putpixel((w, h), (b_r, b_g, b_b))
    watermarkedImgPath = userPath + '/'+'watermarked.png'
    baseImg.save(watermarkedImgPath)
    s = "".join(arr)
    bin_file = open(userPath + '/key.bin', mode='wb')
    bin_file.write(to_bytes(s))
    bin_file.close()
    print('嵌入水印信息成功，嵌入后的图片保存为'+watermarkedImgPath + '\n嵌入后的密钥保存为'+userPath+'/key.bin')


# 新算法的提取
def func_withdraw(baseImg,key):
    (userPath, filename) = os.path.split(baseImg)
    baseImg = Image.open(baseImg)
    watermark_withdraw = baseImg
    bin_file = open(key, mode='rb')
    bin_str = bin_file.read()
    key = format(int.from_bytes(bin_str, byteorder='big', signed=False),
                      '#0' + str(len(bin_str) * 8 + 2) + 'b')[2:]
    end_length_bin = key[len(key) - 8:len(key)]
    end_length = int(end_length_bin, 2)
    key = key[0:-8]
    key = key[0:-8] + key[len(key) - end_length:len(key)]
    w_w = int(math.sqrt(len(key)))
    w_h = w_w
    count = 0
    if len(key)!=w_w*w_h:
        print('key错误')
        return
    for w in range(0,w_w):
        for h in range(0,w_h):
            b_pixel = baseImg.getpixel((w, h))
            b_r = b_pixel[0]
            b_g = b_pixel[1]
            b_b = b_pixel[2]
            # 此阶段 0 表示白 1表示黑
            if key[count] == '0':
                if b_r == 255 & b_g == 255 & b_b == 255:
                    watermark_withdraw.putpixel((w, h), (255, 255, 255))
                    continue
                else:
                    watermark_withdraw.putpixel((w,h),(0,0,0))
            else:
                if (b_r & 1) == 1:
                    watermark_withdraw.putpixel((w, h), (0, 0, 0))
                else:
                    watermark_withdraw.putpixel((w, h), (255, 255, 255))
            count +=1
    cropped = watermark_withdraw.crop((0, 0, w_w, w_h))
    cropped.save(userPath+'/'+'withdraw.png')

# func_withdraw('watermarked_new.png',watermark_w,watermark_h,key)