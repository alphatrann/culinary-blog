import type { Metadata } from "next";
import { AuthShell } from "@/components/auth/auth-shell";
import { RegisterForm } from "@/components/auth/register-form";
import { safeNext, withNext } from "@/lib/auth/redirect";

export const metadata: Metadata = { title: "Tạo tài khoản" };

export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string | string[] }>;
}) {
  const next = safeNext((await searchParams).next);
  return (
    <AuthShell
      title="Tạo tài khoản"
      subtitle="Lưu công thức yêu thích và chia sẻ món ngon của bạn."
      switchPrompt="Đã có tài khoản?"
      switchLabel="Đăng nhập"
      switchHref={withNext("/auth/login", next)}
    >
      <RegisterForm next={next} />
    </AuthShell>
  );
}
