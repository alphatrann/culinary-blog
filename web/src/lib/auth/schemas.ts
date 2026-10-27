import { z } from "zod";

export const passwordRules = [
  { id: "length", label: "Tối thiểu 8 ký tự", test: (v: string) => v.length >= 8 },
  { id: "upper", label: "1 chữ hoa", test: (v: string) => /[A-Z]/.test(v) },
  { id: "digit", label: "1 chữ số", test: (v: string) => /\d/.test(v) },
  { id: "special", label: "1 ký tự đặc biệt", test: (v: string) => /[^A-Za-z0-9]/.test(v) },
] as const;

const email = z
  .string()
  .trim()
  .min(1, "Vui lòng nhập email.")
  .max(256, "Email quá dài.")
  .email("Email không hợp lệ.");

export const loginSchema = z.object({
  email,
  password: z.string().min(1, "Vui lòng nhập mật khẩu.").max(128),
});

export const registerSchema = z.object({
  display_name: z
    .string()
    .trim()
    .min(2, "Tên hiển thị cần từ 2 đến 100 ký tự.")
    .max(100, "Tên hiển thị cần từ 2 đến 100 ký tự."),
  email,
  password: z
    .string()
    .max(128, "Mật khẩu tối đa 128 ký tự.")
    .refine((v) => passwordRules.every((r) => r.test(v)), "Mật khẩu chưa đáp ứng yêu cầu."),
});

export const profileSchema = z.object({
  display_name: z
    .string()
    .trim()
    .min(2, "Tên hiển thị cần từ 2 đến 100 ký tự.")
    .max(100, "Tên hiển thị cần từ 2 đến 100 ký tự."),
  avatar_url: z
    .string()
    .trim()
    .max(500, "Liên kết ảnh tối đa 500 ký tự.")
    .refine(
      (v) => v === "" || /^https?:\/\/\S+$/.test(v),
      "Liên kết ảnh phải bắt đầu bằng http:// hoặc https://.",
    ),
  bio: z.string().trim().max(1000, "Giới thiệu tối đa 1000 ký tự."),
});

export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;
export type ProfileValues = z.infer<typeof profileSchema>;
