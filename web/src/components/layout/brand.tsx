import Link from "next/link";
import { BowlIcon } from "@/components/icons/bowl-icon";

export const BRAND_NAME = "Bếp Nhỏ";

export function Brand({ asLink = true }: { asLink?: boolean }) {
  const content = (
    <>
      <BowlIcon className="text-primary" />
      {BRAND_NAME}
    </>
  );
  const cls = "flex items-center gap-2.5 font-heading text-2xl font-bold text-foreground";
  return asLink ? (
    <Link href="/" className={`${cls} min-h-11`}>
      {content}
    </Link>
  ) : (
    <div className={cls}>{content}</div>
  );
}
