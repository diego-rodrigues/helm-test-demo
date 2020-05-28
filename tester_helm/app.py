"""
APP.py

This is the tester for the app installed using helm. A container with this
code will be executed in the k8s environment. It sends a message to a test
channel, it listens for the answer in the result channel. If the result is
the same as the expected value, it validates the application. If not, the 
application is rejected and the helm installation should rollback to a 
previous revision.
"""

import redis
import logging
import time
import os

REDIS_HOST=os.environ['REDIS_HOST']
REDIS_PORT=os.environ['REDIS_PORT']

TEST_CHANNEL = "test_channel"
RESULT_CHANNEL = "result_channel"
TEST_MESSAGE = "10"
EXPECTED_RESULT_MESSAGE = 20

logging.basicConfig(level=logging.INFO)
redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
service = redis_connection.pubsub()
service.subscribe(RESULT_CHANNEL)


def test():
    # sends a message to the test channel: the application should be
    # listening to this channel.

    redis_connection.publish(TEST_CHANNEL, TEST_MESSAGE)

    # awaits for the application listening to the test channel to process
    # the message and sends a response to the result channel

    # connects to PubSub
    received_message = service.get_message()
    while received_message == None:
        time.sleep(1)
        received_message = service.get_message()

    if received_message['data'] == 1:
        logging.info(
            'Connected to the RESULT_CHANNEL: {}'
            .format(RESULT_CHANNEL))
        
        retries = 0
        test_result = False
        while True:
            received_message = service.get_message()
            if received_message is not None:
                message = received_message['data']
                logging.info(
                    'Received message from RESULT_CHANNEL: {}'
                    .format(message))

                test_result = (int)(message) == EXPECTED_RESULT_MESSAGE
                break

            else:
                time.sleep(1)
                retries += 1
                if retries == 10:
                    logging.info('Max retries reached.')

        if test_result:
            logging.info('Test passed.')
            exit(0)
        else:
            logging.info('Test failed.')
            exit(1)


if __name__ == "__main__":
    test()