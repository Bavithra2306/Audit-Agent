import { useRef } from "react";

const ACCEPTED_TYPES = ".pdf,.docx,.jpg,.jpeg";

export default function UploadBar({ onSend, isSending, isReaudit, invoice }) {
  const inputRef = useRef(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      onSend(file);
    }
    // reset so selecting the same file twice still fires onChange
    e.target.value = "";
  }

  return (
    <div className="upload-dock">
      {isReaudit && (
        <div className="reaudit-context">
          Re-auditing <strong>Invoice ID {invoice.id}</strong> (
          {invoice.invoice_number})
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <button
        className="attach-fab"
        onClick={() => inputRef.current?.click()}
        disabled={isSending}
        title={isReaudit ? "Attach corrected invoice" : "Attach invoice to audit"}
      >
        {isSending ? "…" : "📎"}
        <span>{isSending ? "Auditing…" : "Attach invoice"}</span>
      </button>
    </div>
  );
}
