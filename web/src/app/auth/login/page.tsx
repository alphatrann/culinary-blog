import type { Metadata } from "next";
import { AuthShell } from "@/components/auth/auth-shell";
import { LoginForm } from "@/components/auth/login-form";
import { safeNext, withNext } from "@/lib/auth/redirect";

export const metadata: Metadata = { title: "Đăng nhập" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string | string[] }>;
}) {
  const next = safeNext((await searchParams).next);
  return (
    <AuthShell
      title="Chào mừng trở lại"
      subtitle="Đăng nhập để lưu và đăng công thức của bạn."
      switchPrompt="Chưa có tài khoản?"
      switchLabel="Đăng ký"
      switchHref={withNext("/auth/register", next)}
    >
      <LoginForm next={next} />
    </AuthShell>
  );
}
