import type { Metadata } from "next";
import Link from "next/link";
import { DashboardOverview } from "@/components/dashboard/overview";
import { buttonVariants } from "@/components/ui/button";

export const metadata: Metadata = { title: "Bảng điều khiển" };

export default function DashboardPage() {
  return (
    <main className="mx-auto flex w-full max-w-[1000px] flex-col gap-8 px-4 py-8 sm:px-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Bảng điều khiển</h1>
        <Link href="/dashboard/recipes/new" className={buttonVariants()}>
          Công thức mới
        </Link>
      </div>
      <DashboardOverview />
    </main>
  );
}
