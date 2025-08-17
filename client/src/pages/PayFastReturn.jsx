import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function PayFastReturn() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    // Optionally, you can use m_payment_id / pf_payment_id for showing a receipt
    const timer = setTimeout(() => navigate('/credits'), 3000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 text-center max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Completed</h1>
        <p className="text-gray-600 mb-4">Thank you! Your payment is being confirmed.</p>
        <p className="text-sm text-gray-500">You will be redirected back to Credits in a moment.</p>
      </div>
    </div>
  );
}
