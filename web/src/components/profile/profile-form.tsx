"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldHint, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, isApiError } from "@/lib/api";
import { profileSchema, type ProfileValues } from "@/lib/auth/schemas";
import { sessionQueryKey, useUser, type SessionUser } from "@/lib/session";

const GENERIC = "Đã có lỗi xảy ra. Vui lòng thử lại.";

function toFormValues(user: SessionUser | null): ProfileValues {
  return {
    display_name: user?.display_name ?? "",
    avatar_url: user?.avatar_url ?? "",
    bio: user?.bio ?? "",
  };
}

/** Empty optional fields are sent as null so the server clears them (PATCH only touches what is sent). */
function toPayload({ display_name, avatar_url, bio }: ProfileValues) {
  return { display_name, avatar_url: avatar_url || null, bio: bio || null };
}

export function ProfileForm() {
  const { user } = useUser();
  const queryClient = useQueryClient();
  const [banner, setBanner] = useState<string>();
  const [saved, setSaved] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isDirty },
  } = useForm<ProfileValues>({ resolver: zodResolver(profileSchema), values: toFormValues(user) });

  const save = useMutation({
    mutationFn: (values: ProfileValues) => api.patch("/auth/me", { body: toPayload(values) }),
    onSuccess: (updated) => {
      queryClient.setQueryData(sessionQueryKey, updated);
      setSaved(true);
    },
    onError: (error) => {
      const fieldErrors = isApiError(error) ? error.errors : {};
      for (const [field, message] of Object.entries(fieldErrors)) {
        setError(field as keyof ProfileValues, { message });
      }
      setBanner(Object.keys(fieldErrors).length ? undefined : GENERIC);
    },
  });

  return (
    <form
      noValidate
      onSubmit={handleSubmit((values) => {
        setBanner(undefined);
        setSaved(false);
        save.mutate(values);
      })}
      className="flex flex-col gap-5"
    >
      {banner && <Alert>{banner}</Alert>}
      <Field>
        <Label htmlFor="email">Email</Label>
        <Input id="email" value={user?.email ?? ""} readOnly aria-describedby="email-hint" />
        <FieldHint id="email-hint">Email không thể thay đổi.</FieldHint>
      </Field>
      <Field>
        <Label htmlFor="display_name">Tên hiển thị</Label>
        <Input
          id="display_name"
          autoComplete="name"
          aria-invalid={!!errors.display_name}
          aria-describedby="display_name-error"
          {...register("display_name")}
        />
        <FieldError id="display_name-error">{errors.display_name?.message}</FieldError>
      </Field>
      <Field>
        <Label htmlFor="avatar_url">Liên kết ảnh đại diện</Label>
        <Input
          id="avatar_url"
          type="url"
          inputMode="url"
          placeholder="https://"
          aria-invalid={!!errors.avatar_url}
          aria-describedby="avatar_url-error"
          {...register("avatar_url")}
        />
        <FieldError id="avatar_url-error">{errors.avatar_url?.message}</FieldError>
      </Field>
      <Field>
        <Label htmlFor="bio">Giới thiệu</Label>
        <Textarea
          id="bio"
          maxLength={1000}
          aria-invalid={!!errors.bio}
          aria-describedby="bio-hint bio-error"
          {...register("bio")}
        />
        <FieldHint id="bio-hint">Tối đa 1000 ký tự.</FieldHint>
        <FieldError id="bio-error">{errors.bio?.message}</FieldError>
      </Field>
      <div className="flex items-center gap-4">
        <Button type="submit" disabled={!isDirty || save.isPending}>
          {save.isPending ? "Đang lưu…" : "Lưu thay đổi"}
        </Button>
        {saved && (
          <p role="status" className="text-[13px] text-muted-foreground">
            Đã lưu thay đổi.
          </p>
        )}
      </div>
    </form>
  );
}
