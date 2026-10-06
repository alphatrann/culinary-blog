"use client";

import * as React from "react";
import { Check, Printer, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";

function RecipeActions({ title }: { title: string }) {
  const [copied, setCopied] = React.useState(false);

  async function share() {
    const url = window.location.href;
    try {
      if (navigator.share) {
        await navigator.share({ title, url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      // User dismissed the share sheet or clipboard is blocked; nothing to recover.
    }
  }

  return (
    <div className="flex flex-wrap gap-2 print:hidden">
      <Button variant="outline" onClick={() => window.print()}>
        <Printer aria-hidden />
        In công thức
      </Button>
      <Button variant="outline" onClick={share}>
        {copied ? <Check aria-hidden /> : <Share2 aria-hidden />}
        {copied ? "Đã chép liên kết" : "Chia sẻ"}
      </Button>
      <span role="status" className="sr-only">
        {copied ? "Đã chép liên kết vào bộ nhớ tạm" : ""}
      </span>
    </div>
  );
}

export { RecipeActions };
