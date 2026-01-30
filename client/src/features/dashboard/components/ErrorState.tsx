// Figma: DashboardPage/ErrorState

export type ErrorStateProps = {
  title?: string;
  message?: string;
};

export function ErrorState({
  title = "Something went wrong",
  message = "Try again in a moment.",
}: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 p-4">
      <p className="text-sm font-medium text-rose-900">{title}</p>
      <p className="mt-1 text-sm text-rose-800">{message}</p>
    </div>
  );
}
