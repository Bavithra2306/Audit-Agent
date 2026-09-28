import { useState } from "react";

export default function InvoiceNumberPrompt({
  filename,
  defaultValue,
  onSubmit,
  onCancel,
}) {
  const [value, setValue] = useState(defaultValue || "");
  const trimmed = value.trim();

  function handleSubmit(e) {
    e.preventDefault();
    if (trimmed) onSubmit(trimmed);
  }

  return (
    <div className="prompt-overlay">
      <form className="prompt-card" onSubmit={handleSubmit}>
        <h3>Invoice number needed</h3>
        <p>
          The uploaded file <strong>{filename}</strong> has no invoice number.
          Please enter the invoice number.
        </p>

        <input
          autoFocus
          type="text"
          maxLength={100}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="e.g. INV-2026-0917"
        />

        <div className="prompt-actions">
          <button type="button" className="prompt-cancel" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="prompt-submit" disabled={!trimmed}>
            Continue audit
          </button>
        </div>
      </form>
    </div>
  );
}
