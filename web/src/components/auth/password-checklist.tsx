import { Check, Circle } from "lucide-react";
import { passwordRules } from "@/lib/auth/schemas";

export function PasswordChecklist({ value }: { value: string }) {
  return (
    <ul aria-label="Yêu cầu mật khẩu" className="grid grid-cols-1 gap-x-4 gap-y-1.5 sm:grid-cols-2">
      {passwordRules.map((rule) => {
        const met = rule.test(value);
        const Icon = met ? Check : Circle;
        return (
          <li
            key={rule.id}
            data-met={met}
            className={`flex items-center gap-2 text-[13px] ${met ? "text-herb" : "text-muted-foreground"}`}
          >
            <Icon aria-hidden className="size-3.5 shrink-0" />
            {rule.label}
            <span className="sr-only">{met ? " (đã đạt)" : " (chưa đạt)"}</span>
          </li>
        );
      })}
    </ul>
  );
}
