import pika
import json
import mysql.connector
import os



# connect to mariadb

mydb = mysql.connector.connect(
    host = "mymariadb",
    username = os.environ.get('USER'),
    password = os.environ.get('PASSWORD'),
    database = "main"
)

cursor = mydb.cursor()

# connect to rabbitmq and creating the exchange

connection = pika.BlockingConnection(pika.ConnectionParameters('my-rabbit'))
channel = connection.channel()

channel.exchange_declare(
    exchange= "order",
    exchange_type="direct"
)

# creating the queue

queue = channel.queue_declare('sql_queue') #create a queue with a name
queue_name = queue.method.queue

# creating the binding

channel.queue_bind(
    exchange="order",
    queue=queue_name,
    routing_key="sql"
)

# consumming the msg and sending the sql write query

def callback(ch, method, properties, body):
    payload= json.loads(body)
    print("Sending SQL INSERT INTO")
    sql = payload["sql"]
    val = payload["val"]
    cursor.execute(sql,val)
    mydb.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)

#consumming require the callback and the queue name
    
channel.basic_consume(on_message_callback=callback, queue=queue_name)

print(" waiting for notify message")

channel.start_consuming()
