import logging
import sys
import uuid

from models import OrderEvent

logger: logging.Logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.level = logging.INFO


def generate_order_msg() -> str:
    """
    Generate an order message.

    Returns:
        str: The JSON representation of the order event.
    """
    order_id: str = str(uuid.uuid4())
    logger.info(f"Generating a new order msg: {order_id}")
    order_event: OrderEvent = OrderEvent(order_id=order_id, msg="Hello World")
    return order_event.model_dump_json()
