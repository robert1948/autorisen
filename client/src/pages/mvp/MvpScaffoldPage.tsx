import React from "react";
import { Link } from "react-router-dom";
import Footer from "../../components/Footer";

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
  const showFooter = access === "public";
  const handleOpenSupport = () => undefined;

  return (
    <>
      <div className="mx-auto max-w-3xl p-6">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="mt-2 text-sm text-gray-600">MVP scaffold — Spec: SYSTEM_SPEC §2.5</p>

        <div className="mt-4 rounded border border-gray-200 bg-white p-4 text-sm">
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
                className="rounded border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-50"
              >
                {l.label}
              </Link>
            ))}
          </div>
        )}
      </div>
      {showFooter && <Footer onOpenSupport={handleOpenSupport} />}
    </>
  );
}
