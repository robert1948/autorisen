import React from "react";

export default function SunbirdPilotMobile() {
  return (
    <div className="mx-auto max-w-md px-4 py-6">
      <h1 className="text-2xl font-semibold">Sunbird Pilot</h1>
      <p className="mt-2 text-sm opacity-80">
        Demo module (mobile-first). Connected features will appear here as they go live.
      </p>

      <div className="mt-6 space-y-4">
        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Electricity Monitoring</h2>
          <p className="mt-1 text-sm opacity-80">Coming next (P1)</p>
        </section>

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Water Monitoring</h2>
          <p className="mt-1 text-sm opacity-80">Coming next (P1)</p>
        </section>

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Alerts</h2>
          <p className="mt-1 text-sm opacity-80">Status + notifications (P1)</p>
        </section>
      </div>
    </div>
  );
}
