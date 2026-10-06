import { notFound } from "next/navigation";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox, Radio } from "@/components/ui/checkbox";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, FieldError, FieldHint, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Pagination } from "@/components/ui/pagination";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { RecipeFilterBar } from "@/components/recipes/recipe-filter-bar";
import { RecipeGrid, RecipeGridSkeleton } from "@/components/recipes/recipe-grid";
import { RecipePagination } from "@/components/recipes/recipe-pagination";
import { Textarea } from "@/components/ui/textarea";

/** Dev-only kitchen sink for eyeballing primitives against the mockups. */
export default function UiKitchenSink() {
  if (process.env.NODE_ENV === "production") notFound();
  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 p-8">
      <h1 className="text-page">Bếp Nhỏ — UI</h1>
      <div className="flex flex-wrap gap-3">
        <Button>Đăng nhập</Button>
        <Button variant="herb">Lưu</Button>
        <Button variant="outline">Hủy</Button>
        <Button variant="ghost">Bỏ qua</Button>
        <Button variant="destructive">Xóa</Button>
        <Button disabled>Vô hiệu</Button>
      </div>
      <Field>
        <Label htmlFor="email">Email</Label>
        <Input id="email" placeholder="ban@example.com" />
        <FieldHint>Chúng tôi không chia sẻ email.</FieldHint>
      </Field>
      <Field>
        <Label htmlFor="bad">Mật khẩu</Label>
        <Input id="bad" aria-invalid defaultValue="123" />
        <FieldError>Mật khẩu tối thiểu 8 ký tự.</FieldError>
      </Field>
      <Textarea placeholder="Cách làm…" />
      <Select defaultValue="a" aria-label="Độ khó">
        <option value="a">Dễ</option>
        <option value="b">Trung bình</option>
      </Select>
      <div className="flex gap-4">
        <label className="flex items-center gap-2">
          <Checkbox defaultChecked /> Ăn chay
        </label>
        <label className="flex items-center gap-2">
          <Radio name="r" defaultChecked /> Một
        </label>
        <label className="flex items-center gap-2">
          <Radio name="r" /> Hai
        </label>
      </div>
      <div className="flex flex-wrap gap-2">
        <Badge>Món chính</Badge>
        <Badge variant="outline">Bản nháp</Badge>
        <Badge variant="archived">Lưu trữ</Badge>
        <Badge variant="count">12</Badge>
      </div>
      <Alert>Email hoặc mật khẩu không đúng.</Alert>
      <Skeleton className="h-24 w-full" />
      <EmptyState
        title="Chưa có công thức"
        description="Hãy thử từ khóa khác."
        action={<Button variant="outline">Xóa bộ lọc</Button>}
      />
      <Pagination page={5} pageCount={12} hrefFor={(p) => `?page=${p}`} />
      <RecipeFilterBar basePath="/dev/ui" difficulty="easy" maxCookTime={30} />
      <RecipeGrid
        recipes={[
          {
            slug: "pho-bo",
            title: "Phở bò Hà Nội",
            category: "Món nước",
            time: "3 giờ",
            difficulty: "Trung bình",
            author: "Minh Anh",
          },
          {
            slug: "banh-xeo",
            title: "Bánh xèo miền Tây",
            category: "Món chiên",
            time: "45 phút",
            difficulty: "Trung bình",
            author: "Thu Hà",
          },
          { slug: "ca-kho", title: "Cá kho tộ", time: "90 phút", difficulty: "Dễ" },
        ]}
      />
      <RecipeGrid recipes={[]} />
      <RecipeGridSkeleton count={4} />
      <RecipePagination
        basePath="/dev/ui"
        page={2}
        totalPages={6}
        params={{ difficulty: "easy" }}
      />
    </main>
  );
}
