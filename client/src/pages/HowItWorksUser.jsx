import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function HowItWorksUser() {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-20 max-w-5xl mx-auto text-gray-800">
      <h2 className="text-4xl font-bold text-blue-700 mb-6 text-center">How CapeControl Works for Users</h2>

      <p className="text-lg mb-6 text-center">
        Getting started with CapeControl is simple and straightforward.
        Follow these steps to begin automating your workflows:
      </p>

      <ol className="list-decimal list-inside mb-10 space-y-4 text-left max-w-3xl mx-auto">
        <li>
          <strong>Complete the registration:</strong> Finish setting up your account with all necessary details.
        </li>
        <li>
          <strong>Go to your personal Dashboard:</strong> Access your customized control center to manage your AI agents.
        </li>
        <li>
          <strong>Follow the guide:</strong> Use our step-by-step instructions to get the most out of CapeControl.
        </li>
      </ol>

      <div className="flex justify-center gap-4">
        <Button onClick={() => navigate("/register")}>Complete Registration</Button>
        <Button variant="outline" onClick={() => navigate("/dashboard/user")}>Go to Dashboard</Button>
      </div>
    </section>
  );
}
