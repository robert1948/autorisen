// Figma: DashboardPage/SkeletonBlock

export type SkeletonBlockProps = {
  width?: number | string;
  height?: number | string;
};

export function SkeletonBlock({ width = "100%", height = 12 }: SkeletonBlockProps) {
  return (
    <div
      className="animate-pulse rounded bg-slate-100"
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}
