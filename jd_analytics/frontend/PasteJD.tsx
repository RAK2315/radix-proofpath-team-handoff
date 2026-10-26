import { useState } from "react";
import { FileText } from "lucide-react";
import type { Extraction } from "../../shared/contracts/types";
import { post } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import { Notice } from "../../shared/ui/components";
import { useUnsavedChanges } from "../../shared/ui/drafts";

export default function PasteJD({
  onResult,
}: {
  onResult: (value: Extraction) => Promise<void>;
}) {
  const { status } = useWorkspace();
  const [text, setText] = useState("");
  const [name, setName] = useState("Pasted job description");
  const [hosted, setHosted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useUnsavedChanges("pasted-jd", Boolean(text));
  async function extract() {
    setBusy(true);
    setError("");
    try {
      const result = await post<Extraction>("/jd/extract-text", {
        text,
        source_name: name,
        hosted_consent: hosted,
      });
      setText("");
      await onResult(result);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="paste-jd">
      <label>
        Source name
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={120}
        />
      </label>
      <label>
        Job description text
        <textarea
          rows={10}
          placeholder="Paste the full job description, including responsibilities and qualifications…"
          value={text}
          onChange={(event) => setText(event.target.value)}
          maxLength={120000}
        />
      </label>
      <div className="upload-footer">
        <span>
          {text.length.toLocaleString()} / 120,000 characters · retained as a
          private text source
        </span>
        {status?.llm_configured && (
          <label className="check">
            <input
              type="checkbox"
              checked={hosted}
              onChange={(event) => setHosted(event.target.checked)}
            />{" "}
            Allow {status?.llm_provider || "Groq"} to process this pasted text
          </label>
        )}
      </div>
      {error && <Notice tone="error">{error}</Notice>}
      <div className="card-footer">
        <p className="fine-print">
          Your original text stays attached to every extracted requirement for
          review.
        </p>
        <button
          className="button primary"
          disabled={busy || text.trim().length < 15 || !name.trim()}
          onClick={() => void extract()}
        >
          <FileText size={15} />
          {busy ? "Extracting requirements…" : "Extract pasted JD"}
        </button>
      </div>
    </div>
  );
}
