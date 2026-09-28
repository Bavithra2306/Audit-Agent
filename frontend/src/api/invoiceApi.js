// -------------------------------------------------------------
// Thin wrapper around the 5 backend endpoints. No extra library —
// plain fetch, matching the current invoice_router.py contract.
// -------------------------------------------------------------

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {
      // response wasn't JSON — keep default message
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }
  return res.json();
}

// GET /invoices/all
export async function fetchAllInvoices() {
  const res = await fetch(`${API_BASE_URL}/invoices/all`);
  return handleResponse(res);
}

// GET /invoices/{invoice_id}
export async function fetchInvoiceById(invoiceId) {
  const res = await fetch(`${API_BASE_URL}/invoices/${invoiceId}`);
  return handleResponse(res);
}

// POST /invoices/upload  (initial audit — no invoice_id yet)
// invoiceNumber is only sent when the user typed it in (file had none)
export async function uploadInvoice(file, invoiceNumber) {
  const formData = new FormData();
  formData.append("file", file);
  if (invoiceNumber) formData.append("invoice_number", invoiceNumber);

  const res = await fetch(`${API_BASE_URL}/invoices/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}

// POST /invoices/{invoice_id}/re-audit  (corrected file against existing invoice)
export async function reAuditInvoice(invoiceId, file, invoiceNumber) {
  const formData = new FormData();
  formData.append("file", file);
  if (invoiceNumber) formData.append("invoice_number", invoiceNumber);

  const res = await fetch(`${API_BASE_URL}/invoices/${invoiceId}/re-audit`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}

// Builds the absolute URL for a version's file, from the relative
// file_url the backend returns (e.g. "/invoices/version/7/file")
export function resolveFileUrl(relativeUrl) {
  if (!relativeUrl) return null;
  return `${API_BASE_URL}${relativeUrl}`;
}
