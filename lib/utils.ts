export function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function sportLabel(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
