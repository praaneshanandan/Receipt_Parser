import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from schemas import ReceiptExtractionSchema

app = FastAPI(title="AI Receipt Parser API")

# Configure CORS policies to grant authorization handshakes to the React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permit the explicit frontend domain origin
    allow_credentials=True,
    allow_methods=["*"],                      # Allow all HTTP verbs (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],                      # Allow all header formats
)

# Initialize the secure GenAI Client
ai_client = genai.Client()

@app.get("/")
def health_check():
    return {"status": "FastAPI server is running and ready."}

@app.post("/api/parser/upload")
async def upload_receipt(file: UploadFile = File(...)):
    try:
        # 1. Read incoming stream to capture raw binary contents
        file_bytes = await file.read()
        
        # 2. Package the binary data with its correct media format wrapper
        image_part = types.Part.from_bytes(
            data=file_bytes,
            mime_type=file.content_type
        )
        
        # 3. Execute the structured vision token extraction call
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                image_part, 
                "Extract all factual travel metrics from this document image. "
                "Isolate document identifiers, traveller names, dates, routing cities, and the transaction totals."
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReceiptExtractionSchema,  # Dynamically adapts to your modified schema structure
            ),
        )
        
        # 4. Safely unpack the generated string token payload into a clean JSON dictionary
        extracted_data = json.loads(response.text)
        
        return {
            "success": True,
            "filename": file.filename,
            "data": extracted_data
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI output generation failed structural validation formatting checks.")
    except Exception as e:
        # Catch any pipeline network faults or configuration exceptions safely
        raise HTTPException(status_code=500, detail=f"Internal Parser Error: {str(e)}")