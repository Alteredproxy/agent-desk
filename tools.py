from langchain_core.tools import tool

ORDERS = {
    "123": {"status": "shipped", "amount": 50.00, "item": "Keyboard"},
    "456": {"status": "processing", "amount": 120.00, "item": "Monitor"}
}


@tool
def get_order(order_id: str):
    """ this funtion take in an order id and returns the order """
    if order_id in ORDERS:
        return ORDERS[order_id]
    else:
        return "Order not found"


@tool
def process_refund(order_id: str):
    """ This funtion check get the amount for a refund"""
    if order_id in ORDERS:
        ORDERS[order_id]["status"] = "refunded"
        return f"Refund processed for {ORDERS[order_id].get("amount")}"