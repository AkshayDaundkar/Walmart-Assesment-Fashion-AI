"use client";

// Multipart upload to POST /v1/library/upload; page reload refreshes the library list.

import type { FormEvent } from "react";
import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function UploadForm() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsUploading(true);

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/library/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      window.location.reload();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Unknown upload error");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="field-grid field-grid--upload">
        <div className="field field--full">
          <span className="field__label">Garment photo</span>
          <div className="file-field">
            <input
              name="file"
              type="file"
              accept="image/*"
              required
              suppressHydrationWarning
              aria-label="Choose garment image file"
            />
          </div>
        </div>
        <div className="field">
          <label className="field__label" htmlFor="upload-tags">
            Designer tags
          </label>
          <input
            id="upload-tags"
            className="input"
            name="designer_tags"
            type="text"
            placeholder="e.g. neckline, streetwear"
            autoComplete="off"
          />
        </div>
        <div className="field field--full">
          <label className="field__label" htmlFor="upload-notes">
            Designer notes
          </label>
          <textarea
            id="upload-notes"
            className="textarea"
            name="designer_notes"
            placeholder="Observations, construction ideas, or context from the field…"
          />
        </div>
      </div>
      <div className="btn-row">
        <button type="submit" className="btn btn--primary" disabled={isUploading}>
          {isUploading ? "Uploading & classifying…" : "Upload & classify"}
        </button>
        <span className="muted">Heuristic or OpenAI vision runs on the API (see backend `.env`).</span>
      </div>
      {error ? (
        <p className="product-card__error" style={{ marginTop: "0.75rem" }}>
          {error}
        </p>
      ) : null}
    </form>
  );
}
