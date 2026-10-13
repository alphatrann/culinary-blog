import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useUnsavedChanges } from "./use-unsaved-changes";

function Harness({ dirty }: { dirty: boolean }) {
  useUnsavedChanges(dirty);
  return <a href="/elsewhere">Rời đi</a>;
}

describe("useUnsavedChanges", () => {
  afterEach(() => vi.restoreAllMocks());

  it("asks for confirmation on in-app links when dirty and cancels navigation on refusal", async () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<Harness dirty />);
    const click = new MouseEvent("click", { bubbles: true, cancelable: true, button: 0 });
    screen.getByRole("link").dispatchEvent(click);
    expect(confirm).toHaveBeenCalledOnce();
    expect(click.defaultPrevented).toBe(true);
  });

  it("lets navigation through when the user confirms or the form is clean", async () => {
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(true);
    const { rerender } = render(<Harness dirty />);
    await userEvent.click(screen.getByRole("link"));
    expect(confirm).toHaveBeenCalledOnce();
    rerender(<Harness dirty={false} />);
    await userEvent.click(screen.getByRole("link"));
    expect(confirm).toHaveBeenCalledOnce();
  });

  it("registers beforeunload only while dirty", () => {
    const add = vi.spyOn(window, "addEventListener");
    const { rerender } = render(<Harness dirty={false} />);
    expect(add).not.toHaveBeenCalledWith("beforeunload", expect.anything());
    rerender(<Harness dirty />);
    expect(add).toHaveBeenCalledWith("beforeunload", expect.any(Function));
  });
});
