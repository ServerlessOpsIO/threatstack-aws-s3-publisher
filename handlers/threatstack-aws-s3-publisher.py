# Publish a Threat Stack alert received via SNS to S3.
import boto3
import json
import logging
import os

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

# Initialize AWS client
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
sns_client = boto3.client('s3')

def _put_s3_object(event_message):
    '''Put an S3 object.'''
    return

def handler(event, context):
    _logger.debug('handler(): event={}'.format(json.dumps(event)))
    event_message = event.get('Records')[0].get('Sns').get('Message')
    _logger.info('handler(): event.message={}'.format(event_message))

    # Do something
    s3_response = _put_s3_object(event_message)

    # Return repsonse
    response = {
        's3': s3_response
    }

    _logger.info('handler(): response={}'.format(json.dumps(response)))
    return response


