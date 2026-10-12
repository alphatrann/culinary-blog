"use client";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto w-full max-w-[1200px] space-y-6 px-4 py-8 sm:px-8">
      <h1 className="text-page font-bold">Tất cả công thức</h1>
      <Alert>
        <p className="font-semibold">Không tải được danh sách công thức</p>
        <p>Đã có lỗi xảy ra. Vui lòng thử lại.</p>
      </Alert>
      <Button onClick={reset}>Thử lại</Button>
    </main>
  );
}
