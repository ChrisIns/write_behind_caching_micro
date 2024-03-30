import pika
import json
from pymemcache.client import base
import argparse

#parsing the argument

parser = argparse.ArgumentParser()

parser.add_argument("-l", "--lastname",help="The lastname of the user", type=str)
parser.add_argument("-f", "--firstname",help="The firstname of the user", type=str)
parser.add_argument("-a", "--age",help="The age of the user", type=int)

args = parser.parse_args()



# Connect to memcache

client = base.Client(('localhost', 11210))



# writting data to cache

client.set("user", "{},{},{}".format(args.lastname,args.firstname,args.age))

# Connect to rabbitmq and publishing the message

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()



data = {
    "sql": "INSERT INTO users (LastName, FirstName, Age) VALUES (%s, %s, %s)",
    "val": (args.lastname, args.firstname,args.age)
}

channel.basic_publish(
    exchange="order",
    routing_key="sql",
    body=json.dumps(data)
)

print("Sending asynchronous message")

connection.close()

# getting the data from cache

print(client.get("user"))

