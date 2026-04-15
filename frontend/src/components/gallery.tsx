"use client";

// Renders the inspiration grid; pending/failed badges reflect pollable classification status.

import { useState } from "react";

import { updateAnnotations } from "@/lib/api";
import type { InspirationImage } from "@/types/domain";

type GalleryProps = {
  items: readonly InspirationImage[];
};

function statusBadge(status: InspirationImage["classification_status"] | undefined) {
  const s = status ?? "completed";
  if (s === "completed") {
    return null;
  }
  const label = s === "pending" ? "Classifying" : "Failed";
  const cls = s === "pending" ? "product-card__badge--pending" : "product-card__badge--failed";
  return (
    <span className={`product-card__badge ${cls}`} aria-label={`Classification ${s}`}>
      {label}
    </span>
  );
}

function AnnotationEditor({ item }: { item: InspirationImage }) {
  const [tags, setTags] = useState(item.designer_tags.join(", "));
  const [notes, setNotes] = useState(item.designer_notes);
  const [saving, setSaving] = useState(false);

  async function onSave() {
    setSaving(true);
    try {
      await updateAnnotations(item.id, {
        designer_tags: tags
          .split(",")
          .map((value) => value.trim())
          .filter((value) => value.length > 0),
        designer_notes: notes,
      });
      window.location.reload();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="annotation-box">
      <div className="annotation-box__label">Your annotations</div>
      <input
        className="input"
        value={tags}
        onChange={(event) => setTags(event.target.value)}
        aria-label="Designer tags"
        placeholder="Tags separated by commas"
      />
      <textarea
        className="textarea"
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
        rows={2}
        placeholder="Notes for your team…"
      />
      <button type="button" className="btn btn--secondary" onClick={onSave} disabled={saving}>
        {saving ? "Saving…" : "Save annotations"}
      </button>
    </div>
  );
}

export function Gallery({ items }: GalleryProps) {
  if (items.length === 0) {
    return (
      <div className="gallery">
        <div className="gallery-empty">
          <p style={{ margin: 0, fontSize: "1rem", fontWeight: 600, color: "var(--ink)" }}>
            No looks yet
          </p>
          <p className="muted" style={{ margin: "0.5rem 0 0", maxWidth: "36ch", marginLeft: "auto", marginRight: "auto" }}>
            Upload a garment photo above, or loosen your filters. The API must be running at{" "}
            <code style={{ fontSize: "0.85em" }}>NEXT_PUBLIC_API_BASE_URL</code>.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="gallery" aria-label="Inspiration image gallery">
      {items.map((item) => (
        <article className="product-card" key={item.id}>
          <div className="product-card__media">
            {statusBadge(item.classification_status)}
            <img src={item.image_url} alt={item.ai_description} loading="lazy" />
          </div>
          <div className="product-card__body">
            <h3 className="product-card__title">
              {item.attributes.garment_type}
              {(item.classification_status ?? "completed") !== "completed" ? (
                <span className="product-card__title-meta">· {item.classification_status}</span>
              ) : null}
            </h3>
            <p className="product-card__desc">{item.ai_description}</p>
            {item.classification_error ? (
              <p className="product-card__error">{item.classification_error}</p>
            ) : null}
            <p className="product-card__meta">
              <strong>AI</strong> · {item.attributes.style} · {item.attributes.material} ·{" "}
              {item.attributes.location_context.city}, {item.attributes.location_context.country}
            </p>
            <div>
              <div className="annotation-box__label" style={{ marginBottom: "0.35rem" }}>
                Designer tags
              </div>
              <div className="product-card__chips">
                {item.designer_tags.length ? (
                  item.designer_tags.map((tag) => (
                    <span key={tag} className="chip chip--designer">
                      {tag}
                    </span>
                  ))
                ) : (
                  <span className="muted" style={{ fontSize: "0.8rem" }}>
                    None yet — add below
                  </span>
                )}
              </div>
            </div>
            <AnnotationEditor item={item} />
          </div>
        </article>
      ))}
    </div>
  );
}
