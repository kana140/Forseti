"use client";
import type React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query) router.push(`/?q=${encodeURIComponent(query)}`);
  };

  return (
    <form onSubmit={handleSearch} className="relative w-full">
      <div className="relative flex items-center">
        <Input
          type="text"
          placeholder="Enter component part number (e.g., 1N4148W-TP)"
          value={query}
          onChange={(e) => setQuery(e.target.value.trim())}
          className="w-full pl-4 pr-12 py-6 rounded-lg bg-white text-navy-900 placeholder:text-zinc-400 focus-visible:ring-blue-500"
        />
        <Button
          type="submit"
          className="absolute right-1 bg-blue-500 hover:bg-blue-600 text-white"
        >
          <Search className="h-5 w-5" />
          <span className="sr-only">Search</span>
        </Button>
      </div>
    </form>
  );
}
