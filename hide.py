#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python version 2.7
# reference: http://www.freebuf.com/articles/database/99504.html
# some tips: In python2.7, when open file with rb mode, element should be converted by chr or ord.

# Python 2.7.6 (default, Jun 22 2015, 17:58:13)
# [GCC 4.8.2] on linux2
# Type "help", "copyright", "credits" or "license" for more information.
# >>> img = "/root/hehua.bmp"
# >>> with open(img, 'rb') as f:
# ...     all_the_bmp = f.read()
# ...
# >>> type(all_the_bmp[0])
# <type 'str'>
#
#
# Python 3.4.3 (default, Oct 14 2015, 20:28:29)
# [GCC 4.8.4] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>> img = "/root/hehua.bmp"
# >>>
# >>> with open(img, 'rb') as f:
# ...     all_the_bmp = f.read()
# ...
# >>> type(all_the_bmp[0])
# <class 'int'>

import struct
import sys

img = "/root/hehua.bmp"
text = "/root/test.txt"

with open(img, 'rb') as f:
    all_the_bmp = f.read()

with open(text, 'rb') as f:
    all_the_text = f.read()

count = struct.unpack('<L', all_the_bmp[10:14])[0]  # 获取bmp像素数据偏移值
print "bmp像素数据偏移值:0x%x" % count, "%d" % count

bmp_length = len(all_the_bmp) - count  # 获取bmp像素数据大小
txt_length = len(all_the_text)  # 获取文本数据大小

bit = 4  # 按照bit个比特位进行数据拆分

if bmp_length < txt_length * int(8 / bit):  # 判断bmp空间是否足够隐写
    print("too small")
    sys.exit(1)

result = []
pos = 0

# 将文本数据大小进行隐写
for i in range(4):  # 用四个字节表示txt文件大小，约等于2^32/2^8/2^20=512MB
    bchar = (txt_length >> (i * 8)) & 0xff  # 循环取最后一个字节
    for j in range(int(8 / bit)):
        temp = (bchar >> j * bit) & (pow(2, bit) - 1)  # or (bchar >> (j * bit)) & (1<< bit - 1) 取最后bit个比特
        mchar = ((ord(all_the_bmp[count + pos]) >> bit) << bit) | temp
        result.append(mchar)
        pos += 1

for bchar in all_the_text:  # 将文本数据进行隐写
    for i in range(int(8 / bit)):
        temp = (ord(bchar) >> i * bit) & (pow(2, bit) - 1)
        result.append(((ord(all_the_bmp[count + pos]) >> bit) << bit) | temp)
        pos += 1

m_bmp = all_the_bmp[:count] + "".join(map(chr, result)) + all_the_bmp[count+pos:]
with open("/root/m{}_hehua.bmp".format(bit), 'wb') as f:
    f.write(m_bmp)

ord1 = map(ord, all_the_bmp)
ord2 = map(ord, m_bmp)

diff = map(lambda x: abs(x[0]-x[1]), zip(ord1, ord2))
diff = all_the_bmp[:count] + "".join(map(chr, diff))[count:]

with open("/root/diff.bmp".format(bit), 'wb') as f:
    f.write(diff)


pos = 0
data_len = 0
for i in range(4):  # 读取信息长度
    bchar = 0
    for j in range(int(8 / bit)):
        bchar |= ((ord(m_bmp[count + pos]) & (pow(2, bit) - 1)) << j * bit)
        pos += 1
    data_len |= bchar << i * 8

result = []
for i in range(data_len):  # 读取隐写数据
    bchar = 0
    for j in range(int(8 / bit)):
        bchar |= ((ord(m_bmp[count + pos]) & (pow(2, bit) - 1)) << j * bit)
        pos += 1
    result.append(chr(bchar))
result = "".join(result)
with open("/root/result.txt", 'wb') as f:
    f.write(result)

