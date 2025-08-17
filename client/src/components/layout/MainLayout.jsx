import NavBar from "../Navbar";
import Footer from "../Footer";

export default function MainLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
      <NavBar />
      <main className="flex-1 p-4 sm:p-6 max-w-5xl mx-auto">{children}</main>
      <Footer />
    </div>
  );
}
