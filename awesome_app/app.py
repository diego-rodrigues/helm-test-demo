import redis
import logging
import time
import os

REDIS_HOST=os.environ['REDIS_HOST']
REDIS_PORT=os.environ['REDIS_PORT']

TEST_CHANNEL = "test_channel"
RESULT_CHANNEL = "result_channel"
logging.basicConfig(level=logging.INFO)
redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
service = redis_connection.pubsub()
service.subscribe(TEST_CHANNEL)


def listen():
    continue_listening = True
    received_message = service.get_message()
    while received_message == None:
        time.sleep(1)
        received_message = service.get_message()

    if received_message['data'] == 1:
        logging.info(
            'Connected to the TEST_CHANNEL: {}'
            .format(TEST_CHANNEL))
        
        while continue_listening:
            received_message = service.get_message()
            if received_message:
                message = received_message['data']
                logging.info('Received message: {}'.format(message))

                
                if message == b'STOP':
                    continue_listening = False

                else:
                    result_message = (int)(message) + 15
                    redis_connection.publish(RESULT_CHANNEL, result_message)
                    logging.info('Sent message: {} to channel: {}.'.format(result_message, RESULT_CHANNEL))

            time.sleep(1)

    logging.info('Exiting...')



if __name__ == "__main__":
    listen()