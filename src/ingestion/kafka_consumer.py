
import json
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "sales-transactions-stream"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="sales-streaming-group",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)


def consume_sales_data():
    total_received = 0
    total_sales = 0.0

    print("Waiting for streaming data...\n")

    try:
        for message in consumer:
            record = message.value

            total_received += 1
            total_sales += record["sales"]

            if total_received % 50 == 0:
                print(
                    f"Received: {total_received:,} records | "
                    f"Total Sales: {total_sales:,.2f}"
                )

            if total_received >= 1000:
                break

    finally:
        consumer.close()

    print("\nStreaming consumption completed!")
    print(f"Total Records Received: {total_received:,}")
    print(f"Total Sales: {total_sales:,.2f}")


if __name__ == "__main__":
    consume_sales_data()
