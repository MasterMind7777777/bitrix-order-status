from flask import Flask, request, jsonify, send_from_directory
from bitrix_api import get_order_by_id, get_orders_by_status_before_date, get_basket_items, calculate_time_for_items
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/orders', methods=['GET'])
def get_orders():
    base_url = "https://vlotho.ru/rest/13202/yd0cah2o4ywvd747"
    headers = {'Content-Type': 'application/json'}
    
    order_id = request.args.get('order_id')
    from_date = request.args.get('from_date')
    until_date = request.args.get('until_date')
    
    if not order_id:
        return jsonify({"error": "Missing order_id parameter"}), 400
    
    order = get_order_by_id(base_url, headers, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    order_date = order['dateInsert']
    
    pending_orders = get_orders_by_status_before_date(base_url, headers, "P", order_date)
    
    if from_date or until_date:
        pending_orders = [order for order in pending_orders if (not from_date or order['dateInsert'] >= from_date) and (not until_date or order['dateInsert'] <= until_date)]
    
    total_items = 0
    order_details = []

    for order in pending_orders:
        basket_items = get_basket_items(base_url, headers, order['id'])
        item_count = sum(float(item['quantity']) for item in basket_items)
        time_needed = calculate_time_for_items(item_count)
        total_items += item_count
        order_details.append({
            "order_id": order['id'],
            "items": item_count,
            "time": time_needed
        })
    
    total_time = calculate_time_for_items(total_items)
    
    response_data = {
        "order_details": order_details,
        "total_items": total_items,
        "total_time": total_time
    }
    
    return jsonify(response_data), 200

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

