"use client";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto max-w-[1200px] px-4 py-10 sm:px-8 sm:py-12">
      <EmptyState
        title="Không tải được trang"
        description="Đã có lỗi xảy ra. Bạn thử tải lại nhé."
        action={
          <Button variant="outline" onClick={reset}>
            Thử lại
          </Button>
        }
      />
    </main>
  );
}
