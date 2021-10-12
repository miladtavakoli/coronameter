
# Coronameter
Crawl data from [https://worldometers.info/coronavirus/](https://worldometers.info/coronavirus/) and compare statistics


# Requirements

 - Create python virtualenv and active:
	  `python3 -m "virtualenv" .venv && source .venv/bin/activate`
 - install requirements
     `pip install -r requirements.txt`

 - Database required **MongoDB**:
	 - Mongodb :  [https://docs.mongodb.com/manual/installation/](https://docs.mongodb.com/manual/installation/)
	 - Docker hub : [https://hub.docker.com/_/mongo](https://hub.docker.com/_/mongo)
	
- Run **RabbitMQ**:
  - https://www.rabbitmq.com/download.html
	- `sudo docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.8-management`


- Create a `.env` file based on  `.env-example` file.

- Run 

