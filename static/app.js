async function fetchOrderInfo() {
    const orderId = document.getElementById('order_id').value;
    const fromDate = document.getElementById('from_date').value;
    const untilDate = document.getElementById('until_date').value;
    const resultDiv = document.getElementById('result');

    resultDiv.innerHTML = `
        <div class="flex justify-center items-center">
            <div class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4"></div>
        </div>
    `;

    let url = `/orders?order_id=${orderId}`;
    if (fromDate) {
        url += `&from_date=${fromDate}`;
    }
    if (untilDate) {
        url += `&until_date=${untilDate}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();
        if (response.ok) {
            resultDiv.innerHTML = renderOrderDetails(data);
        } else {
            resultDiv.innerHTML = `<div class="text-red-500">Error: ${data.error}</div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="text-red-500">Error: ${error.message}</div>`;
    }
}

function renderOrderDetails(data) {
    const orderDetails = data.order_details.map(detail => `
        <div class="bg-white shadow-md rounded-lg p-4 mb-4">
            <p><strong>Order ID:</strong> ${detail.order_id}</p>
            <p><strong>Items:</strong> ${detail.items}</p>
            <p><strong>Time:</strong> ${detail.time}</p>
        </div>
    `).join('');

    return `
        <div>
            <h2 class="text-xl font-bold mb-4">Order Details</h2>
            ${orderDetails}
            <div class="bg-white shadow-md rounded-lg p-4">
                <p><strong>Total Items:</strong> ${data.total_items}</p>
                <p><strong>Total Time:</strong> ${data.total_time}</p>
            </div>
        </div>
    `;
}

