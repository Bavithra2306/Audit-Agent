export default function TypingIndicator() {
  return (
    <div className="message-pair">
      <div className="bubble bubble-agent typing-bubble">
        <div className="typing-content">
          <span className="typing-spinner" />
          <span className="typing-text">
            Auditing invoice
            <span className="typing-dots">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          </span>
        </div>
      </div>
    </div>
  );
}
