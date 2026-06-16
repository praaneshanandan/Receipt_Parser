from pydantic import BaseModel, Field
from typing import Optional

class ReceiptExtractionSchema(BaseModel):
    """
    Refactored strict data contract mapping factual metrics 
    directly extracted from physical travel document layouts.
    """
    invoice_number: Optional[str] = Field(
        None, description="The unique invoice, document, or receipt identification number."
    )
    passenger_name: Optional[str] = Field(
        None, description="The full name of the employee or passenger listed on the travel ticket."
    )
    ticket_pnr: Optional[str] = Field(
        None, description="The booking reference, PNR code, or ticket number for the journey."
    )
    claim_date: Optional[str] = Field(
        None, description="The issuance date listed on the receipt (YYYY-MM-DD)."
    )
    travel_date_from: Optional[str] = Field(
        None, description="The departure or start date of the travel journey (YYYY-MM-DD)."
    )
    travel_date_to: Optional[str] = Field(
        None, description="The return or end date of the travel journey (YYYY-MM-DD)."
    )
    from_city: Optional[str] = Field(
        None, description="The starting or departure city of the travel."
    )
    to_city: Optional[str] = Field(
        None, description="The destination or arrival city."
    )
    purpose: Optional[str] = Field(
        None, description="The corporate or business reason for the trip if explicit."
    )
    mode_of_travel: Optional[str] = Field(
        None, description="The transportation medium used, e.g., Flight, Train, Cab, Bus."
    )
    total_amount: float = Field(
        0.0, description="The total transactional gross cost or net amount paid. Default to 0.0."
    )
    payment_mode: Optional[str] = Field(
        None, description="Method of payment used, e.g., Credit Card, Cash, Self-pay."
    )