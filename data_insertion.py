import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')
import pdf2jpg
from pdf2jpg import pdf2jpg
inputpath = r"FInvoice.pdf"
outputpath = r""
result = pdf2jpg.convert_pdf2jpg(inputpath,outputpath, pages="ALL")
print(outputpath)

import os
import glob

folder = inputpath+"_dir/"
for count, filename in enumerate(os.listdir(folder)):
    oldname = folder + filename   
    newname = folder + "invoice_" + str(count + 1) + ".jpg"
    os.rename(oldname, newname)

image= "invoice_1.jpg"

data = open(image, 'rb')
s3.Bucket('billfly-bucket').put_object(Key='invoice_1.jpg', Body=data)