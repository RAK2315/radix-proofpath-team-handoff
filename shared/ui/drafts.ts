import { useEffect } from "react";

const drafts = new Map<string, boolean>();
export function confirmDiscard(key?: string) {
  return (
    ![...drafts].some(([name, dirty]) => dirty && (!key || name === key)) ||
    window.confirm(
      "Discard unsaved changes? Save your draft first to keep these edits.",
    )
  );
}
export function useUnsavedChanges(key: string, dirty: boolean) {
  useEffect(() => {
    drafts.set(key, dirty);
    const warn = (event: BeforeUnloadEvent) => {
      if (dirty) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", warn);
    return () => {
      drafts.delete(key);
      window.removeEventListener("beforeunload", warn);
    };
  }, [key, dirty]);
}
