import React from "react";
import { Link } from "react-router-dom";
import { PaymentStatus } from "../components/payments/PaymentStatus";

export default function CheckoutSuccess() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <PaymentStatus
            status="paid"
            amount={0} // We might not have the amount here unless passed via params
            transactionId="Processing..."
          />
          <div className="mt-6">
            <Link
              to="/app/dashboard"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Return to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
