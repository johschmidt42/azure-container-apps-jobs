import json
import logging
import sys

from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient, QueueMessage

from models import OrderEvent, StorageQueueSettings

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.level = logging.INFO


class Process:
    def __init__(self):
        self.settings: StorageQueueSettings = StorageQueueSettings()
        self.credential: DefaultAzureCredential = DefaultAzureCredential()

        self.visibility_timeout: int = 5  # 5 min
        self.max_retries: int = 3
        self.queue_client: QueueClient = QueueClient(
            account_url=self.settings.storage_queue_url,
            queue_name=self.settings.queue_name,
            credential=self.credential,
        )

    def run(self) -> None:
        """
        Process storage queue messages.

        Returns: None

        """

        # This part should always work. Otherwise, Azure Container Apps will
        # endlessly process the same (visible) message,
        # because the message will not be read/processed.
        msg: None | QueueMessage = self.receive_message()

        # exit early if no messages are present
        if msg is None:
            logger.info("No messages received")
            return None

        msg_id: str = msg["id"]
        dequeue_count: int = msg["dequeue_count"]

        logger.info(f"Processing a new message from storage queue: {msg_id}")

        try:
            order_event: OrderEvent = OrderEvent(**json.loads(msg["content"]))

            # avoid endlessly retrying the same message
            if dequeue_count > self.max_retries:
                self.add_to_poison_queue(msg=msg)
                self.delete_message(msg=msg)
                return None

            # self.process_message_fail(order_event=order_event)
            self.process_message(order_event=order_event)
            self.delete_message(msg)

            return None

        except Exception as ex:
            logger.exception(ex)
            raise ex

    def add_to_poison_queue(self, msg: QueueMessage) -> None:
        """
        Adds a message to the poison queue.

        Args:
            self: The instance of the class.
            msg (QueueMessage): The message to be added to the poison queue.

        Returns:
            None
        """
        poison_queue_client: QueueClient = QueueClient(
            account_url=self.settings.storage_queue_url,
            queue_name=self.settings.poison_queue_name,
            credential=self.credential,
        )
        poison_queue_client.send_message(content=msg, time_to_live=-1)

        return None

    def receive_message(self) -> None | QueueMessage:
        """

        Receive a message from the queue.

        Returns:
            None: If no message is received from the queue.
            QueueMessage: The received message from the queue.

        Raises:
            Exception: If there is an error receiving the message.

        """
        try:
            msg: None | QueueMessage = self.queue_client.receive_message(
                visibility_timeout=self.visibility_timeout
            )
            return msg

        except Exception as ex:
            logger.exception(ex)
            logger.critical("Failed to receive message!")
            raise ex

    def delete_message(self, msg: QueueMessage) -> None:
        """
        Delete a message from the queue.

        Args:
            self (object): The instance of the class that this method belongs to.
            msg (QueueMessage): The message to be deleted from the queue.

        Returns:
            None: This method does not return anything.

        Raises:
            Exception: If there is an error encountered while trying to delete the message from the queue.
        """
        try:
            self.queue_client.delete_message(msg)
            return None

        except Exception as ex:
            logger.exception(ex)
            logger.critical("Failed to delete message!")
            raise ex

    def process_message(self, order_event: OrderEvent) -> None:
        """
        Processes a given order event message.

        Args:
            order_event: An instance of the OrderEvent class representing the order event message to be processed.

        Raises:
            Exception: If an error occurs during the processing of the message.

        Returns:
            None: No value is returned.
        """
        try:
            ...

        except Exception as ex:
            logger.exception(ex)
            logger.error("Failed to process message!")
            raise ex

    def process_message_fail(self, order_event: OrderEvent) -> None:
        raise ValueError("Can't process message!")


if __name__ == "__main__":
    process: Process = Process()
    process.run()
