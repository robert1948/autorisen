import React from 'react';
import { Link } from 'react-router-dom';

export default function PayFastCancel() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-rose-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 text-center max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Cancelled</h1>
        <p className="text-gray-600 mb-4">Your payment was cancelled. No charges were made.</p>
        <Link className="text-blue-600 hover:underline" to="/credits">Back to Credits</Link>
      </div>
    </div>
  );
}
