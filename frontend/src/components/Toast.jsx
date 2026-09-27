export default function Toast({ toast }) {
  if (!toast) return null;
  return (
    <div className="toast" style={{ borderColor: toast.color, color: toast.color }}>
      {toast.text}
    </div>
  );
}
