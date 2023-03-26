import threading

from config import Config
import etl
from kafka import KafkaProducer
import pytest
import docker
import time
from threading import Thread
import sys

impressions_csv1 = "banner_id,campaign_id\n1,1\n2,1\n3,1\n1,2\n4,3"
clicks_csv1 = "click_id,banner_id,campaign_id\n100000,1,1\n100001,2,1\n100002,4,3"
clicks_csv2 = "click_id,banner_id,campaign_id\n100003,1,1\n100004,1,2\n100002,4,3"
conversions_csv1 = "conversion_id,click_id,revenue\n2000,100002,1.173893\n2001,100001,0.388161"


@pytest.fixture(scope="session", autouse=True)
def setup_and_cleanup(request):
    docker_client = docker.from_env()

    """Cleanup a testing containers once we are finished."""

    def remove_test_containers():
        tmp = docker_client.containers.list(all=True, filters={'name': 'etl-test-kafka'})
        for con in tmp:
            con.stop()
            con.remove()
        tmp = docker_client.containers.list(all=True, filters={'name': 'etl-test-zookeeper'})
        for con in tmp:
            con.stop()
            con.remove()
        tmp = docker_client.containers.list(all=True, filters={'name': 'etl-test-mysql'})
        for con in tmp:
            con.stop()
            con.remove()
        tmp = docker_client.networks.list(filters={'name': 'etl-test-network'})
        for net in tmp:
            net.remove()

    request.addfinalizer(remove_test_containers)

    """prepare something ahead of all tests."""
    remove_test_containers()
    docker_client.networks.create("etl-test-network", driver="bridge")
    docker_client.containers.run("docker.io/confluentinc/cp-zookeeper:5.3.6", name='etl-test-zookeeper',
                                 network="etl-test-network", detach=True,
                                 environment=["ZOOKEEPER_CLIENT_PORT=2181"])
    docker_client.containers.run("docker.io/confluentinc/cp-kafka:5.3.6", name='etl-test-kafka', ports={'29092': 29092},
                                 detach=True, network="etl-test-network",
                                 environment={
                                     "KAFKA_BROKER_ID": 1,
                                     "KAFKA_ZOOKEEPER_CONNECT": "etl-test-zookeeper:2181",
                                     "KAFKA_ADVERTISED_LISTENERS":
                                         "PLAINTEXT://etl-test-kafka:9092,PLAINTEXT_HOST://localhost:29092",
                                     "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP":
                                         "PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT",
                                     "KAFKA_INTER_BROKER_LISTENER_NAME": "PLAINTEXT",
                                     "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": 1
                                 })
    docker_client.containers.run("docker.io/mariadb:10.3.38", name='etl-test-mysql', detach=True,
                                 ports={'3306': 13306},
                                 environment={"MARIADB_ROOT_PASSWORD": "test",
                                              "MARIADB_DATABASE": "test",
                                              "MARIADB_USER": "test",
                                              "MARIADB_PASSWORD": "test"})

    time.sleep(10)

    producer = KafkaProducer(bootstrap_servers="localhost:29092", retries="1")
    producer.send("test-csv", key=str.encode("/tmp/test-impression1_impressions_0"),
                  value=str.encode(impressions_csv1)).get()
    producer.send("test-csv", key=str.encode("/tmp/test-click1_clicks_0"),
                  value=str.encode(clicks_csv1)).get()
    producer.send("test-csv", key=str.encode("/tmp/test-click2_clicks_0"),
                  value=str.encode(clicks_csv2)).get()
    producer.send("test-csv", key=str.encode("/tmp/test-conversion1_conversions_0"),
                  value=str.encode(conversions_csv1)).get()


def test_check():
    config = Config()
    setattr(config, "KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    setattr(config, "KAFKA_GROUP_ID", "test-grp")
    setattr(config, "KAFKA_AUTO_OFFSET_RESET", "earliest")
    setattr(config, "KAFKA_TOPIC_NAME", "test-csv")
    setattr(config, "KAFKA_SESSION_TIMEOUT_MS", 60000)
    setattr(config, "MYSQL_USER", "test")
    setattr(config, "MYSQL_PASS", "test")
    setattr(config, "MYSQL_DB", "test")
    setattr(config, "MYSQL_ADDR", "localhost:13306")

    runner = Thread(target=etl.run, args=(config,))
    runner.start()
    time.sleep(5)
    runner.join(0)
    assert etl.models.get_data_revision() == 4
    assert etl.models.get_tops_by_revenue(0, 1) == [2]
    assert etl.models.get_tops_by_clicks(0, 1) == [1, 2]
    assert etl.models.get_tops_by_clicks(0, 3) == [4]
    assert etl.models.get_tops_by_random(0, 2) == [1]
    assert etl.models.get_tops_by_random(0, 4) == []
