import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')


data = open('test.jpg', 'rb')
s3.Bucket('my-bucket').put_object(Key='test.jpg', Body=data)