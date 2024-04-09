# write_behind_caching microservice architecture

![write behind](https://github.com/ChrisIns/write_behind_caching_micro/assets/45426865/38fe86d5-4aee-4791-91a4-c9c6699f4876)

The goal of this project is to demonstrate a simple write behind caching mechanism with RabbitMQ and Memcached.

For the need of this demo, the use case is simple: we want to add a user to the database.

Our user object consists of a LastName, FirstName and Age.

The goal of a write-behind caching strategy is to process the write directly to the caching system first, and then asynchronously write to the database. In comparaison to a write-through caching strategy, the write-behind strategy improves the write performance (the user doesnt have to wait for the write to complete(i.e for the write to be processed by the database).

This simple project will then go through multiple stages where i'll add a k8s layer onto it, then i'll migrate everything to AWS.

## Tools Used

The caching tool used will be memcached

We'll use a rabbitmq image for dealing with asynchronous jobs

Two python code will be written to publish a job to the queue (and write to the memcached container), and one script will be run as a container to consumme the event and put in the queue, and write to the database asynchronously.

## Rabbitmq Consummer script

The script will:

* Connect to rabbitmq and mysql container
* Create an exchange responsible for receiving the message from the publisher
* Create a queue that will store the messages
* Create a binding that will link the exchange and the queue together (with the binding key set to "sql")
* Create the callback method that will access the body of the message pushed by the publisher, and do a specific action asynchronously (in this case it will do an INSERT INTO the mysql database)

## Publisher Script

The script will:

* take as inputs the Lastname, FirstName, and age that the user want to write to the the database
* The script will connect to the memcached container and write the data to the cache
* Connect to rabbitmq and publish the sql queries and its variables to the rabbitmq queue (by using the good routing key)
* It will then close the connection to the rabbitmq instance

## memcached container

The docker image was created based on a simple Ubuntu image and by doing the usual install steps to run memcached as a service

## mysql container

We build the docker image from a basic mysql image and just add the startup mysql script to create the database and the table.

## Rabbitmq consummer app container

The docker image for the consummer script was built from a basic Ubuntu image, we install python and pip, we copy the source code and the requirement.txt file.
Then we install the requirements based on this file.
The only change worth talking about is that we commented the CMD statement that runs the script, because the CMD will be done in the docker-compose file.

## Docker compose 

We use docker compose to run / build the differents images of this project.
The most important thing is that we pass the environment variables like sql user and password through the .env file that is obviously not pushed to the repo.

Also, even though I use the depends_on keyword to start the mysql and rabbitmq container before the consummer container, we have to use the sleep command or else i'm running into error connecting the script to the database (happens only with docker compose)

## Running the project and results

### starting the containers

```
sudo docker-compose up -d 
```

### Checking containers are running 

```
test@test-virtual-machine:~/write_behind_micro$ sudo docker ps
CONTAINER ID   IMAGE                            COMMAND                  CREATED      STATUS              PORTS                                                                                                                                                 NAMES
c6716e9d3da8   write_behind_micro_myconsummer   "sh -c 'sleep 10;pyt…"   8 days ago   Up About a minute                                                                                                                                                         write_behind_micro_myconsummer_1
6652ad7783de   rabbitmq:3-management            "docker-entrypoint.s…"   8 days ago   Up About a minute   4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, :::5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp, :::15672->15672/tcp   write_behind_micro_my-rabbit_1
ef5c777b6991   write_behind_micro_mymariadb     "docker-entrypoint.s…"   8 days ago   Up About a minute   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp, 33060/tcp                                                                                                  write_behind_micro_mymariadb_1
d58ea34ef73a   write_behind_micro_memmicro      "/bin/sh -c '/usr/bi…"   8 days ago   Up About a minute   0.0.0.0:11210->11211/tcp, :::11210->11211/tcp
```

### Running the publisher script

```
python3 publisher.py -l Smith -f John -a 25

```
### Checking the database

```
sudo docker exec -it ef5c777b6991  mysql -u *** -p main

mysql> SELECT * FROM users;
+----+----------+-----------+------+
| ID | LastName | FirstName | age  |
+----+----------+-----------+------+
|  1 | Smith    | John      |   25 |
+----+----------+-----------+------+
1 row in set (0.01 sec)

```

The data was indeed written asynchronously thanks to the consummer container.

