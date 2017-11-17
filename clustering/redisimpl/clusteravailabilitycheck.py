import redis
import threading
import logging
import time
import json

###
#Ruben Edery on 15/11/17
#For Mr Gilles Giraud
#Tp Python
###

from threading import Timer

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)


class ClusterAvailabilityCheck(threading.Thread):

    def __init__(self, redis, server_id, url, _queue_, presence_interval):

        threading.Thread.__init__(self)

        #Define value server status
        self.statusserver=dict()

        self.redis = redis
        self.server_id = server_id
        self.channel_name = "cluster_management_channel"
        self._queue_ = _queue_
        self.presence_interval = presence_interval
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(self.channel_name)
        self.bootstrap = True
        self.servers = dict()
        self.ordinal = -1
        self.cluster_availability = None
        self.server_url = url

        self.timer = Timer(2*self.presence_interval, self.end_of_bootstrap )
        self.timer.start()

    def end_of_bootstrap(self):
        self.bootstrap = False;
        max_ordinal = -1
        for ordinal in self.servers.keys() :
            if ordinal > max_ordinal :
                max_ordinal = ordinal

        if -1 == max_ordinal :
            self.ordinal = 0
            logging.info("%s is master", self.server_id)

        else :
            #logging.info("max_ordinal = %s", max_ordinal)
            self.ordinal = 1 + max_ordinal
            logging.info("%s is backup", self.server_id)

        if self.cluster_availability :
            self.cluster_availability.set_ordinal(self.ordinal)
            self.cluster_availability.publishClusterPresence()

    def set_cluster_availability(self, cluster_availability):
        self.cluster_availability = cluster_availability



    def is_master(self):
        if self.bootstrap :
            return False

        for ordinal in self.servers.keys():
            if self.ordinal > ordinal :
                return False

        return True

    def get_instance_urls(self):
        urls = list()
        for ordinal in self.servers.keys():
            status = self.servers[ordinal]
            logging.info("%s", status)
            urls.append(status['url'])
        return urls

    def get_master_url(self):
        _ordinal_ = -1
        for ordinal in self.servers.keys():
            if ordinal == self.ordinal :
                continue

            if _ordinal_ == -1 :
                _ordinal_ = ordinal
            else :
                if ordinal < _ordinal_ :
                    _ordinal_ = ordinal

        status = self.servers[_ordinal_]
        return status['url'];

    #Use PyCharm
    def run(self):
        logging.info("TEST = %s", "TEST-CLUSTER-AVAILABILITY.")
        while True:
            return_message_state = self.pubsub.get_message()
            if return_message_state:
                logging.info("RECEIVED = %s", return_message_state)
                if return_message_state['data'] == 1:
                    None
                else:
                    status_state = json.loads(return_message_state['data'])
                    if self.server_id == status_state['id']:
                        logging.info("From Myself = %s", status_state['id'])
                        logging.info("Keys = %s",self.servers.viewitems())
                        None
                    self.statusserver[status_state['ordinal']] = status_state['timestamp_epoch']
                    logging.info("Server items = %s", self.servers.viewitems())
                    self.servers[status_state['ordinal']] = status_state
                    #while status server and timestamp items
                    for ordinal, timestamp in self.statusserver.items():
                        if (self.presence_interval + timestamp < time.time()):
                            #logging doesnt work, use print
                            print("Serveur "+str(ordinal) + " est kill")
                            del self.statusserver[ordinal]
                            del self.servers[ordinal]
                    if self.is_master():
                        print("Serveur : Serveur master ! ")
                    else:
                        print("Serveur : Serveur de secours ! ")
                        logging.info("END = %s", "FIN-TEST-CLUSTER-AVAILABILITY.")
                time.sleep(0.3)




