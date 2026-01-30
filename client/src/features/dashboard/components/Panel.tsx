// Figma: DashboardPage/Panel

import type { ReactNode } from "react";

export type PanelProps = {
  title: string;
  children: ReactNode;
  action?: ReactNode;
};

export function Panel({ title, children, action }: PanelProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      <div className="px-4 py-3">{children}</div>
    </section>
  );
}
