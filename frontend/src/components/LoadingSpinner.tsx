export function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <span className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
    </div>
  );
}
