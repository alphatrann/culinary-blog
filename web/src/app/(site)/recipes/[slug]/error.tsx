"use client";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function RecipeError({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto w-full max-w-[1200px] px-4 py-16 sm:px-8">
      <EmptyState
        title="Không tải được công thức"
        description="Đã có lỗi khi tải trang. Kiểm tra kết nối rồi thử lại nhé."
        action={<Button onClick={reset}>Thử lại</Button>}
      />
    </main>
  );
}
