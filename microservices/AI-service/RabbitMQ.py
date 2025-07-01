import json
import requests
from ai_utils import generate_reply

#


def on_message(ch, method, properties, body):
    # Process the incoming message
    email = json.loads(body)
    

    # Generate a reply using the AI service
    reply = generate_reply(email)
 

    # Send to drafts-service
    requests.post("http://drafts-service:5000/save", json={
        "email_id": email["id"],
        "reply": reply
    })


# # Establish a connection to RabbitMQ
# connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
# channel = connection.channel()
# channel.queue_declare(queue='new-email')

# # Set up a consumer to listen for messages on the queue
# channel.basic_consume(queue='new-email', on_message_callback=on_message, auto_ack=True)
# print('[*] Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()
