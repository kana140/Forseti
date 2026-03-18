import Link from "next/link";
import { CircuitBoard } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-navy-900 text-white py-12">
      <div className="container px-4 md:px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <CircuitBoard className="h-6 w-6" />
              <span className="font-bold text-xl">Forseti</span>
            </div>
            <p className="text-zinc-300 text-sm">
              The ultimate electronic component search engine. Find parts across
              multiple sourcing sites instantly.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/"
                  className="text-zinc-300 hover:text-white text-sm"
                >
                  Home
                </Link>
              </li>
              <li>
                <Link
                  href="#"
                  className="text-zinc-300 hover:text-white text-sm"
                >
                  About Us
                </Link>
              </li>
              <li>
                <Link
                  href="/forum"
                  className="text-zinc-300 hover:text-white text-sm"
                >
                  Forum
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-zinc-700 mt-8 pt-8 text-center text-zinc-300 text-sm">
          <p>&copy; {new Date().getFullYear()} Forseti. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
