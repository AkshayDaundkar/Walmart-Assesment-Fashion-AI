"use client";

import type { ReactNode } from "react";
import { useEffect, useId, useRef, useState } from "react";

type CollapsibleFilterPanelProps = {
  /** Open by default when user has active filters or search */
  defaultExpanded: boolean;
  activeFilterCount: number;
  resultCount: number;
  children: ReactNode;
};

export function CollapsibleFilterPanel({
  defaultExpanded,
  activeFilterCount,
  resultCount,
  children,
}: CollapsibleFilterPanelProps) {
  const panelId = useId();
  const [expanded, setExpanded] = useState(defaultExpanded);
  const contentRef = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState<number | undefined>(defaultExpanded ? undefined : 0);

  useEffect(() => {
    setExpanded(defaultExpanded);
  }, [defaultExpanded]);

  useEffect(() => {
    const el = contentRef.current;
    if (!el) {
      return;
    }
    if (expanded) {
      setHeight(el.scrollHeight);
    } else {
      setHeight(0);
    }
  }, [expanded, children]);

  useEffect(() => {
    const el = contentRef.current;
    if (!el || !expanded) {
      return;
    }
    const ro = new ResizeObserver(() => {
      setHeight(el.scrollHeight);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [expanded]);

  return (
    <section className="panel filter-panel" id="filters" aria-labelledby={`${panelId}-heading`}>
      <div className="filter-panel__header">
        <div className="filter-panel__title-row">
          <h2 className="panel__title" id={`${panelId}-heading`}>
            Refine results
            <span className="panel__title-badge">Filters</span>
            {activeFilterCount > 0 ? (
              <span className="filter-panel__count-badge">{activeFilterCount} active</span>
            ) : null}
          </h2>
          <p className="filter-panel__meta muted">
            {resultCount} item{resultCount === 1 ? "" : "s"} · Facets from your library
          </p>
        </div>
        <button
          type="button"
          className="filter-panel__toggle"
          aria-expanded={expanded}
          aria-controls={`${panelId}-region`}
          id={`${panelId}-toggle`}
          onClick={() => setExpanded((value) => !value)}
        >
          <span className="filter-panel__toggle-label">{expanded ? "Hide filters" : "Show filters"}</span>
          <svg
            className={`filter-panel__chevron ${expanded ? "filter-panel__chevron--open" : ""}`}
            width={20}
            height={20}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>
      </div>

      <div
        id={`${panelId}-region`}
        role="region"
        aria-labelledby={`${panelId}-toggle`}
        className="filter-panel__collapsible"
        style={{
          maxHeight: height === undefined ? "none" : `${height}px`,
          opacity: expanded ? 1 : 0,
        }}
        data-expanded={expanded ? "true" : "false"}
      >
        <div ref={contentRef} className="filter-panel__collapsible-inner">
          {children}
        </div>
      </div>
    </section>
  );
}
