import React from "react";
import { Link } from "react-router-dom";

type Access = "public" | "auth" | "onboarding" | "app" | "help";
type DataDependency = "none" | "read-only" | "write";

type NavLink = {
  to: string;
  label: string;
};

type Props = {
  title: string;
  route: string;
  access: Access;
  data: DataDependency;
  links?: NavLink[];
};

export default function MvpScaffoldPage({ title, route, access, data, links }: Props) {
  const linkClassName = (label: string) => {
    if (label === "Login") {
      return "inline-flex items-center justify-center rounded-md bg-white px-6 py-3 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-white/20 hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/70";
    }

    if (label === "Register") {
      return "inline-flex items-center justify-center rounded-md bg-transparent px-6 py-3 text-sm font-semibold text-white ring-1 ring-white/40 hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/70";
    }

    return "inline-flex items-center justify-center rounded border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-slate-900 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500/40";
  };

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="mt-2 text-sm text-gray-600">MVP scaffold — Spec: SYSTEM_SPEC §2.5</p>

      <div className="mt-4 rounded border border-gray-200 bg-white p-4 text-sm text-slate-900">
        <div>Route: {route}</div>
        <div>Access: {access}</div>
        <div>Data: {data}</div>
      </div>

      {links && links.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-3">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={linkClassName(l.label)}
            >
              {l.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
