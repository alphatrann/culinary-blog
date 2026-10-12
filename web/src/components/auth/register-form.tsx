"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { PasswordChecklist } from "@/components/auth/password-checklist";
import { PasswordInput } from "@/components/auth/password-input";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldHint, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { mapAuthError } from "@/lib/auth/errors";
import { safeNext } from "@/lib/auth/redirect";
import { registerSchema, type RegisterValues } from "@/lib/auth/schemas";

export function RegisterForm({ next }: { next?: string | null }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [banner, setBanner] = useState<string>();
  const {
    register,
    handleSubmit,
    setError,
    control,
    formState: { errors },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { password: "" },
  });
  const password = useWatch({ control, name: "password" }) ?? "";

  const signUp = useMutation({
    mutationFn: (body: RegisterValues) => api.post("/auth/register", { body }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["auth"] });
      router.replace(safeNext(next) ?? "/");
      router.refresh();
    },
    onError: (error) => {
      const failure = mapAuthError(error, "register");
      setBanner(failure.banner);
      for (const [field, message] of Object.entries(failure.fields)) {
        setError(field as keyof RegisterValues, { message });
      }
    },
  });

  return (
    <form
      noValidate
      onSubmit={handleSubmit((values) => {
        setBanner(undefined);
        signUp.mutate(values);
      })}
      className="flex flex-col gap-5"
    >
      {banner && <Alert>{banner}</Alert>}
      <Field>
        <Label htmlFor="display_name">Tên hiển thị</Label>
        <Input
          id="display_name"
          autoComplete="name"
          placeholder="Ví dụ: Minh Anh"
          aria-invalid={!!errors.display_name}
          aria-describedby="display_name-hint display_name-error"
          {...register("display_name")}
        />
        <FieldHint id="display_name-hint">Từ 2 đến 100 ký tự.</FieldHint>
        <FieldError id="display_name-error">{errors.display_name?.message}</FieldError>
      </Field>
      <Field>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="ban@example.com"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? "email-error" : undefined}
          {...register("email")}
        />
        <FieldError id="email-error">{errors.email?.message}</FieldError>
      </Field>
      <Field>
        <Label htmlFor="password">Mật khẩu</Label>
        <PasswordInput
          id="password"
          autoComplete="new-password"
          placeholder="Tạo mật khẩu"
          aria-invalid={!!errors.password}
          aria-describedby="password-rules password-error"
          {...register("password")}
        />
        <div id="password-rules">
          <PasswordChecklist value={password} />
        </div>
        <FieldError id="password-error">{errors.password?.message}</FieldError>
      </Field>
      <Button type="submit" disabled={signUp.isPending}>
        {signUp.isPending ? "Đang tạo tài khoản…" : "Tạo tài khoản"}
      </Button>
      <p className="text-[13px] text-muted-foreground">
        Bằng việc tạo tài khoản, bạn đồng ý với Điều khoản sử dụng.
      </p>
    </form>
  );
}
