"use client";
import type React from "react";
import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
  fetchData: (query: string) => Promise<void>;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
}

export function SearchBar({ fetchData, setIsLoading }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const MIN_SPINNER_TIME = 500; // ms

  // const handleSearch = (e: React.FormEvent) => {
  //   e.preventDefault();
  //   setIsLoading(true);
  //   setQuery(query); // trigger effect
  // };

  // useEffect(() => {
  //   if (!query) return;
  //   fetchData(query);
  // }, [query]);
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const startTime = Date.now();

    if (query) {
      fetchData(query).then(() => {
        const elapsed = Date.now() - startTime;
        const remaining = MIN_SPINNER_TIME - elapsed;
        if (remaining > 0) {
          setTimeout(() => setIsLoading(false), remaining);
        } else {
          setIsLoading(false);
        }
      });
    }
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
