# Publish a Threat Stack alert received via SNS to S3.
import boto3
import iso8601
import json
import logging
import os

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))
_logger = logging.getLogger(__name__)

# Initialize AWS client
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
AWS_S3_PREFIX='alerts'
s3_client = boto3.client('s3')

def _get_alert_date(alert):
    '''Return a datetime object of date and time found in the alert.'''
    created_at = alert.get('alert').get('createdAt')
    date_time = iso8601.parse_date(created_at)
    return date_time


def _get_key_prefix(dt):
    '''Get a key prefix based on datetime object.'''
    key ='year={year}/month={month}/day={day}'.format(
        year=dt.year,
        month=dt.month,
        day=dt.day,
    )
    return key


def _get_key_by_type(obj_type, obj_id, alert_id, dt):
    '''Get a key name based on obj type, id, alert ID and datetime.'''
    key_prefix = _get_key_prefix(dt)
    object_name = '{}.json'.format(obj_id)

    key = '/'.join(
        [
            AWS_S3_PREFIX,
            obj_type,
            key_prefix,
            'alert_id={}'.format(alert_id),
            object_name
        ]
    )
    return key


def _get_alert_key(alert_id, dt):
    '''Get a key name based on alert_id and datetime'''
    key_prefix = _get_key_prefix(dt)
    object_name = '{}.json'.format(alert_id)
    key = '/'.join(
        [
            AWS_S3_PREFIX,
            'alert',
            key_prefix,
            object_name
        ]
    )
    return key


def _put_s3_object(key, obj_dict):
    '''Put an S3 object.'''
    resp = s3_client.put_object(
        Body=json.dumps(obj_dict),
        Bucket=AWS_S3_BUCKET_NAME,
        Key=key
    )
    return resp


def handler(event, context):
    _logger.debug('handler(): event={}'.format(json.dumps(event)))
    event_message = event.get('Records')[0].get('Sns').get('Message')
    _logger.info('handler(): event.message={}'.format(event_message))

    alert = json.loads(event_message)
    alert_id = alert.get('alert').get('id')
    dt = _get_alert_date(alert)

    s3_responses = {}

    for k, v in alert.items():
        if k == 'alert':
            key = _get_alert_key(alert_id, dt)
            resp = _put_s3_object(key, v)
            s3_responses[k] = {key: resp}

        elif k == 'events':
            event_responses = []
            for item in v:
                event_id = item.get('_id')
                key = _get_key_by_type(k, event_id, alert_id, dt)
                resp = _put_s3_object(key, item)
                event_responses.append({key: resp})
            s3_responses[k] = event_responses

        else:
            obj_id = v.get('id')
            key = _get_key_by_type(k, obj_id, alert_id, dt)
            resp = _put_s3_object(key, v)
            s3_responses[k] = {key: resp}

    # Return response
    response = {
        's3': s3_responses
    }

    _logger.info('handler(): response={}'.format(json.dumps(response)))
    return response

