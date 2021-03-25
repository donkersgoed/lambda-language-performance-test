import datetime
import sys
import boto3

def retrieve_logs():
    log_group = sys.argv[1]
    cloudwatch_client = boto3.client('logs')

    paginator = cloudwatch_client.get_paginator('filter_log_events')

    ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
    start_time = int(ten_minutes_ago.timestamp() * 1000)

    events = []
    response_iterator = paginator.paginate(
        logGroupName=log_group,
        startTime=start_time
    )
    for page in response_iterator:
        events += page['events']

    with open('log_output.txt', 'w+') as log_output_fh:
        log_output_fh.write(
            ''.join(
                [
                    f"{event['timestamp']}\t{event['message']}" for event in events
                ]
            )
        )

if __name__ == '__main__':
    retrieve_logs()
