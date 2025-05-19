from typing import Optional, Dict
from pydantic import BaseModel

# --- Data Models ---
class OrderGenericDetailsResponse(BaseModel):
    """
    Response model for OrderGenericDetails endpoint.  The fields are made
    optional to support different levels of detail based on the seed.
    """
    order_id: int
    order_date: Optional[str] = None
    customer_name: Optional[str] = None
    items: Optional[list] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None  # ["pending", "processing", "shipped", "delivered"]
    tracking_id: Optional[str] = None  # Added for OrderTracking
    cancellation_reason: Optional[str] = None  # Added for OrderCancellation
    other_details: Optional[Dict] = None # Added for extra details


class OrderCancellationRequest(BaseModel):
    """Request model for OrderCancellation endpoint."""
    order_id: int
    reason: str


class OrderTrackingResponse(BaseModel):
    """Response model for OrderTracking endpoint."""
    order_id: int
    status: str
    tracking_events: list

class CodeVerifierResponse(BaseModel):
    """Response model for 2-step code verification endpoint."""
    order_id: int
    verified: bool
