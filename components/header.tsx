import Link from "next/link";
import { CircuitBoard } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="bg-navy-900 text-white">
      <div className="container px-4 md:px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <CircuitBoard className="h-6 w-6" />
            <span className="font-bold text-xl">Forseti</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6">
            {/* <Link href="/" className="text-sm font-medium hover:text-zinc-200">
              Home
            </Link> */}
            {/* <Link href="/" className="text-sm font-medium hover:text-zinc-200">
              About
            </Link>
            <Link href="#" className="text-sm font-medium hover:text-zinc-200">
              Suppliers
            </Link>
            <Link href="#" className="text-sm font-medium hover:text-zinc-200">
              Contact
            </Link> */}
          </nav>
          <div className="flex items-center space-x-2"></div>
        </div>
      </div>
    </header>
  );
}
