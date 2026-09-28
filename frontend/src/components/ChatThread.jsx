import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";
import UploadBar from "./UploadBar.jsx";
import TypingIndicator from "./TypingIndicator.jsx";

export default function ChatThread({
  invoice,
  pendingRejections,
  onUpload,
  isSending,
  errorMessage,
}) {
  const bottomRef = useRef(null);

  const versions = invoice?.versions
    ? [...invoice.versions].sort((a, b) => a.version_number - b.version_number)
    : [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [versions.length, pendingRejections.length, isSending]);

  const isNewInvoiceThread = !invoice;

  return (
    <div className="chat-thread">
      <div className="chat-header">
        {isNewInvoiceThread ? (
          <h2>New Invoice Audit</h2>
        ) : (
          <>
            <h2>{invoice.invoice_number}</h2>
            <span className="muted">
              Invoice ID: {invoice.id} · {versions.length} version
              {versions.length === 1 ? "" : "s"}
            </span>
          </>
        )}
      </div>

      <div className="chat-messages">
        {isNewInvoiceThread && pendingRejections.length === 0 && !isSending && (
          <div className="empty-state">
            <p>Attach a PDF, DOCX, JPG or JPEG below to start an audit.</p>
          </div>
        )}

        {versions.map((version) => (
          <MessageBubble
            key={version.id}
            version={version}
            onViewFile={(url, name) =>
              window.dispatchEvent(
                new CustomEvent("preview-file", { detail: { url, name } })
              )
            }
          />
        ))}

        {pendingRejections.map((rejection, idx) => (
          <MessageBubble
            key={`pending-${idx}`}
            version={rejection}
            isPending
            onViewFile={() => {}}
          />
        ))}

        {isSending && <TypingIndicator />}

        <div ref={bottomRef} />
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}

      <UploadBar
        onSend={onUpload}
        isSending={isSending}
        isReaudit={!isNewInvoiceThread}
        invoice={invoice}
      />
    </div>
  );
}
