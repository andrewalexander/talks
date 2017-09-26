#!/usr/bin/env/python

"""
Modified from Python packages supplied in Amazon Elastic Beanstalk Getting Started Guide: 
  
  http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/RelatedResources.html

"""
import logging
import logging.handlers
import urllib
import cgi
import os
import json
import boto3

from wsgiref.simple_server import make_server
from botocore.exceptions import ClientError, NoCredentialsError


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/var/log/python/log/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

# Handle the welcome_page
welcome = urllib.urlopen('public/index.html').read()

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    status  = ''
    headers = []

    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                logger.info("Received message: %s" % request_body)
            elif path == '/uploadPost':
                # read our form data from the POST
                formdata = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])

                response_json = process_post_data(formdata, environ)
                status = response_json['status']
                print(response_json)
                
                response = str(response_json['response'])
                print(response)

                # request_body_size = int(environ['CONTENT_LENGTH'])
                # request_body = environ['wsgi.input'].read(request_body_size).decode()
                # logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'], environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        
    else:
        response = welcome
    
    if not status:
        status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]

def process_post_data(formdata, environ):
    if 'upfile' in formdata and formdata['upfile'].filename != '':    
        # we gave our upload an id of 'upfile' in the HTML
        file_data = formdata['upfile'].file.read()
        filename = formdata['upfile'].filename
        # CHANGE THIS!!!
        bucket_name = 'se-summit-17-demo-bucket'

        # write the content of the uploaded file to a local file
        target = os.path.join('uploads', filename)
        f = open(target, 'wb')
        f.write(file_data)
        f.close()
        logger.info('Wrote {} bytes to uploads/{}'.format(environ['CONTENT_LENGTH'], filename))
        
        try:
            # upload to s3 with public permissions
            s3 = boto3.resource('s3')
            s3.Object(bucket_name, 'raw-images/{}'.format(filename)).upload_file('uploads/{}'.format(filename))
            logger.info('Wrote {} bytes to s3://{}/raw-images/{}'.format(environ['CONTENT_LENGTH'], bucket_name, filename))                    
            
            # generate s3 url - replaces spaces with '+'
            s3_url = 'http://s3.amazonaws.com/{}/processed-thumbnails/thumb-{}'.format(bucket_name, filename)
            s3_url = s3_url.replace(' ', '+')

            response_json = {
                'status': '200 OK',
                'response': s3_url
            }
        except (ClientError, NoCredentialsError) as e:
            logging.exception(e)
            response_json = {
                'status': '500 Internal Server Error',
                'response': e
            }

    return response_json

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
