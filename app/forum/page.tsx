import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

export default function ForumPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow flex items-center justify-center">
        <div className="text-center py-12">
          <h1 className="text-3xl font-bold text-navy-900">Forum</h1>
          <p className="text-zinc-500 mt-2">Coming soon</p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
