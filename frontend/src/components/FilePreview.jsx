export default function FilePreview({ fileUrl, filename, onClose }) {
  if (!fileUrl) return null;

  const isImage = /\.(jpg|jpeg)$/i.test(filename || "");
  const isPdf = /\.pdf$/i.test(filename || "");

  return (
    <div className="file-preview-overlay" onClick={onClose}>
      <div className="file-preview-panel" onClick={(e) => e.stopPropagation()}>
        <div className="file-preview-header">
          <span>{filename}</span>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="file-preview-body">
          {isImage && <img src={fileUrl} alt={filename} />}
          {isPdf && <iframe src={fileUrl} title={filename} />}
          {!isImage && !isPdf && (
            <div className="file-preview-fallback">
              <p>Preview not available for this file type.</p>
              <a href={fileUrl} target="_blank" rel="noreferrer">
                Open in new tab
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
