import io
import time  
import json
import base64
import re
import fitz # PyMuPDF
import easyocr 
from PIL import Image
from ollama import Client
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ReceiptExtractionSchema

app = FastAPI(title="AI Receipt Parser API")

# Configure CORS policies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Global Initializer (GPU Enabled)
print("Loading GPU-Accelerated EasyOCR engines...")
reader = easyocr.Reader(['en'], gpu=True) 
print("EasyOCR CUDA Engine online and ready!")

# ==========================================
# ADVANCED HELPER FUNCTIONS
# ==========================================
def sanitize_file_to_image(file_bytes: bytes, filename: str, content_type: str) -> bytes:
    try:
        if content_type == "application/pdf" or filename.lower().endswith('.pdf'):
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            first_page = pdf_document[0]
            pix = first_page.get_pixmap(dpi=120) 
            return pix.tobytes("png")
        else:
            img = Image.open(io.BytesIO(file_bytes))
            max_size = 1000
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="JPEG", quality=85)
            return output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File router failed: {str(e)}")

def extract_text_with_spatial_sorting(image_bytes: bytes) -> str:
    """
    Spatial Coordinate Text Reassembly:
    Retrieves coordinate bounding boxes from EasyOCR and groups words into 
    distinct horizontal rows based on their vertical positioning (Y-axis).
    """
    ocr_results = reader.readtext(image_bytes, detail=1)
    
    if not ocr_results:
        return ""
        
    # Pre-sort all text segments by their top-left Y-coordinate
    ocr_results.sort(key=lambda entry: entry[0][0][1])
    
    lines = []
    current_line = [ocr_results[0]]
    
    for entry in ocr_results[1:]:
        current_y = entry[0][0][1]
        baseline_y = current_line[-1][0][0][1]
        box_height = current_line[-1][0][2][1] - current_line[-1][0][0][1]
        
        if abs(current_y - baseline_y) < (box_height * 0.5):
            current_line.append(entry)
        else:
            current_line.sort(key=lambda item: item[0][0][0])
            lines.append(" ".join([item[1] for item in current_line]))
            current_line = [entry]
            
    current_line.sort(key=lambda item: item[0][0][0])
    lines.append(" ".join([item[1] for item in current_line]))
    
    return "\n".join(lines)

def extract_json_from_text(raw_text: str) -> dict:
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if not match:
        raise ValueError("Could not locate a valid JSON dictionary in the AI response.")
    return json.loads(match.group(0))

# ==========================================
# DETERMINISTIC VALIDATION LOGIC
# ==========================================
def audit_extracted_data(data: dict, raw_text: str) -> list:
    """
    Programmatically cross-checks the JSON object fields against text patterns.
    Rules change dynamically based on the mode of travel.
    """
    failed_fields = []
    mode = data.get("mode_of_travel", "")
    
    # 1. Passenger Name structural sanity check
    name = data.get("passenger_name")
    if name:
        if mode == "Flight" and any(keyword in name.upper() for keyword in ["FLYER", "BLUE", "TIER", "FREQUENT"]):
            failed_fields.append("passenger_name")
        # Catch Indian Train Waitlist/Berth clutter (e.g., "PQWL/12", "RAC", "LOWER")
        elif mode == "Train" and any(keyword in name.upper() for keyword in ["WL", "CNF", "PQWL", "RAC", "LOWER", "UPPER"]):
            failed_fields.append("passenger_name")
    else:
        # Cabs usually don't have names on standard meter receipts, but Flights/Trains must.
        if mode in ["Flight", "Train"]:
            failed_fields.append("passenger_name")

    # 2. Reference Number (PNR) Validation based on Mode
    pnr = data.get("ticket_pnr")
    if mode == "Flight":
        if not pnr:
            failed_fields.append("ticket_pnr")
        elif pnr:
            clean_pnr = pnr.replace(" ", "")
            if len(clean_pnr) > 8 or clean_pnr.isdigit():
                failed_fields.append("ticket_pnr")
    elif mode == "Train":
        # Indian Railway PNRs are exactly 10 digits
        if not pnr:
            failed_fields.append("ticket_pnr")
        elif pnr:
            clean_pnr = pnr.replace(" ", "")
            if not clean_pnr.isdigit() or len(clean_pnr) != 10:
                failed_fields.append("ticket_pnr")

    # 3. Destination City Check 
    if mode in ["Flight", "Train"]:
        if not data.get("to_city") or data.get("to_city") == data.get("from_city"):
            failed_fields.append("to_city")
            failed_fields.append("from_city")
    # Note: If mode == "Cab", it's fine if to_city is null (local trips)

    # 4. Total Amount Verification (Universal)
    amount = data.get("total_amount")
    if amount is None or amount == 0.0:
        failed_fields.append("total_amount")
    else:
        raw_digits = re.findall(r'\d{3,4}', raw_text.replace(" ", ""))
        if raw_digits:
            max_raw_digit = max([float(d) for d in raw_digits if d.isdigit()])
            if max_raw_digit > (amount * 2) and str(int(amount)) in raw_text.replace(" ", ""):
                failed_fields.append("total_amount")

    return list(set(failed_fields))

# ==========================================
# API ENDPOINTS
# ==========================================
@app.get("/")
def health_check():
    return {"status": "FastAPI local server is running and ready."}

@app.post("/api/parser/upload")
async def parse_receipt(file: UploadFile = File(...)):
    try:
        raw_bytes = await file.read()
        image_bytes = sanitize_file_to_image(raw_bytes, file.filename, file.content_type)
        
        # 1. Phase 1: Spatial OCR Layout Generation
        print(f"\n[START] Running layout-preserving OCR on {file.filename}...")
        start_ocr_time = time.time()
        structured_ocr_text = extract_text_with_spatial_sorting(image_bytes)
        ocr_latency = time.time() - start_ocr_time
        print(f"[SUCCESS] OCR Phase Complete.")
        
        local_client = Client(host='http://localhost:11434')
        
        # 2. Phase 2: Base Pass Execution
        print("Passing structured text to Qwen2.5 (Pass 1)...")
        start_base_time = time.time()
        
        base_prompt = f"""Extract data from the raw OCR text into a flat JSON object using these exact keys:
                        - "invoice_number": String or null.
                        - "passenger_name": Clean uppercase traveler name only. Remove frequent flyer card numbers or tiers.
                        - "ticket_pnr": 6-character alphanumeric Booking Reference / PNR string.
                        - "claim_date": Transaction/issuance date in YYYY-MM-DD format.
                        - "travel_date_from": First flight or trip departure date in YYYY-MM-DD format.
                        - "travel_date_to": Return/final landing arrival date in YYYY-MM-DD format.
                        - "from_city": Departure location origin airport/city.
                        - "to_city": Arrival destination airport/city string.
                        - "purpose": String or null.
                        - "mode_of_travel": Flat string only. Must be one of: ["Flight", "Train", "Cab", "Bus"].
                        - "total_amount": Float number total transaction value. Verify financial table summary blocks.
                        - "payment_mode": Clean medium classification string (e.g. ""UPI", Visa", "Cash", "Credit Card","Debit Card").

                        Raw OCR Text to parse:
                        {structured_ocr_text}

                        Output the final populated JSON object now:"""

        response = local_client.chat(
            model='qwen2.5:1.5b',
            messages=[
                {'role': 'system', 'content': 'You are a precise data extraction script. You only output a single, flat valid JSON object.'},
                {'role': 'user', 'content': base_prompt}
            ],
            options={'temperature': 0.0, 'num_predict': 256}
        )
        
        raw_ai_response = response['message']['content']
        extracted_data = extract_json_from_text(raw_ai_response)
        base_llm_latency = time.time() - start_base_time
        print(f"[SUCCESS] Base Pass Complete.")
        
        # 3. Phase 3: Programmatic Audit & Conditional Reflection Pass
        reflection_latency = 0.0
        failed_fields = audit_extracted_data(extracted_data, structured_ocr_text)
        
        if failed_fields:
            print(f"\n[ALERT] Audit flagged discrepancies in keys: {failed_fields}. Compiling targeted Correction Pass...")
            start_reflection_time = time.time()
            
            # Phase 3: Dynamic Instructions based on Mode
            mode = extracted_data.get("mode_of_travel", "")
            reflection_instructions = []
            
            if "ticket_pnr" in failed_fields:
                if mode == "Train":
                    reflection_instructions.append("- 'ticket_pnr': Extract the 10-digit numeric Indian Railways PNR.")
                else:
                    reflection_instructions.append("- 'ticket_pnr': Isolate the short 6-character alphanumeric alpha locator (e.g., 'HC76IW'), NOT the long numeric ticket string.")
            
            if "passenger_name" in failed_fields:
                if mode == "Train":
                    reflection_instructions.append("- 'passenger_name': Strip out booking status codes like 'PQWL', 'WL', 'CNF', and age numbers. Extract just the human name.")
                else:
                    reflection_instructions.append("- 'passenger_name': Strip table layout text like 'FREQUENT FLYER' or card IDs. Extract only the literal human name string.")
            
            if "total_amount" in failed_fields:
                reflection_instructions.append("- 'total_amount': Verify the absolute final balance total. Check if a leading digit was dropped due to layout columns.")
                
            if "to_city" in failed_fields or "from_city" in failed_fields:
                reflection_instructions.append("- 'from_city' & 'to_city': Read the sequential route list to match the starting location and target destination.")

            reflection_prompt = f"""You are reviewing a draft data extraction to correct specific key field errors. Fix the targeted fields by analyzing the raw OCR text.

Current incorrect/suspicious extractions:
{json.dumps({k: extracted_data.get(k) for k in failed_fields}, indent=2)}

### Targeted Correction Rules:
{"\n".join(reflection_instructions)}

Raw OCR Text Reference:
{structured_ocr_text}

Output a flat JSON object containing ONLY the corrected keys and their new verified values:"""

            correction_response = local_client.chat(
                model='qwen2.5:1.5b',
                messages=[
                    {'role': 'system', 'content': 'You are an error correction script. You only output a single flat JSON object.'},
                    {'role': 'user', 'content': reflection_prompt}
                ],
                options={'temperature': 0.0, 'num_predict': 150}
            )
            
            corrected_fields = extract_json_from_text(correction_response['message']['content'])
            
            # Merge fields back into original container object
            for key, val in corrected_fields.items():
                if key in extracted_data:
                    extracted_data[key] = val
                    
            reflection_latency = time.time() - start_reflection_time
            print("[SUCCESS] Discrepancies resolved and structural fields updated.")

        # 4. Pipeline Execution Summary Report
        print("\n" + "="*40)
        print("       PIPELINE PERFORMANCE REPORT      ")
        print("="*40)
        print(f" OCR Layer Latency       : {ocr_latency:.2f} seconds")
        print(f" Base LLM Pass Latency   : {base_llm_latency:.2f} seconds")
        print(f" Reflection Pass Latency : {reflection_latency:.2f} seconds")
        print(f" Total Engine Roundtrip  : {(ocr_latency + base_llm_latency + reflection_latency):.2f} seconds")
        print("="*40 + "\n")
        
        print("=== FINAL RECONCILED AI RESPONSE ===")
        print(json.dumps(extracted_data, indent=4))
        print("=====================================\n")
        
        return {
            "success": True,
            "filename": file.filename,
            "data": extracted_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Parser Error: {str(e)}")