from kafka import KafkaConsumer
import logging
from etl import models

logger = logging.getLogger(__name__)
configs = {}


def run(config):
    global configs
    configs = config
    models.create_db_connection(configs)
    consumer = KafkaConsumer(config.KAFKA_TOPIC_NAME,
                             bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                             group_id=config.KAFKA_GROUP_ID,
                             key_deserializer=bytes.decode,
                             value_deserializer=bytes.decode,
                             auto_offset_reset=config.KAFKA_AUTO_OFFSET_RESET,
                             session_timeout_ms=config.KAFKA_SESSION_TIMEOUT_MS,
                             enable_auto_commit=False)
    for record in consumer:
        try:
            logfile, datatype, quarter = record.key.split("_")

            if not is_valid_csv(record.value):
                with open(logfile, 'r+') as f:
                    f.truncate(0)
                    f.write("Invalid CSV file")
                logger.info("Receive an invalid csv file.")
                continue

            if datatype == "impressions":
                pass
                models.import_impressions(logfile=logfile, data=record.value, quarter=quarter)
            elif datatype == "clicks":
                models.import_clicks(logfile=logfile, data=record.value, quarter=quarter)
            elif datatype == "conversions":
                models.import_conversions(logfile=logfile, data=record.value, quarter=quarter)
            else:
                logger.info("Receive an unsupported csv file.")
                with open(logfile, 'r+') as f:
                    f.truncate(0)
                    f.write("Can not handle this csv type!")
            consumer.commit()

        except KeyError as e:
            logger.error(e.args[0])
            consumer.commit()
        except Exception as e:
            logger.error("Probably can not connect to mysql, error message is:\n {}".format(e))
            break
    consumer.close()


def is_valid_csv(file):
    return True
