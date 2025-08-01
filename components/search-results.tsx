"use client";

import { Button } from "@/components/ui/button";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import Image from "next/image";
import { ChevronDown, ChevronUp } from "lucide-react";
import { ExternalLink } from "lucide-react";

interface SearchResultsProp {
  data: {
    data: object;
    searchQuery: string;
  };
  isLoading: boolean;
}

type Source = {
  website: string;
  name: string;
  url: string;
  listings: Listing[];
  logo?: string;
};

type Listing = {
  distributor: string;
  manufacturer: string;
  partNumber: string;
  stock: string;
  prices: quantityPrice[];
};

type quantityPrice = {
  quantity: string;
  price: string;
};

type ComponentResult = {
  partNumber: string;
  sources: Source[];
};

type RawWebsiteResult = {
  productData: any[]; // or replace `any` with the proper type if you have it
  websiteLink: string;
};

type RawApiData = {
  [partNumber: string]: {
    [website: string]: RawWebsiteResult;
  };
};

export function SearchResults({ data, isLoading }: SearchResultsProp) {
  const query = data.searchQuery;
  const [results, setResults] = useState<ComponentResult[]>([]);
  // const [loading, setLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<{
    [key: string]: boolean;
  }>({});

  useEffect(() => {
    if (data?.data) {
      const rawData = data.data as RawApiData;

      const transformedResults = Object.entries(rawData).map(
        ([partNumber, websites]) => ({
          partNumber,
          sources: Object.entries(websites).map(([website, websiteResult]) => {
            const site = websiteResult as RawWebsiteResult;

            return {
              website,
              name: website,
              url: site.websiteLink || "#",
              // logo: "/placeholder.svg",
              listings: (site.productData || []).map((p) => ({
                distributor: p.distributor || "Unknown Distributor",
                manufacturer: p.manufacturer || "Unknown Manufacturer",
                partNumber: p.distributorNo || partNumber,
                stock: p.stock || "N/A",
                prices: p.prices,
                link: p.link || "#",
              })),
            };
          }),
        })
      );

      setResults(transformedResults);
    }
  }, [data]);

  useEffect(() => {
    if (Object.keys(results).length > 0) {
      const newExpandedSources: { [key: string]: boolean } = {};

      results.forEach((component) => {
        component.sources.forEach((source, sourceIdx) => {
          const key = `${component.partNumber}-${sourceIdx}`;
          newExpandedSources[key] = sourceIdx === 0; // Expand first source of each component
        });
      });

      setExpandedSources(newExpandedSources);
    }
  }, [results]);

  if (!query) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-navy-900">Popular Components</h2>
        <p className="text-zinc-500 mt-2">
          Search for a component to see results
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          {["Microcontrollers", "Resistors", "Capacitors"].map((category) => (
            <Card key={category} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle>{category}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-zinc-500">
                  Browse popular {category.toLowerCase()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-navy-900">
            Searching for "{query}"
          </h2>
        </div>
        {[1, 2, 3].map((i) => (
          <Card key={i} className="w-full">
            <CardHeader>
              <Skeleton className="h-8 w-48" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <div className="pt-4">
                  <Skeleton className="h-24 w-full" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-navy-900">
          Results for "{query}"
        </h2>
        <p className="text-zinc-500">{results.length} components found</p>
      </div>

      {results.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-xl font-medium text-navy-900">
            No components found
          </h3>
          <p className="text-zinc-500 mt-2">
            Try a different search term or browse categories
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {results.map((component, id) => (
            <Card key={id} className="w-full">
              <CardHeader>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div>
                    <CardTitle className="text-navy-900">
                      {component.partNumber}
                    </CardTitle>
                    {/* <p className="text-zinc-500">{component.description}</p> */}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {component.sources.map((source, i) => {
                    const sourceKey = `${component.partNumber}-${i}`;
                    const isExpanded = expandedSources[sourceKey] || false;

                    return (
                      <div
                        key={i}
                        className="border rounded-lg overflow-hidden"
                      >
                        <div
                          className="bg-zinc-50 px-4 py-2 border-b flex justify-between items-center cursor-pointer hover:bg-zinc-100 transition-colors"
                          onClick={() =>
                            setExpandedSources({
                              ...expandedSources,
                              [sourceKey]: !isExpanded,
                            })
                          }
                        >
                          <div className="flex items-center gap-2">
                            <Image
                              src={
                                "/images/logos/" +
                                source.name.replace(".com", "").toLowerCase() +
                                ".png"
                              }
                              alt={source.name}
                              width={80}
                              height={20}
                              className="h-5 w-auto"
                            />
                            <h4 className="font-medium text-navy-900">
                              {source.name}
                            </h4>
                            <span className="text-xs text-zinc-500">
                              ({source.listings.length} listings)
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:underline text-xs flex items-center gap-1"
                              onClick={(e) => e.stopPropagation()}
                            >
                              View on {source.name}{" "}
                              <ExternalLink className="h-3 w-3" />
                            </a>
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-zinc-500" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-zinc-500" />
                            )}
                          </div>
                        </div>
                        {isExpanded && (
                          <div className="overflow-x-auto">
                            <table className="w-full border-collapse">
                              <thead>
                                <tr className="border-b bg-zinc-50">
                                  <th className="text-left py-2 px-3 text-xs">
                                    Distributor
                                  </th>
                                  <th className="text-left py-2 px-3 text-xs">
                                    Manufacturer
                                  </th>
                                  <th className="text-left py-2 px-3 text-xs">
                                    Part #
                                  </th>
                                  <th className="text-left py-2 px-3 text-xs">
                                    Stock
                                  </th>
                                  <th
                                    className="text-left py-2 px-3 text-xs"
                                    colSpan={3}
                                  >
                                    Price Breaks
                                  </th>
                                  <th className="text-left py-2 px-3 text-xs"></th>
                                </tr>
                              </thead>
                              <tbody>
                                {source.listings.map((listing, index) => (
                                  <tr
                                    key={index}
                                    className="border-b hover:bg-zinc-50"
                                  >
                                    <td className="py-2 px-3 font-medium text-xs">
                                      {listing.distributor}
                                    </td>
                                    <td className="py-2 px-3 text-xs">
                                      {listing.manufacturer}
                                    </td>
                                    <td className="py-2 px-3 text-xs">
                                      {listing.partNumber}
                                    </td>
                                    <td className="py-2 px-3 text-xs">
                                      {listing.stock}
                                    </td>
                                    <td className="py-2 px-3 text-xs">
                                      {listing.prices &&
                                      listing.prices.length > 0 ? (
                                        <div className="flex flex-col gap-1">
                                          {listing.prices
                                            .slice(0, 3)
                                            .map((pb, i) => (
                                              <div key={i}>
                                                <b>{pb.quantity}</b>: {pb.price}
                                              </div>
                                            ))}
                                        </div>
                                      ) : (
                                        <span className="text-zinc-400">
                                          No prices
                                        </span>
                                      )}
                                    </td>
                                    <td className="py-2 px-3">
                                      <Button
                                        size="sm"
                                        className="bg-blue-500 hover:bg-blue-600 text-white text-xs h-7 px-2"
                                      >
                                        Buy
                                      </Button>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
