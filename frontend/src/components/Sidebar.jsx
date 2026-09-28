const STATUS_COLORS = {
  PASSED: "#2e7d32",
  DISCREPANCY_FOUND: "#c62828",
  FAILED: "#757575",
};

function latestVersion(invoice) {
  if (!invoice.versions || invoice.versions.length === 0) return null;
  return invoice.versions.reduce((latest, v) =>
    v.version_number > latest.version_number ? v : latest
  );
}

export default function Sidebar({
  invoices,
  selectedInvoiceId,
  onSelectInvoice,
  onNewInvoice,
  loading,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>Audit Agent</h1>
        <button className="new-invoice-btn" onClick={onNewInvoice}>
          + New Invoice
        </button>
      </div>

      <div className="invoice-list">
        {loading && <p className="muted">Loading…</p>}

        {!loading && invoices.length === 0 && (
          <p className="muted">No invoices audited yet.</p>
        )}

        {invoices.map((invoice) => {
          const latest = latestVersion(invoice);
          const isActive = invoice.id === selectedInvoiceId;

          return (
            <button
              key={invoice.id}
              className={`invoice-item ${isActive ? "active" : ""}`}
              onClick={() => onSelectInvoice(invoice.id)}
            >
              <div className="invoice-item-top">
                <span className="invoice-number">
                  {invoice.invoice_number}
                </span>
                {latest && (
                  <span
                    className="status-dot"
                    style={{
                      backgroundColor:
                        STATUS_COLORS[latest.status] || "#999",
                    }}
                    title={latest.status}
                  />
                )}
              </div>
              <div className="invoice-item-sub">
                {invoice.versions?.length || 0} version
                {invoice.versions?.length === 1 ? "" : "s"}
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
