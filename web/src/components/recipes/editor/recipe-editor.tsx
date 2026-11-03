"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { FormProvider, useForm, useWatch, type Path } from "react-hook-form";
import { Alert } from "@/components/ui/alert";
import { api, isApiError, type ResponseBody } from "@/lib/api";
import {
  editStateFromRecipe,
  PUBLISHED_STATUS,
  toFormValues,
  type EditState,
  type RecipeDetail,
} from "@/lib/recipes/edit";
import { mapRecipeError } from "@/lib/recipes/errors";
import { saveRecipeEdit } from "@/lib/recipes/save-edit";
import {
  emptyRecipeForm,
  isPublishable,
  recipeFormSchema,
  toCreatePayload,
  type RecipeFormValues,
} from "@/lib/recipes/schemas";
import { useUnsavedChanges } from "@/lib/use-unsaved-changes";
import { BasicInfoCard } from "./basic-info-card";
import { ConflictDialog } from "./conflict-dialog";
import { ImagePanel } from "./image-panel";
import { IngredientsCard } from "./ingredients-card";
import { NutritionCard } from "./nutrition-card";
import { PublishCard } from "./publish-card";
import { StepsCard } from "./steps-card";

type CreatedRecipe = ResponseBody<"/recipes", "post">;
type CreateMode = "draft" | "publish";

export type RecipeEditorProps =
  | { mode?: "create" }
  | {
      mode: "edit";
      recipe: RecipeDetail;
      /** Fetches the latest saved version, used when a save conflicts with a newer one. */
      onReload: () => Promise<RecipeDetail>;
    };

export function RecipeEditor(props: RecipeEditorProps) {
  const router = useRouter();
  const recipe = props.mode === "edit" ? props.recipe : null;
  const onReload = props.mode === "edit" ? props.onReload : null;

  const [banner, setBanner] = useState<string>();
  const [notice, setNotice] = useState<string>();
  const [done, setDone] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [status, setStatus] = useState(recipe?.status);
  const [images, setImages] = useState(recipe?.images ?? []);
  // Create: a draft that was created but failed to publish; retries only call publish.
  const created = useRef<CreatedRecipe | null>(null);
  // Edit: what the server last confirmed (row version and children), updated by each successful save call.
  const serverState = useRef<EditState | null>(recipe ? editStateFromRecipe(recipe) : null);

  const form = useForm<RecipeFormValues>({
    resolver: zodResolver(recipeFormSchema),
    defaultValues: recipe ? toFormValues(recipe) : emptyRecipeForm,
  });
  const { handleSubmit, setError, setValue, control, formState, getValues, reset } = form;

  const ingredients = useWatch({ control, name: "ingredients" });
  const steps = useWatch({ control, name: "steps" });
  const checklist = isPublishable({ ingredients: ingredients ?? [], steps: steps ?? [] });

  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/categories"),
    staleTime: 5 * 60_000,
  });

  // The category <select> only shows a value once its options exist. In edit mode the options can arrive after
  // the form was reset with the saved category, so write the value again when they do.
  useEffect(() => {
    if (recipe && categories.data) setValue("category_id", getValues("category_id"));
    // The recipe is fixed for the life of this editor, so only the options matter here.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [categories.data]);

  const create = useMutation({
    mutationFn: async ({ values, mode }: { values: RecipeFormValues; mode: CreateMode }) => {
      if (!created.current) {
        created.current = await api.post("/recipes", { body: toCreatePayload(values) });
      }
      const draft = created.current;
      if (mode === "publish") {
        return await api.patch("/recipes/{recipe_id}/publish", { path: { recipe_id: draft.id } });
      }
      return draft;
    },
    onSuccess: (saved, { mode }) => {
      setDone(true);
      router.push(mode === "publish" ? `/recipes/${saved.slug}` : "/dashboard/recipes");
    },
    onError: (error) => {
      const failure = mapRecipeError(error);
      const draftSaved = created.current !== null;
      setBanner(
        draftSaved
          ? `Đã lưu bản nháp nhưng chưa xuất bản được. ${failure.banner ?? ""}`.trim()
          : failure.banner,
      );
      for (const [field, message] of Object.entries(failure.fields)) {
        setError(field as keyof RecipeFormValues, { message });
      }
    },
  });

  const save = useMutation({
    mutationFn: (values: RecipeFormValues) => {
      if (!recipe || !serverState.current) throw new Error("Edit mode without a loaded recipe");
      return saveRecipeEdit({
        api,
        recipeId: recipe.id,
        state: serverState.current,
        values,
        onCreated: (list, rowIndex, id) => setValue(`${list}.${rowIndex}.id` as const, id),
      });
    },
    onSuccess: () => {
      setBanner(undefined);
      setNotice("Đã lưu thay đổi.");
      reset(getValues());
    },
    onError: (error) => {
      setNotice(undefined);
      if (isApiError(error) && error.isConflict) {
        setConflict(true);
        return;
      }
      const failure = mapRecipeError(error);
      setBanner(
        `Một số thay đổi chưa được lưu. Lưu lại để thử tiếp. ${failure.banner ?? ""}`.trim(),
      );
      for (const [field, message] of Object.entries(failure.fields)) {
        setError(field as Path<RecipeFormValues>, { message });
      }
    },
  });

  const togglePublish = useMutation({
    mutationFn: () => {
      if (!recipe) throw new Error("Edit mode without a loaded recipe");
      const path = { recipe_id: recipe.id };
      return status === PUBLISHED_STATUS
        ? api.patch("/recipes/{recipe_id}/unpublish", { path })
        : api.patch("/recipes/{recipe_id}/publish", { path });
    },
    onSuccess: (updated) => {
      if (serverState.current) serverState.current.rowVersion = updated.row_version;
      setStatus(updated.status);
      setBanner(undefined);
      setNotice(
        updated.status === PUBLISHED_STATUS
          ? "Đã xuất bản công thức."
          : "Đã gỡ xuất bản công thức.",
      );
    },
    onError: (error) => setBanner(mapRecipeError(error).banner),
  });

  const remove = useMutation({
    mutationFn: () => {
      if (!recipe) throw new Error("Edit mode without a loaded recipe");
      return api.delete("/recipes/{recipe_id}", { path: { recipe_id: recipe.id } });
    },
    onSuccess: () => {
      setDone(true);
      router.push("/dashboard/recipes");
    },
    onError: (error) => setBanner(mapRecipeError(error).banner),
  });

  useUnsavedChanges(formState.isDirty && !done);

  const submitCreate = (mode: CreateMode) =>
    handleSubmit((values) => {
      setBanner(undefined);
      create.mutate({ values, mode });
    })();

  const submitEdit = () =>
    handleSubmit((values) => {
      setBanner(undefined);
      setNotice(undefined);
      save.mutate(values);
    })();

  /** Conflict resolution: reload the newer version (dropping local edits), or re-save local edits on top of it. */
  async function resolveConflict(choice: "reload" | "overwrite") {
    if (!recipe || !onReload) return;
    const local = getValues();
    const latest = await onReload();
    serverState.current = editStateFromRecipe(latest);
    setImages(latest.images);
    setStatus(latest.status);
    setConflict(false);
    if (choice === "reload") {
      reset(toFormValues(latest));
      setBanner(undefined);
      setNotice("Đã tải phiên bản mới.");
    } else {
      save.mutate(local);
    }
  }

  const pending = recipe
    ? save.isPending
      ? "save"
      : togglePublish.isPending
        ? status === PUBLISHED_STATUS
          ? "unpublish"
          : "publish"
        : remove.isPending
          ? "delete"
          : null
    : create.isPending
      ? (create.variables?.mode ?? null)
      : null;

  return (
    <FormProvider {...form}>
      <form noValidate onSubmit={(e) => e.preventDefault()} className="flex flex-col gap-6">
        {banner && <Alert>{banner}</Alert>}
        {notice && (
          <p role="status" className="text-sm text-herb">
            {notice}
          </p>
        )}
        <div className="grid items-start gap-6 min-[1000px]:grid-cols-[1fr_360px]">
          <div className="flex flex-col gap-6 min-[1000px]:order-2">
            <PublishCard
              hasIngredients={checklist.ingredients}
              hasSteps={checklist.steps}
              pending={pending}
              onSaveDraft={() => submitCreate("draft")}
              onPublish={() => submitCreate("publish")}
              edit={
                recipe && status !== undefined
                  ? {
                      published: status === PUBLISHED_STATUS,
                      dirty: formState.isDirty,
                      onSave: () => void submitEdit(),
                      onPublishToggle: () => togglePublish.mutate(),
                      onDelete: () => remove.mutate(),
                    }
                  : undefined
              }
            />
            <NutritionCard />
          </div>
          <div className="flex flex-col gap-6 min-[1000px]:order-1">
            <BasicInfoCard
              categories={categories.data ?? []}
              categoriesLoading={categories.isPending}
            />
            <ImagePanel recipeId={recipe?.id ?? null} images={images} onChange={setImages} />
            <IngredientsCard />
            <StepsCard />
          </div>
        </div>
      </form>
      <ConflictDialog
        open={conflict}
        busy={save.isPending}
        onReload={() => void resolveConflict("reload")}
        onOverwrite={() => void resolveConflict("overwrite")}
      />
    </FormProvider>
  );
}
