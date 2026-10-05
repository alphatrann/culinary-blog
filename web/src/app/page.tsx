import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-start justify-center gap-4 p-8">
      <h1 className="text-3xl font-semibold">🍜 Culinary Blog</h1>
      <p className="text-muted-foreground">Recipe-sharing platform. Frontend scaffold.</p>
      <Button>Browse recipes</Button>
    </main>
  );
}
