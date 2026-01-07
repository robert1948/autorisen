import React from "react";
import { Link } from "react-router-dom";
import { PaymentStatus } from "../../components/payments/PaymentStatus";

export default function CheckoutCancel() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <PaymentStatus
            status="cancelled"
            amount={0}
            transactionId="Cancelled"
          />
          <div className="mt-6 flex gap-4">
            <Link
              to="/app/checkout"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Try Again
            </Link>
            <Link
              to="/app/dashboard"
              className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
