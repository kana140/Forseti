import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { SearchBar } from "@/components/search-bar";
import { Card, CardHeader } from "@/components/ui/card";

export default function ForumPage() {
  let mockForumData = [
    {
      user: "Hale The Idiot Anana",
      post: "I think I am stupid",
      timestamp: "03/10/2025 12:00:00",
    },
    {
      user: "Craig The FAT Anana",
      post: "I think I am fat",
      timestamp: "03/10/2025 12:00:10",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <section className="py-20 bg-gradient-to-b from-navy-900 to-navy-800">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center text-center space-y-4">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-white">
                Welcome to the forum! 🚀
              </h1>
              <p className="mx-auto max-w-[700px] text-zinc-200 md:text-xl">
                Search for topics
              </p>
              <div className="w-full max-w-2xl mx-auto mt-6">
                {/* <SearchBar fetchData={fetchData} setIsLoading={setIsLoading} /> */}
              </div>
            </div>
          </div>
        </section>
        <section className="py-12">
          <div className="container px-4 md:px-6">
            {/* <SearchResults data={data} isLoading={isLoading} /> */}
            {/* temporary search results, make the searchresults/searchbar modular */}
            {mockForumData.map((mockData) => {
              return (
                <Card>
                  {" "}
                  {mockData.user}
                  {mockData.post}
                  {mockData.timestamp}
                  <CardHeader></CardHeader>
                </Card>
              );
            })}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
