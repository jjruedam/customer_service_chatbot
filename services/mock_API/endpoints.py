from fastapi import FastAPI, HTTPException, Query, Body
from services.mock_API.data_models import OrderGenericDetailsResponse, OrderCancellationRequest, OrderTrackingResponse, CodeVerifierResponse
from services.mock_API.data_mocking import generate_order_details, update_order_details
import random
import time

app = FastAPI(
    title="Mock Order Management API",
    description="This API mocks order management services for testing purposes.",
    version="1.0.0",
)

# --- API Endpoints ---
@app.get("/order/details", response_model=OrderGenericDetailsResponse)
async def get_order_details(order_id: int = Query(..., description="The ID of the order to retrieve."),
                           include_tracking: bool = Query(False, description="Include tracking information."),
                           include_cancellation: bool = Query(False, description="Include cancellation reason.")):
    """
    Retrieves generic details for a specific order.
    Demonstrates how a single endpoint can serve different data requirements.
    """
    # Use order_id as the seed for consistent results for the same order.
    order_details = generate_order_details(order_id)

    if include_tracking:
        order_details.tracking_id = f"TRACK-{order_id}-{random.randint(100, 999)}"
    if include_cancellation:
        if random.random() < 0.2:  # Simulate 20% chance of having been cancelled
            order_details.cancellation_reason = random.choice(["Customer request", "Item unavailable", "Payment issue"])
        else:
            order_details.cancellation_reason = None # Ensure no reason is included if not cancelled.

    return order_details



@app.post("/order/cancel", response_model=OrderGenericDetailsResponse)
async def cancel_order(cancellation_request: OrderCancellationRequest):
    """
    Cancels a specific order.  Returns order details, including cancellation reason.
    """
    order_id = cancellation_request.order_id
    reason = cancellation_request.reason

    # In a real application, you would update the order status in the database.
    # Here, we just mock the behavior.

    order_details = generate_order_details(order_id) # Get base order details

    if order_details.status not in ["shipped", "delivered"]:
        order_details.status = "cancelled"
        order_details.cancellation_reason = reason  # Store the provided reason.
    
    
    update_order_details(order_id,order_details)

    return order_details



@app.get("/order/track", response_model=OrderTrackingResponse)
async def track_order(order_id: int = Query(..., description="The ID of the order to track.")):
    """
    Retrieves tracking information for a specific order.
    """
    order_details = generate_order_details(order_id) # Get order details

    if not order_details.tracking_id:
        raise HTTPException(status_code=404, detail=f"Tracking information not found for order {order_id}")

    # Mock tracking events.
    num_events = random.randint(1, 4)
    tracking_events = [
        {
            "event": "Order placed",
            "timestamp": "2024-07-28T10:00:00",
        }
    ]
    if num_events > 1:
        tracking_events.append({"event": "Order processed", "timestamp": "2024-07-28T12:00:00"})
    if num_events > 2:
        tracking_events.append({"event": "Order shipped", "timestamp": "2024-07-29T08:00:00"})
    if num_events > 3:
        tracking_events.append({"event": "Order delivered", "timestamp": "2024-07-31T14:00:00"})

    return OrderTrackingResponse(
        order_id=order_id,
        status=order_details.status,
        tracking_events=tracking_events,
    )



@app.post("/security/send_2_steps_code")
async def send_2_steps_code(request: dict = Body(...)):
    """
    Send 2-steps code to email address associated with the order_id
    """
    # Extract order_id from the request body
    order_id = request.get("order_id")
    if not order_id:
        raise HTTPException(status_code=400, detail="order_id is required")
    
    
    return {"message": "2-step code sent successfully"}

    

@app.get("/security/verify_2_steps_code", response_model=CodeVerifierResponse)
async def verify_2_steps_code(
    order_id: int = Query(..., description="The ID of the order to retrieve."),
    code: int = Query(..., description="The 2-steps code sent.")
):
    """
    Verify the 2-steps code for the order with the given ID
    """
    # In production, you would compare against a code stored in your database
    # This is just a hard-coded example
    if code != 123654:
        return CodeVerifierResponse(order_id=order_id, verified=False)
    
    return CodeVerifierResponse(order_id=order_id, verified=True)
    


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)