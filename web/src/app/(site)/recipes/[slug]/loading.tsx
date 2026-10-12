import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <main
      role="status"
      aria-label="Đang tải công thức"
      className="mx-auto w-full max-w-[1200px] px-4 py-6 sm:px-8"
    >
      <Skeleton className="h-5 w-64" />
      <Skeleton className="mt-6 h-6 w-24 rounded-full" />
      <Skeleton className="mt-4 h-12 w-3/4" />
      <Skeleton className="mt-3 h-5 w-1/2" />
      <Skeleton className="mt-8 aspect-[4/3] w-full rounded-xl sm:aspect-video" />
      <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, i) => (
          <Skeleton key={i} className="h-20 rounded-xl" />
        ))}
      </div>
      <div className="mt-12 grid gap-10 lg:grid-cols-[380px_1fr]">
        <Skeleton className="h-96 rounded-xl" />
        <div className="space-y-6">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      </div>
    </main>
  );
}
