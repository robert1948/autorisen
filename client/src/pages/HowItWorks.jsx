import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function HowItWorks() {
  const navigate = useNavigate();

  return (
    <section className="px-6 py-20 max-w-5xl mx-auto text-gray-800">
      <h2 className="text-4xl font-bold text-blue-700 mb-6 text-center">How CapeControl Works</h2>

      <p className="text-lg mb-6 text-center">
        CapeControl makes it easy to automate your workflows with smart AI agents.
        Here’s how you can get started:
      </p>

      <ol className="list-decimal list-inside mb-10 space-y-4 text-left max-w-3xl mx-auto">
        <li>
          <strong>Sign Up:</strong> Create your account and access your dashboard.
        </li>
      </ol>

      <div className="flex justify-center gap-4">
        <Button onClick={() => navigate("/register")}>Start Now</Button>
      </div>
    </section>
  );
}
