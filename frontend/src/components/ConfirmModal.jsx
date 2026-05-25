function ConfirmModal({ title, message, onConfirm, onCancel, emoji = '🗑️' }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-emoji">{emoji}</div>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onCancel}>
            Nah, keep it
          </button>
          <button className="btn btn-danger" onClick={onConfirm}>
            Yeah, delete it
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
