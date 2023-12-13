import click
import psycopg2
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# PostgreSQL query to get replication slot size
REPLICATION_SLOT_QUERY = "SELECT slot_name, pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS replication_lag_bytes FROM pg_replication_slots;"

# Slack client initialization
slack_token = os.environ["SLACK_BOT_TOKEN"]
deployment_name = os.environ["DEPLOYMENT_NAME"]
client = WebClient(token=slack_token)


def query_replication_slot_size(conn):
    with conn.cursor() as cur:
        cur.execute(REPLICATION_SLOT_QUERY)
        slots = cur.fetchall()
        return slots


def post_message_to_slack(channel, message):
    try:
        response = client.chat_postMessage(
            channel=channel, text=message, parse="full", link_names=True
        )
    except SlackApiError as e:
        print(f"Error posting to Slack: {e.response['error']}")


@click.command()
@click.option("--db-host", default="localhost", help="Database host.")
@click.option("--db-port", default=5432, help="Database port.")
@click.option("--db-user", default="user", help="Database user.")
@click.option("--db-password", default="password", help="Database password.")
@click.option("--db-name", default="dbname", help="Database name.")
@click.option(
    "--slack-channel", default="#general", help="Slack channel to post messages to."
)
@click.option(
    "--size-threshold-mb",
    default=100,
    type=int,
    help="Size threshold in MB for triggering a Slack notification.",
)
@click.option(
    "--interval-seconds", default=60, help="Interval in seconds between each check."
)
def main(
    db_host,
    db_port,
    db_user,
    db_password,
    db_name,
    slack_channel,
    interval_seconds,
    size_threshold_mb,
):
    while True:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
        )
        print(f"Connected to database '{db_name}' on '{db_host}'")
        slots = query_replication_slot_size(conn)
        for slot in slots:
            slot_name, size = slot
            size_mb = size / 1024 / 1024
            if size_mb > size_threshold_mb:
                msg = f"☠️ [{deployment_name}] Replication slot '{slot_name}' size is over {size_threshold_mb}MB: {size_mb} MB. cc: @channel"
                post_message_to_slack(slack_channel, msg)
            else:
                msg = f"🎅 [{deployment_name}] Replication slot '{slot_name}' size is {size_mb} MB."
                post_message_to_slack(slack_channel, msg)

        conn.close()
        print(f"Disconnected from database '{db_name}' on '{db_host}'")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
