"use client";

import { useState } from "react";
import { SearchBar } from "@/components/search-bar";
import { SearchResults } from "@/components/search-results";
import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

interface SearchData {
  data: object;
  searchQuery: string;
}

export default function Home() {
  const [data, setData] = useState<SearchData>({
    data: {},
    searchQuery: "",
  });
  const [cache, setCache] = useState(new Map());
  const [isLoading, setIsLoading] = useState(false);

  async function fetchData(query: string): Promise<void> {
    if (cache.has(query)) {
      setData(cache.get(query));
      setIsLoading(false);
      return;
    }

    const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
    const requestUrl = `${API_URL}/api/search?q=${query}`;
    const response = await fetch(requestUrl);
    const result = await response.json();
    console.log(result);
    setData(result);
    setCache((prevCache) => new Map(prevCache).set(query, result));
    setIsLoading(false);
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <section className="py-20 bg-gradient-to-b from-navy-900 to-navy-800">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center text-center space-y-4">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-white">
                Find Electronic Components Instantly
              </h1>
              <p className="mx-auto max-w-[700px] text-zinc-200 md:text-xl">
                Search across multiple suppliers to find the best prices and
                availability for electronic components.
              </p>
              <div className="w-full max-w-2xl mx-auto mt-6">
                <SearchBar fetchData={fetchData} setIsLoading={setIsLoading} />
              </div>
            </div>
          </div>
        </section>
        <section className="py-12">
          <div className="container px-4 md:px-6">
            <SearchResults data={data} isLoading={isLoading} />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
