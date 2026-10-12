"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { PasswordInput } from "@/components/auth/password-input";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldError, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { mapAuthError } from "@/lib/auth/errors";
import { safeNext } from "@/lib/auth/redirect";
import { loginSchema, type LoginValues } from "@/lib/auth/schemas";

export function LoginForm({ next }: { next?: string | null }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [banner, setBanner] = useState<string>();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  const login = useMutation({
    mutationFn: (body: LoginValues) => api.post("/auth/login", { body }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["auth"] });
      router.replace(safeNext(next) ?? "/");
      router.refresh();
    },
    onError: (error) => {
      const failure = mapAuthError(error, "login");
      setBanner(failure.banner);
      for (const [field, message] of Object.entries(failure.fields)) {
        setError(field as keyof LoginValues, { message });
      }
    },
  });

  return (
    <form
      noValidate
      onSubmit={handleSubmit((values) => {
        setBanner(undefined);
        login.mutate(values);
      })}
      className="flex flex-col gap-5"
    >
      {banner && <Alert>{banner}</Alert>}
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
          autoComplete="current-password"
          placeholder="Nhập mật khẩu"
          aria-invalid={!!errors.password}
          aria-describedby={errors.password ? "password-error" : undefined}
          {...register("password")}
        />
        <FieldError id="password-error">{errors.password?.message}</FieldError>
      </Field>
      <Button type="submit" disabled={login.isPending}>
        {login.isPending ? "Đang đăng nhập…" : "Đăng nhập"}
      </Button>
    </form>
  );
}
