export interface ReceiptExtractionData {
  invoice_number: string;
  passenger_name: string;
  ticket_pnr: string;
  claim_date: string;
  travel_date_from: string;
  travel_date_to: string;
  from_city: string;
  to_city: string;
  purpose: string;
  mode_of_travel: string;
  total_amount: number;
  payment_mode: string;
}