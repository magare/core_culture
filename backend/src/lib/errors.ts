export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message); }
}

export function databaseCode(error: unknown): string | undefined {
  if (!error || typeof error !== "object") return;
  if ("code" in error && typeof error.code === "string") return error.code;
  if ("cause" in error) return databaseCode(error.cause);
}
