import { isApiError } from "@/lib/api";

export type AuthField = "display_name" | "email" | "password";

export interface AuthFailure {
  banner?: string;
  fields: Partial<Record<AuthField, string>>;
}

const FIELDS: AuthField[] = ["display_name", "email", "password"];
const GENERIC = "Đã có lỗi xảy ra. Vui lòng thử lại.";

/** Maps an API failure onto a form-level banner and/or per-field messages. */
export function mapAuthError(error: unknown, mode: "login" | "register"): AuthFailure {
  if (!isApiError(error)) return { banner: GENERIC, fields: {} };
  if (error.isLocked) {
    return {
      banner: "Tài khoản tạm khóa do đăng nhập sai quá 5 lần. Vui lòng thử lại sau 15 phút.",
      fields: {},
    };
  }
  if (error.isRateLimited) {
    return { banner: "Bạn thao tác quá nhanh. Vui lòng thử lại sau ít phút.", fields: {} };
  }
  if (error.status === 401) {
    return { banner: "Email hoặc mật khẩu không đúng.", fields: {} };
  }
  if (error.status === 409 && mode === "register") {
    return {
      banner: "Email này đã được đăng ký. Hãy đăng nhập hoặc dùng email khác.",
      fields: { email: "Email này đã được đăng ký." },
    };
  }
  if (error.status === 422) {
    const fields: AuthFailure["fields"] = {};
    for (const f of FIELDS) if (error.errors[f]) fields[f] = error.errors[f];
    return Object.keys(fields).length ? { fields } : { banner: GENERIC, fields };
  }
  return { banner: GENERIC, fields: {} };
}
