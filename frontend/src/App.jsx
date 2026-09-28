import { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatThread from "./components/ChatThread.jsx";
import FilePreview from "./components/FilePreview.jsx";
import InvoiceNumberPrompt from "./components/InvoiceNumberPrompt.jsx";
import {
  fetchAllInvoices,
  fetchInvoiceById,
  uploadInvoice,
  reAuditInvoice,
} from "./api/invoiceApi.js";

export default function App() {
  const [invoices, setInvoices] = useState([]);
  const [loadingInvoices, setLoadingInvoices] = useState(true);

  const [selectedInvoiceId, setSelectedInvoiceId] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  const [pendingRejections, setPendingRejections] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const [previewFile, setPreviewFile] = useState(null);

  // Set when the uploaded file has no invoice number: { file }
  const [numberPrompt, setNumberPrompt] = useState(null);

  const refreshInvoiceList = useCallback(async () => {
    try {
      const data = await fetchAllInvoices();
      setInvoices(data);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoadingInvoices(false);
    }
  }, []);

  useEffect(() => {
    refreshInvoiceList();
  }, [refreshInvoiceList]);

  useEffect(() => {
    function handlePreview(e) {
      setPreviewFile(e.detail);
    }
    window.addEventListener("preview-file", handlePreview);
    return () => window.removeEventListener("preview-file", handlePreview);
  }, []);

  async function selectInvoice(invoiceId) {
    setSelectedInvoiceId(invoiceId);
    setPendingRejections([]);
    setErrorMessage(null);
    try {
      const data = await fetchInvoiceById(invoiceId);
      setSelectedInvoice(data);
    } catch (err) {
      setErrorMessage(err.message);
      setSelectedInvoice(null);
    }
  }

  function startNewInvoiceThread() {
    setSelectedInvoiceId(null);
    setSelectedInvoice(null);
    setPendingRejections([]);
    setErrorMessage(null);
    setNumberPrompt(null);
  }

  // invoiceNumber is only passed when the user typed it into the prompt
  async function runAudit(file, invoiceNumber) {
    setIsSending(true);
    setErrorMessage(null);
    setNumberPrompt(null);

    try {
      const result = selectedInvoiceId
        ? await reAuditInvoice(selectedInvoiceId, file, invoiceNumber)
        : await uploadInvoice(file, invoiceNumber);

      // File has no invoice number → ask the user, then send the file again
      if (result.status === "NEEDS_INVOICE_NUMBER") {
        setNumberPrompt({ file });
        return;
      }

      // Nothing was saved on the backend (REJECTED, or FAILED on a new
      // upload) → show a one-off bubble for this session only.
      if (result.version_number === undefined) {
        setPendingRejections((prev) => [
          ...prev,
          {
            status: result.status,
            description: result.explanation,
            original_filename: file.name,
            version_number: null,
            file_url: null,
          },
        ]);
        return;
      }

      // Saved as a new version → reload list + thread
      await refreshInvoiceList();
      await selectInvoice(result.invoice_id);
    } catch (err) {
      // Duplicate-hash (409), duplicate identity (409) and validation errors
      setErrorMessage(err.message);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        invoices={invoices}
        selectedInvoiceId={selectedInvoiceId}
        onSelectInvoice={selectInvoice}
        onNewInvoice={startNewInvoiceThread}
        loading={loadingInvoices}
      />

      <ChatThread
        invoice={selectedInvoice}
        pendingRejections={pendingRejections}
        onUpload={(file) => runAudit(file, null)}
        isSending={isSending}
        errorMessage={errorMessage}
      />

      {numberPrompt && (
        <InvoiceNumberPrompt
          filename={numberPrompt.file.name}
          defaultValue={selectedInvoice?.invoice_number || ""}
          onSubmit={(number) => runAudit(numberPrompt.file, number)}
          onCancel={() => setNumberPrompt(null)}
        />
      )}

      {previewFile && (
        <FilePreview
          fileUrl={previewFile.url}
          filename={previewFile.name}
          onClose={() => setPreviewFile(null)}
        />
      )}
    </div>
  );
}
