
import json
import time
import pandas as pd
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "sales-transactions-stream"

DATA_PATH = "data/raw/train.csv"
BATCH_SIZE = 100
LIMIT_RECORDS = 1000
START_ROW = 50000
DELAY_SECONDS = 0.5

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    acks="all",
    retries=5
)


def stream_sales_data():
    total_sent = 0

    try:
        for chunk in pd.read_csv(
            DATA_PATH,
            skiprows=range(1, START_ROW + 1),
            chunksize=BATCH_SIZE
        ):
            remaining = LIMIT_RECORDS - total_sent
            chunk = chunk.head(remaining)

            records = chunk.to_dict(orient="records")

            for record in records:
                record["date"] = str(record["date"])
                record["store_nbr"] = int(record["store_nbr"])
                record["onpromotion"] = int(record["onpromotion"])
                record["sales"] = float(record["sales"])

                producer.send(KAFKA_TOPIC, value=record)

            producer.flush()
            total_sent += len(records)

            print(f"Total records sent: {total_sent:,}")

            if total_sent >= LIMIT_RECORDS:
                break

            time.sleep(DELAY_SECONDS)

    finally:
        producer.close()

    print(f"\nStreaming completed! Total: {total_sent:,} records")


if __name__ == "__main__":
    stream_sales_data()
