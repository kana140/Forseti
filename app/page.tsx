"use client";
import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { SearchBar } from "@/components/search-bar";
import { SearchResults } from "@/components/search-results";
import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

interface SearchData {
  data: object;
  searchQuery: string;
}

function HomeContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get("q") ?? "";

  const [data, setData] = useState<SearchData>({ data: {}, searchQuery: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [popularQueries, setPopularQueries] = useState<string[]>([]);
  const cache = useRef(new Map());

  useEffect(() => {
    const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
    fetch(`${API_URL}/api/popular`)
      .then((res) => res.json())
      .then((result) => setPopularQueries(result.queries ?? []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!query) {
      setData({ data: {}, searchQuery: "" });
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setData((prev) => ({ ...prev, searchQuery: query }));

    if (cache.current.has(query)) {
      setData(cache.current.get(query));
      setIsLoading(false);
      return;
    }

    const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
    fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        cache.current.set(query, result);
        setIsLoading(false);
      });
  }, [query]);

  function handlePopularSearch(q: string) {
    router.push(`/?q=${encodeURIComponent(q)}`);
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
                Search across multiple sourcing sites to find the best prices
                and availability for electronic components.
              </p>
              <div className="w-full max-w-2xl mx-auto mt-6">
                <SearchBar />
              </div>
            </div>
          </div>
        </section>
        <section className="py-12">
          <div className="container px-4 md:px-6">
            <SearchResults
              data={data}
              isLoading={isLoading}
              popularQueries={popularQueries}
              onPopularSearch={handlePopularSearch}
            />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default function Home() {
  return (
    <Suspense>
      <HomeContent />
    </Suspense>
  );
}
