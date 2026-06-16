import { useState, useEffect } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import type { ReceiptExtractionData } from './types';
import axios from 'axios';

const initialFormValues: ReceiptExtractionData = {
  invoice_number: '',
  passenger_name: '',
  ticket_pnr: '',
  claim_date: '',
  travel_date_from: '',
  travel_date_to: '',
  from_city: '',
  to_city: '',
  purpose: '',
  mode_of_travel: '',
  total_amount: 0,
  payment_mode: '',
};

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [formData, setFormData] = useState<ReceiptExtractionData>(initialFormValues);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');

  // 1. REHYDRATION HOOK: Runs once when the component mounts in the browser
  useEffect(() => {
    const savedDataStr = localStorage.getItem('crm_active_receipt_claim');
    if (savedDataStr) {
      try {
        // Deserialization: Convert the flat text string back into a typed JavaScript object
        const parsedData: ReceiptExtractionData = JSON.parse(savedDataStr);
        setFormData(parsedData);
      } catch (e) {
        console.error("Failed to parse local storage cache data:", e);
      }
    }
  }, []);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setErrorMessage('');
    }
  };

  // 2. INPUT SYNC: Keeps local storage updated with any manual user typing/corrections
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const updatedValues = {
      ...formData,
      [name]: name === 'total_amount' ? Number(value) : value,
    };
    
    setFormData(updatedValues);
    // Write changes immediately to the browser database
    localStorage.setItem('crm_active_receipt_claim', JSON.stringify(updatedValues));
  };

  const handleUploadAndParse = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please select a valid receipt image file first.');
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');

    const uploadPayload = new FormData();
    uploadPayload.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/parser/upload', uploadPayload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        const extractedClaim: ReceiptExtractionData = response.data.data;
        setFormData(extractedClaim);
        
        // 3. PERSIST REWARD DATA: Serialize and commit the newly extracted AI results
        localStorage.setItem('crm_active_receipt_claim', JSON.stringify(extractedClaim));
      } else {
        setErrorMessage('Data processing returned an unexpected payload structure.');
      }
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Network validation handshake failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  // 4. RESET CACHE METHOD: Clears out all state inputs and flushes the localStorage vault
  const handleClearCache = () => {
    setFormData(initialFormValues);
    setFile(null);
    localStorage.removeItem('crm_active_receipt_claim');
  };

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '0 20px', fontFamily: 'sans-serif' }}>
      <h2>Enterprise CRM: Travel Receipt Parser</h2>
      <p style={{ color: '#666' }}>Upload your travel receipt image to auto-populate CRM claim items via Gemini Vision extraction.</p>
      
      <hr />

      {/* Upload Interface Section */}
      <form onSubmit={handleUploadAndParse} style={{ marginBottom: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '6px' }}>
        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Select Receipt Document:</label>
        <input type="file" accept="image/*" onChange={handleFileChange} style={{ marginBottom: '15px' }} />
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit" disabled={isProcessing} style={{ padding: '10px 20px', background: '#0070f3', color: '#fff', border: 'none', borderRadius: '4px', cursor: isProcessing ? 'not-allowed' : 'pointer' }}>
            {isProcessing ? 'AI Processing Engine Running...' : 'Upload & Parse Receipt'}
          </button>
          
          <button type="button" onClick={handleClearCache} style={{ padding: '10px 20px', background: '#ba000d', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Clear Persistent Cache
          </button>
        </div>
      </form>

      {errorMessage && <p style={{ color: 'red', fontWeight: 'bold' }}>{errorMessage}</p>}

      {/* Auto-Populating Form Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Invoice/Receipt Number</label>
          <input type="text" name="invoice_number" value={formData.invoice_number || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Passenger Name</label>
          <input type="text" name="passenger_name" value={formData.passenger_name || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Ticket/PNR Number</label>
          <input type="text" name="ticket_pnr" value={formData.ticket_pnr || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Claim Date</label>
          <input type="text" name="claim_date" value={formData.claim_date || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Travel Date From</label>
          <input type="text" name="travel_date_from" value={formData.travel_date_from || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Travel Date To</label>
          <input type="text" name="travel_date_to" value={formData.travel_date_to || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>From City</label>
          <input type="text" name="from_city" value={formData.from_city || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>To City</label>
          <input type="text" name="to_city" value={formData.to_city || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Mode of Travel</label>
          <input type="text" name="mode_of_travel" value={formData.mode_of_travel || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Purpose of Trip</label>
          <input type="text" name="purpose" value={formData.purpose || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Total Amount</label>
          <input type="number" name="total_amount" value={formData.total_amount || 0} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontWeight: 'bold' }}>Payment Mode</label>
          <input type="text" name="payment_mode" value={formData.payment_mode || ''} onChange={handleInputChange} style={{ width: '100%', padding: '8px', marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
      </div>
    </div>
  );
}