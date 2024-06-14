import requests
import json
from typing import TypedDict, Optional, List
from enum import Enum
from datetime import timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Order(TypedDict):
    accountNumber: str
    additionalInfo: Optional[str]
    affiliateId: Optional[str]
    canceled: str
    comments: Optional[str]
    companyId: str
    currency: str
    dateCanceled: Optional[str]
    dateInsert: str
    dateLock: Optional[str]
    dateMarked: Optional[str]
    dateStatus: str
    dateUpdate: str
    deducted: str
    discountValue: str
    empCanceledId: Optional[str]
    empMarkedId: Optional[str]
    empStatusId: str
    externalOrder: str
    id: str
    id1c: Optional[str]
    lid: str
    lockedBy: Optional[str]
    marked: str
    orderTopic: Optional[str]
    payed: str
    personTypeId: str
    personTypeXmlId: str
    price: str
    reasonCanceled: Optional[str]
    reasonMarked: Optional[str]
    recountFlag: str
    recurringId: Optional[str]
    responsibleId: Optional[str]
    statusId: str
    statusXmlId: str
    taxValue: str
    updated1c: str
    userDescription: str
    userId: str
    version: str
    version1c: Optional[str]
    xmlId: str

class BasketItem(TypedDict):
    id: str
    orderId: str
    productId: str
    name: str
    price: str
    quantity: str

class OrderStatus(Enum):
    PENDING = "P"
    DONE = "F"
    DELIVERING = "D"
    ACCEPTED_PAYMENT_PENDING = "N"

def parse_orders(response: str) -> List[Order]:
    data = json.loads(response)
    return data.get('result', {}).get('orders', [])

def parse_basket_items(response: str) -> List[BasketItem]:
    data = json.loads(response)
    return data.get('result', {}).get('basketItems', [])

def fetch_data(url: str, headers: dict, payload: Optional[dict] = None) -> Optional[str]:
    try:
        if payload:
            logging.info(f"POST request to {url} with payload {payload}")
            response = requests.post(url, headers=headers, json=payload)
        else:
            logging.info(f"GET request to {url}")
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

def get_order_by_number(base_url: str, headers: dict, order_number: str) -> Optional[Order]:
    url = f"{base_url}/sale.order.list/"
    payload = {"filter": {"id": order_number}, "select": ["dateInsert"]}
    response = fetch_data(url, headers, payload)
    if response:
        orders = parse_orders(response)
        if orders:
            return orders[0]
    return None

def get_orders_by_status_before_date(base_url: str, headers: dict, status: str, date: str) -> List[Order]:
    url = f"{base_url}/sale.order.list/"
    filters = {"statusId": status, "<=dateInsert": date}
    payload = {"filter": filters, "select": ["id", "accountNumber", "statusId"]}
    response = fetch_data(url, headers, payload)
    return parse_orders(response) if response else []

def get_basket_items(base_url: str, headers: dict, order_id: str) -> List[BasketItem]:
    url = f"{base_url}/sale.basketitem.list/"
    payload = {"filter": {"orderId": order_id}}
    response = fetch_data(url, headers, payload)
    return parse_basket_items(response) if response else []

def calculate_time_for_items(total_items: int) -> str:
    total_minutes = total_items * 5
    time_delta = timedelta(minutes=total_minutes)
    days, seconds = time_delta.days, time_delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{days} days {hours} hours {minutes} minutes"

def main(base_url: str, headers: dict, order_number: str, from_date: Optional[str] = None, until_date: Optional[str] = None):
    logging.info(f"Fetching order by number: {order_number}")
    order = get_order_by_number(base_url, headers, order_number)
    if not order:
        logging.error("Order not found.")
        return

    order_date = order['dateInsert']
    logging.info(f"Order date: {order_date}")

    logging.info("Fetching pending orders before the given order date")
    pending_orders = get_orders_by_status_before_date(base_url, headers, OrderStatus.PENDING.value, order_date)

    if from_date or until_date:
        pending_orders = [order for order in pending_orders if (not from_date or order['dateInsert'] >= from_date) and (not until_date or order['dateInsert'] <= until_date)]

    total_items = 0
    for order in pending_orders:
        logging.info(f"Fetching basket items for order ID: {order['id']}")
        basket_items = get_basket_items(base_url, headers, order['id'])
        total_items += sum(float(item['quantity']) for item in basket_items)

    time_needed = calculate_time_for_items(total_items)
    logging.info(f"Total time needed: {time_needed}")

base_url = "https://vlotho.ru/rest/13202/yd0cah2o4ywvd747"
headers = {'Content-Type': 'application/json'}

order_number = "5609"  # Replace with the actual order number
# from_date = "2024-01-01"  # Optional
# until_date = "2024-06-10"  # Optional

main(base_url, headers, order_number)
