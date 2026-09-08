export default function ErrorState({ message, onRetry }: { message: string, onRetry?: () => void }) {
  return (
    <div className="error-state">
      <p className="error-message">{message}</p>
      {onRetry && <button onClick={onRetry}>Retry</button>}
    </div>
  );
}
