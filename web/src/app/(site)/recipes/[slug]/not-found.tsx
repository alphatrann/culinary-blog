import Link from "next/link";
import { EmptyState } from "@/components/ui/empty-state";
import { buttonVariants } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="mx-auto w-full max-w-[1200px] px-4 py-16 sm:px-8">
      <EmptyState
        title="Không tìm thấy công thức"
        description="Công thức này không tồn tại hoặc chưa được đăng."
        action={
          <Link href="/" className={buttonVariants()}>
            Về trang chủ
          </Link>
        }
      />
    </main>
  );
}
