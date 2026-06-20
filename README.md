# 📋 Receipt Parser - Enterprise Travel Receipt Extraction

An AI-powered travel receipt parsing system that automatically extracts structured data from receipt images using Google's Gemini Vision API. Built for enterprise CRM integration with real-time data extraction and persistent local caching.

---

## 📋 About

Receipt Parser is a full-stack application designed to streamline travel expense management by automatically extracting key information from receipt images. Using advanced computer vision capabilities, it identifies and structures travel metrics such as passenger names, dates, routes, and transaction totals for direct CRM integration.

**Key Capabilities:**
- Automatic optical recognition and extraction from receipt images
- Real-time AI-powered data parsing using Gemini Vision
- Client-side persistence layer for draft management
- Structured JSON response format for seamless system integration
- CORS-enabled backend for cross-domain communication

---

## 🛠️ Built With

### Frontend
- **React 18** - UI component framework
- **TypeScript** - Type-safe application code
- **Vite** - Lightning-fast build tool and dev server
- **Axios** - HTTP client for API communication
- **CSS Grid & Flexbox** - Responsive layout system

### Backend
- **FastAPI** - High-performance Python web framework
- **Google Gemini API** - Vision-based document extraction
- **Pydantic** - Data validation and schema definition
- **CORS Middleware** - Cross-origin resource sharing

---

## ⚙️ Tech Stack Overview

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + TypeScript | Interactive UI, form management |
| **Frontend Build** | Vite | Module bundling, HMR development |
| **HTTP Client** | Axios | API communication |
| **Backend** | FastAPI | REST API endpoints |
| **Validation** | Pydantic | Request/response schema enforcement |
| **AI Vision** | Google Gemini 2.5 Flash | Receipt image analysis |
| **Storage** | Browser localStorage | Client-side draft persistence |

---

## 🔄 Project Workflow

```
User Upload Receipt Image
         ↓
   [React Frontend]
         ↓
   Validate File
         ↓
   Send to Backend (multipart/form-data)
         ↓
   [FastAPI Backend]
         ↓
   Process with Gemini Vision API
         ↓
   Extract structured data
         ↓
   Return JSON response
         ↓
   [React Frontend]
         ↓
   Populate form fields
         ↓
   Cache to localStorage
         ↓
   Display to user for review/edit
```

---

## 📊 Extracted Data Fields

The system extracts and structures the following fields from receipt documents:

| Field | Type | Description |
|-------|------|-------------|
| `invoice_number` | string | Unique receipt/document identification number |
| `passenger_name` | string | Full name of traveler on ticket |
| `ticket_pnr` | string | Booking reference or PNR code |
| `claim_date` | string | Receipt issuance date (YYYY-MM-DD) |
| `travel_date_from` | string | Journey start date (YYYY-MM-DD) |
| `travel_date_to` | string | Journey end date (YYYY-MM-DD) |
| `from_city` | string | Departure city |
| `to_city` | string | Destination city |
| `purpose` | string | Business reason for trip |
| `mode_of_travel` | string | Transportation type (Flight, Train, Cab, Bus, etc.) |
| `total_amount` | float | Total transaction amount |
| `payment_mode` | string | Payment method (Credit Card, Cash, etc.) |

---

## 💼 Use Cases

- **Expense Management**: Automated receipt capture for employee reimbursement workflows
- **Travel Policy Compliance**: Validate trips against corporate travel policies
- **CRM Integration**: Auto-populate travel claim records in enterprise systems
- **Audit Trail**: Create standardized records for financial audits
- **Cost Center Allocation**: Extract routing and cost data for budget tracking
- **Data Entry Automation**: Eliminate manual receipt data entry

---

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.9+
- Google Gemini API key

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Receipt_Parser-main
```

#### 2. Backend Setup
```bash
cd receipt_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn google-genai pydantic python-multipart python-cors

# Set Google API key
export GOOGLE_API_KEY=your_api_key_here  # On Windows: set GOOGLE_API_KEY=your_api_key_here
```

#### 3. Frontend Setup
```bash
cd receipt_frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Run Backend Server
```bash
cd receipt_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs on:** `http://localhost:8000`  
**Frontend runs on:** `http://localhost:5173`

---

## 📈 Performance Characteristics

- **API Response Time**: ~2-5 seconds (dependent on image size and API latency)
- **Max File Size**: Browser default (typically 5GB), limited by multipart form-data
- **Concurrent Requests**: Single-threaded per user session, scales horizontally with multiple uvicorn workers
- **Local Cache**: ~10KB per cached receipt data in browser localStorage
- **AI Model**: Gemini 2.5 Flash - optimized for speed over maximum accuracy

---

## 🔐 Security & Architecture

### Authentication & Authorization
- **CORS Policy**: Restricted to `http://localhost:5173` in development
- **API Exposure**: Currently open; production deployments should implement API key authentication

### Data Handling
- **File Validation**: CORS checks multipart form-data headers
- **AI Processing**: Raw images sent to Google API; no local model storage required
- **Client-Side Caching**: localStorage stores extracted JSON only (no file data)
- **Transport Security**: Production deployments should use HTTPS

### Recommendations for Production
1. Implement API key authentication on backend endpoints
2. Add request rate limiting to prevent abuse
3. Use HTTPS for all client-server communication
4. Implement image file size validation and type checking
5. Add audit logging for all API calls
6. Encrypt sensitive data in localStorage or migrate to server-side sessions
7. Restrict CORS origins to approved production domains

---

## 📝 Project Structure

```
Receipt_Parser-main/
├── receipt_backend/
│   ├── main.py                          # FastAPI application & routes
│   ├── schemas.py                       # Pydantic data models
│   └── venv/                            # Python virtual environment
│
├── receipt_frontend/
│   ├── src/
│   │   ├── App.tsx                      # Main React component
│   │   ├── main.tsx                     # React entry point
│   │   ├── types.ts                     # TypeScript interfaces
│   │   ├── App.css                      # Application styles
│   │   ├── index.css                    # Global styles
│   │   └── assets/                      # Static assets
│   ├── public/                          # Public static files
│   ├── index.html                       # HTML template
│   ├── package.json                     # NPM dependencies
│   ├── tsconfig.json                    # TypeScript config
│   ├── vite.config.ts                   # Vite bundler config
│   └── eslint.config.js                 # ESLint rules
│
└── README.md                            # This file
```

---

## 🔧 Configuration

### Environment Variables (Backend)
```bash
# .env (create in receipt_backend/)
GOOGLE_API_KEY=your_gemini_api_key_here
```

### CORS Configuration (Backend)
Edit `main.py` to adjust allowed origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API Endpoint
Edit `src/App.tsx` to change backend URL:
```typescript
const response = await axios.post('http://localhost:8000/api/parser/upload', uploadPayload, {
  headers: { 'Content-Type': 'multipart/form-data' },
});
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: "Google API key not found"**
- Ensure `GOOGLE_API_KEY` environment variable is set
- Verify key is valid at https://console.cloud.google.com/

**Issue: "CORS error when frontend calls backend"**
- Check that backend is running on `http://localhost:8000`
- Verify frontend origin matches `allow_origins` in CORS middleware
- Ensure `Content-Type: multipart/form-data` header is sent

**Issue: "ModuleNotFoundError: No module named 'google'"**
- Run: `pip install google-genai`
- Verify virtual environment is activated

### Frontend Issues

**Issue: "File upload appears to hang"**
- Check network tab in browser DevTools for failed requests
- Ensure backend server is running and accessible
- Verify image file is under size limits

**Issue: "Form data not persisting after page refresh"**
- Check browser DevTools → Application → localStorage
- Verify `crm_active_receipt_claim` key exists
- Clear cache and try uploading receipt again

**Issue: "Vite dev server shows blank page"**
- Run: `npm install` to ensure all dependencies installed
- Check console for compilation errors
- Clear `.node_modules` and reinstall: `rm -rf node_modules && npm install`

### API Issues

**Issue: "Invalid JSON response from Gemini API"**
- Verify image contains readable receipt data
- Try uploading a different image
- Check Gemini API quota and rate limits

---

## Author

praanesh 
