const Alert = ({ message, type = "success", onClose }) => {
  if (!message) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '30px',
      right: '30px',
      zIndex: 3000,
      padding: '16px 24px',
      borderRadius: '12px',
      background: type === "success" ? "rgba(52, 199, 89, 0.9)" : "rgba(255, 59, 48, 0.9)",
      backdropFilter: 'blur(10px)',
      color: 'white',
      boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
      display: 'flex',
      alignItems: 'center',
      gap: '15px',
      animation: 'slideIn 0.3s ease-out'
    }}>
      <span style={{ fontWeight: 600 }}>{message}</span>
      <button 
        onClick={onClose}
        style={{
          background: 'transparent',
          border: 'none',
          color: 'white',
          cursor: 'pointer',
          fontSize: '1.2rem'
        }}
      >
        ×
      </button>
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default Alert;
