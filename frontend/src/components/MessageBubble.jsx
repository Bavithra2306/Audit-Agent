import { resolveFileUrl } from "../api/invoiceApi";

const STATUS_LABELS = {
  PASSED: "Passed",
  DISCREPANCY_FOUND: "Discrepancy Found",
  FAILED: "Failed",
  REJECTED: "Rejected",
};

const STATUS_CLASS = {
  PASSED: "status-passed",
  DISCREPANCY_FOUND: "status-discrepancy",
  FAILED: "status-failed",
  REJECTED: "status-rejected",
};

function formatMoney(value, currency) {
  if (value === null || value === undefined) return "—";
  return `${currency || ""} ${Number(value).toFixed(2)}`.trim();
}

export default function MessageBubble({ version, onViewFile, isPending }) {
  const statusClass = STATUS_CLASS[version.status] || "status-failed";
  const statusLabel = STATUS_LABELS[version.status] || version.status;
  const fileUrl = version.file_url ? resolveFileUrl(version.file_url) : null;

  return (
    <div className="message-pair">
      {/* User bubble — the uploaded file */}
      <div className="bubble bubble-user">
        <div className="bubble-label">
          {version.version_number
            ? `You — Version ${version.version_number}`
            : "You"}
        </div>
        <div className="bubble-filename">
          {version.original_filename || "uploaded file"}
        </div>
        {fileUrl && (
          <button
            className="view-file-btn"
            onClick={() => onViewFile(fileUrl, version.original_filename)}
          >
            View file
          </button>
        )}
      </div>

      {/* Agent bubble — the audit result */}
      <div className={`bubble bubble-agent ${statusClass}`}>
        <div className="bubble-label">
          <span className="status-badge">{statusLabel}</span>
          {isPending && <span className="pending-tag">not saved</span>}
        </div>

        {version.status === "PASSED" ||
        version.status === "DISCREPANCY_FOUND" ? (
          <div className="totals-row">
            <span>
              Stated total: {formatMoney(version.stated_grand_total, version.currency)}
            </span>
            <span>
              Calculated total:{" "}
              {formatMoney(version.calculated_grand_total, version.currency)}
            </span>
          </div>
        ) : null}

        <p className="explanation-text">{version.description}</p>
      </div>
    </div>
  );
}
