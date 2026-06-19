# AI Receipt Parser

An intelligent, multi-modal travel receipt parser that automatically extracts and validates expense claim data from receipt images and PDFs using advanced OCR and local LLM technology.

---

## 📋 About

The **AI Receipt Parser** is a sophisticated document processing system designed for corporate travel expense management. It leverages computer vision (OCR) and large language models to automatically extract structured data from physical travel receipts, eliminating manual data entry and reducing processing time.

The system is built with **intelligence and validation at its core** - it doesn't just extract data, it validates it against mode-specific rules (flights, trains, cabs, buses) and self-corrects when anomalies are detected through a multi-pass refinement pipeline.

**Key Problem Solved**: Corporate reimbursement teams spend hours manually reviewing and transcribing receipt data. This tool automates 90% of the work while maintaining high accuracy through intelligent validation.

---

## 🛠️ Built With

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool and dev server
- **Axios** - HTTP client for API communication
- **LocalStorage API** - Client-side data persistence

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.x** - Core backend language
- **EasyOCR** - GPU-accelerated optical character recognition
- **Ollama** - Local LLM inference engine
- **Qwen2.5 (1.5B)** - Lightweight language model for extraction
- **PyMuPDF (fitz)** - PDF document processing
- **Pillow (PIL)** - Image processing and optimization
- **Pydantic** - Data validation and schema management

### Infrastructure
- **CORS Middleware** - Secure cross-origin communication
- **GPU Support** - CUDA-enabled EasyOCR for fast processing

---

## ⚙️ Tech Stack Overview

| Component | Technology |
|-----------|-----------|
| **Frontend Framework** | React + TypeScript + Vite |
| **Backend Framework** | FastAPI |
| **OCR Engine** | EasyOCR (GPU-accelerated) |
| **LLM Model** | Ollama + Qwen2.5:1.5b |
| **Document Processing** | PyMuPDF + Pillow |
| **Data Validation** | Pydantic BaseModel |
| **State Management** | React Hooks + localStorage |
| **API Communication** | RESTful with Axios |

---

## 🔄 Project Workflow

### Three-Phase Intelligent Pipeline

#### **Phase 1: Spatial OCR Layout Generation**
```
Receipt Image/PDF
    ↓
[Sanitization Layer]
  - Convert PDF → Image (120 DPI)
  - Compress oversized images (max 1000×1000px)
  - Convert to RGB format
  - Optimize JPEG quality
    ↓
[EasyOCR Engine]
  - Extract text with coordinate bounding boxes
  - Preserve spatial relationships
  - Sort by Y-coordinate to maintain layout
    ↓
Structured Text (with line breaks)
```

#### **Phase 2: Base LLM Extraction**
```
Structured OCR Text
    ↓
[Qwen2.5 LLM - First Pass]
  - Temperature: 0.0 (deterministic)
  - Input: Raw OCR text + detailed field instructions
  - Output: JSON object with 12 fields
    ↓
Raw Extracted Data
```

#### **Phase 3: Intelligent Validation & Self-Correction**
```
Extracted JSON
    ↓
[Mode-Aware Validation Engine]

IF mode = "Flight":
  ✓ Passenger name: Remove frequent flyer tier/card clutter
  ✓ PNR: Must be 6-char alphanumeric
  ✓ Cities: Cannot be identical
  ✓ Amount: Cross-validate with OCR digits

IF mode = "Train" (Indian Railways):
  ✓ Passenger name: Filter out waitlist codes (WL, CNF, RAC, etc.)
  ✓ PNR: Must be exactly 10 digits
  ✓ Cities: Cannot be identical
  ✓ Amount: Cross-validate with OCR digits

IF mode = "Cab":
  ✓ PNR: Optional
  ✓ Destination: Can be null (local trips)
  ✓ Amount: Required

    ↓
[Anomaly Detection]
  - Are any fields flagged as invalid?
    
    IF YES → Trigger Reflection Pass:
    ┌─────────────────────────────────┐
    │ Phase 3b: Correction Pass (LLM) │
    │ ─────────────────────────────────│
    │ Input: Only flagged fields +    │
    │ mode-specific correction rules  │
    │ Output: Corrected JSON subset   │
    │ Merge back into original object │
    └─────────────────────────────────┘
    
    IF NO → Proceed to response
    
    ↓
[Final Reconciled Data]
  - Performance metrics logged
  - JSON returned to frontend
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/TypeScript)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Upload Form         ← LocalStorage (crm_active_...) │   │
│  │  File Input          → Axios POST /api/parser/upload │   │
│  │  Auto-Populate Form  ← Response JSON                 │   │
│  │  Manual Corrections  → localStorage Sync             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI/Python)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ POST /api/parser/upload                              │   │
│  │ ├─ Phase 1: OCR (EasyOCR)                           │   │
│  │ ├─ Phase 2: Extraction (Qwen2.5 LLM)               │   │
│  │ ├─ Phase 3: Validation & Reflection                │   │
│  │ └─ Response: Extracted Data + Performance Metrics   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Extracted Data Fields

The parser extracts 12 structured fields from travel receipts:

| Field | Type | Example | Required |
|-------|------|---------|----------|
| `invoice_number` | String | "INV-2024-001234" | No |
| `passenger_name` | String | "JOHN DOE" | Yes (Flight/Train) |
| `ticket_pnr` | String | "ABC123" | Yes (Flight), 10-digit (Train) |
| `claim_date` | String (YYYY-MM-DD) | "2024-06-15" | Yes |
| `travel_date_from` | String (YYYY-MM-DD) | "2024-06-16" | Yes |
| `travel_date_to` | String (YYYY-MM-DD) | "2024-06-18" | Yes |
| `from_city` | String | "DEL" / "Delhi" | Yes (Flight/Train) |
| `to_city` | String | "BOM" / "Mumbai" | Yes (Flight/Train) |
| `purpose` | String | "Business Conference" | No |
| `mode_of_travel` | Enum | "Flight" / "Train" / "Cab" / "Bus" | Yes |
| `total_amount` | Float | 15500.00 | Yes |
| `payment_mode` | String | "Credit Card" / "UPI" / "Cash" | Yes |

---

## 💼 Use Cases

### 1. **Corporate Travel Reimbursement**
Streamline employee expense claims by automatically extracting receipt data. Reduce manual data entry time from hours to minutes and improve accuracy.

### 2. **CRM Integration**
Auto-populate travel expense records directly into CRM systems. Maintain a structured, queryable database of all corporate travel for analytics and reporting.

### 3. **Multi-Modal Travel Support**
Handle diverse receipt formats:
- **Flights**: Extract PNR, passenger tier, destination pairs
- **Trains**: Validate Indian Railway PNR format, filter waitlist codes
- **Cabs**: Simplified extraction, no PNR validation
- **Buses**: Similar to flights with flexible validation

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** (Backend)
- **Node.js 16+** (Frontend)
- **Ollama** installed with Qwen2.5 model downloaded
- **CUDA-capable GPU** (recommended for EasyOCR performance)

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   cd receipt_backend
   pip install fastapi uvicorn easyocr torch pillow pydantic ollama python-multipart
   ```

2. **Start Ollama service** (if not already running):
   ```bash
   ollama serve
   ```

3. **Download Qwen2.5 model**:
   ```bash
   ollama pull qwen2.5:1.5b
   ```

4. **Run the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies**:
   ```bash
   cd receipt_frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

### Testing the Application

1. Navigate to `http://localhost:5173` in your browser
2. Upload a travel receipt image or PDF
3. Click **"Upload & Parse Receipt"**
4. View auto-populated form data
5. Make manual corrections if needed (auto-saves to localStorage)
6. Submit the form data to your CRM/expense system

---

## 📈 Performance Characteristics

The pipeline logs performance metrics for each phase:

- **OCR Layer**: ~4-6 seconds (depends on image resolution)
- **Base LLM Pass**: ~5-8 seconds (Qwen2.5 inference)
- **Reflection Pass**: ~1-1.5 seconds (if validation fails)
- **Total Roundtrip**: ~8-15 seconds (end-to-end)

**GPU acceleration** significantly reduces OCR latency. CPU-only mode will be 3-5x slower.

---

## 🔐 Security & Architecture

- **CORS Policy**: Restricted to `http://localhost:5173` in development
- **File Validation**: Accepts only images and PDFs; validates MIME types
- **No Cloud Dependencies**: All processing is local (Ollama, EasyOCR) - no data sent to external APIs
- **Stateless Backend**: Each request is independent; no user sessions or authentication required (add as needed)

---

## 📝 Project Structure

```
ai-receipt-parser/
├── receipt_backend/
│   ├── main.py                 # FastAPI app & core pipeline
│   ├── schemas.py              # Pydantic models
│   └── temp_storage/           # Temporary file cache
│
├── receipt_frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── types.ts           # TypeScript interfaces
│   │   ├── main.tsx           # React entry point
│   │   ├── index.css          # Global styles
│   │   └── App.css            # Component styles
│   ├── index.html             # HTML template
│   ├── package.json           # npm dependencies
│   ├── vite.config.ts         # Vite configuration
│   └── tsconfig.json          # TypeScript configuration
│
├── audit.py                    # (Utility script - for audit logic testing)
└── readme.md                   # This file
```

---

## 🔧 Configuration

### Backend (FastAPI)
- **Host**: `localhost`
- **Port**: `8000`
- **Allowed Origins**: `http://localhost:5173`
- **OCR GPU**: Enabled by default (set `gpu=False` in `main.py` if CPU-only)
- **LLM Model**: `qwen2.5:1.5b` (configurable in `main.py`)
- **LLM Temperature**: `0.0` (deterministic extraction)

### Frontend (React/Vite)
- **Host**: `localhost`
- **Port**: `5173`
- **API Base URL**: `http://localhost:8000`
- **LocalStorage Key**: `crm_active_receipt_claim`

---

## 🐛 Troubleshooting

### Backend won't start
- Ensure Ollama service is running: `ollama serve`
- Verify Qwen2.5 is downloaded: `ollama list`
- Check Python dependencies: `pip install -r requirements.txt`

### Frontend shows CORS errors
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in `main.py`

### OCR is slow
- Enable GPU: Install CUDA and restart Ollama
- Verify GPU availability: Check EasyOCR logs during startup

### LLM not extracting data correctly
- Verify OCR text quality (check logs for raw OCR output)
- Test with a clearer receipt image
- Adjust LLM model or temperature settings in `main.py`

---


## Author

praanesh v a 
