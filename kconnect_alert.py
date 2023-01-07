import sys
import os
import json
import time
from base64 import b64encode
from dotenv import load_dotenv
import logging
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

file_name = os.path.splitext(os.path.basename(__file__))[0]

load_dotenv('.env')

# ID of channel you want to post message to
channel_id = "C04GX2M"
SLACK_BOT_TOKEN = 'xoxb-RwP2PYrbCxx'
WEB_HOOK = 'https://hooks.slack.com/services/T2HSRK5PS/M9uAj18IUZdJb'
MONITOR_TIME_SECS = 300
# os.environ['DEBUG'] = 'TRUE'

PYTHON_MAJOR_VERSION = sys.version_info.major
KAFKA_CONNECT_REST = os.environ.get('KAFKA_CONNECT_API_ENDPOINT', None)  # https://example.com:8084
KAFKA_CONNECT_CREDENTIALS = os.environ.get('KAFKA_CONNECT_API_CREDENTIALS', None)  # admin:password
BASE_PATH = '/connectors'

if PYTHON_MAJOR_VERSION == 2:
    import httplib
else:
    import http.client as httplib

default_log_args = {
    "level": logging.DEBUG if os.environ.get("DEBUG", 0) else logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M"
}

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)


def get_logger(name):
    logging.basicConfig(**default_log_args)
    return logging.getLogger(name)


class VariableError(Exception):
    def __init__(self, variable, message='Environment variable not found or values missing!'):
        self.variable = variable
        self.message = message
        super().__init__(self.variable + ' - ' + self.message)


class ConnectError(Exception):
    def __init__(self, method, path, http_status, reason):
        self.method = method
        self.path = path
        self.http_status = http_status
        self.reason = reason


class HttpUtil:
    def __init__(self, http_connection, headers):
        self.http_connection = http_connection
        self.headers = headers

    def get(self, path):
        log = get_logger(f"{HttpUtil.__name__}.{HttpUtil.get.__name__}")
        self.http_connection.request(method='GET', url=path, body=None, headers=self.headers)
        response = self.http_connection.getresponse()

        if response.status != 200:
            raise ConnectError(method='GET', path=path, http_status=response.status, reason=response.reason)

        response_json = json.loads(response.read())
        log.debug(f'path: {path} | status: {response.status} | response: {response_json}')

        return response_json

    def post(self, path):
        log = get_logger(f"{HttpUtil.__name__}.{HttpUtil.post.__name__}")
        self.http_connection.request('POST', url=path, body=None, headers=self.headers)
        response = self.http_connection.getresponse()
        response.read()

        if response.status != 204:
            raise ConnectError(method='POST', path=path, http_status=response.status, reason=response.reason)

        result = {'http_status': response.status, 'reason': response.reason, 'path': path, 'method': 'POST'}
        log.debug(f'{result}')
        return result

    def put(self, path):
        log = get_logger(f"{HttpUtil.__name__}.{HttpUtil.put.__name__}")
        self.http_connection.request('PUT', url=path, body=None, headers=self.headers)
        response = self.http_connection.getresponse()
        response.read()

        if response.status != 202:
            raise ConnectError(method='PUT', path=path, http_status=response.status, reason=response.reason)

        result = {'http_status': response.status, 'reason': response.reason, 'path': path, 'method': 'PUT'}
        log.debug(f'{result}')
        return result


def alert_slack(connector_name=None, connector_state=None, connector_type=None, worker_id=None, task_id=None,
                task_state=None, trace=None, message=None):
    kafka_template = [{
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": connector_name,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Connector State:*\n{connector_state}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Worker ID:*\n{worker_id}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*When:*\n{datetime.datetime.now()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:*\n{connector_type}"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Task ID:*\n{task_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Task State:*\n{task_state}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""*Trace:*\n```{trace[:2500]}```"""
                }
            }
        ]
    }]

    client = WebClient(token=SLACK_BOT_TOKEN)
    log = get_logger(f"{alert_slack.__name__}")
    try:
        result = client.chat_postMessage(
            username='Alerts_Bot',
            icon_emoji=':traffic_light:',
            channel=channel_id,
            text=message,
            attachments=kafka_template
        )
        log.debug(f"Response - {result}")
    except SlackApiError as e:
        log.exception(f"Error: {e}")


if __name__ == '__main__':
    log = get_logger("__main__")

    while True:
        if not KAFKA_CONNECT_REST:
            raise VariableError('KAFKA_CONNECT_REST')
        if str(KAFKA_CONNECT_REST).lower().startswith('https'):
            conn = httplib.HTTPSConnection(KAFKA_CONNECT_REST.replace('https://', '').replace('http://', ''))
            if not KAFKA_CONNECT_CREDENTIALS:
                raise VariableError('KAFKA_CONNECT_CREDENTIALS ')
        else:
            conn = httplib.HTTPConnection(KAFKA_CONNECT_REST.replace('https://', '').replace('http://', ''))

        # Authorization token: we need to base 64 encode, then decode it to ASCII as python 3 stores it as a byte string
        auth_header = {
            "Authorization": "Basic {}".format(
                b64encode(bytes(f"{KAFKA_CONNECT_CREDENTIALS}", "utf-8")).decode("ascii"))
        }
        http_util = HttpUtil(conn, headers=auth_header)
        try:
            connectors = http_util.get(BASE_PATH)  # list of all available connectors
            for connector in connectors:
                status = http_util.get(BASE_PATH + '/' + connector + '/status')
                connector_state = status['connector']['state']
                worker_id = status['connector']['worker_id']
                connector_name = status['name']
                connector_type = status['type']
                log.info('Connector: ' + connector_name + ': ' + connector_state)
                failed_tasks = {}
                for task in status['tasks']:
                    task_id = str(task['id'])
                    task_state = task['state']
                    trace = task['trace']
                    log.info('Task ' + task_id + ': ' + task_state)
                    if task['state'] == 'FAILED':
                        message = f'Alert! - connector {connector_name} has failed task({task_id}). Restarting!'
                        response = http_util.post(
                            BASE_PATH + '/' + connector + '/tasks/' + str(task['id']) + '/restart')
                        log.info(f"{response}")
                        alert_slack(connector_name=connector_name, connector_state=connector_state,
                                    connector_type=connector_type, worker_id=worker_id, task_id=task_id,
                                    task_state=task_state, trace=trace, message=message)
        except ConnectError as ex:
            log.exception('Got error %s (%s) for request %s %s%s  ' % (
                ex.http_status, ex.reason, ex.method, KAFKA_CONNECT_REST, ex.path))
        time.sleep(MONITOR_TIME_SECS)
