import { useEffect, useState } from "react";

export default function CapeAIIntro() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => setShow(true), 1000);
    return () => clearTimeout(timeout);
  }, []);

  if (!show) return null;

  return (
    <div className="fixed bottom-6 right-6 max-w-sm bg-white border border-blue-200 shadow-lg rounded-xl p-4 animate-fade-in">
      <div className="flex items-start gap-3">
        <div className="text-blue-500 text-2xl">🤖</div>
        <div>
          <p className="font-semibold text-blue-700">Hi, I'm CapeAI.</p>
          <p className="text-sm text-gray-700 mt-1">
            I’ll help guide you through your business setup and agent tools. Ready when you are.
          </p>
        </div>
      </div>
    </div>
  );
}
