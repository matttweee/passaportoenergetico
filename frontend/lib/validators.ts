export function validateCap(cap: string): boolean {
  return /^\d{5}$/.test((cap || "").trim());
}

export function validateDocType(docType: string): boolean {
  return docType === "recent" || docType === "old";
}

export function validateFileType(mime: string): boolean {
  const allowed = ["application/pdf", "image/jpeg", "image/png", "image/jpg"];
  return allowed.includes((mime || "").toLowerCase().split(";")[0].trim());
}

export function validateFileSize(bytes: number, maxMb: number = 15): boolean {
  return bytes > 0 && bytes <= maxMb * 1024 * 1024;
}
