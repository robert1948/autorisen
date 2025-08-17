import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function HowItWorksDeveloper() {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-20 max-w-5xl mx-auto text-gray-800">
      <h2 className="text-4xl font-bold text-blue-700 mb-6 text-center">How CapeControl Works for Developers</h2>

      <p className="text-lg mb-6 text-center">
        Getting started with CapeControl as a developer is simple and straightforward.
        Follow these steps to begin building and managing AI agents:
      </p>

      <ol className="list-decimal list-inside mb-10 space-y-4 text-left max-w-3xl mx-auto">
        <li>
          <strong>Complete the registration:</strong> Finish setting up your developer account with all necessary details.
        </li>
        <li>
          <strong>Go to your personal Dashboard:</strong> Access your developer control center to create and manage AI agents.
        </li>
        <li>
          <strong>Follow the guide:</strong> Use our comprehensive developer documentation to build powerful AI solutions.
        </li>
      </ol>

      <div className="flex justify-center gap-4">
        <Button onClick={() => navigate("/register")}>Complete Registration</Button>
        <Button variant="outline" onClick={() => navigate("/dashboard/developer")}>Go to Developer Dashboard</Button>
      </div>
    </section>
  );
}
