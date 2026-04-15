import Link from "next/link";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function SiteHeader() {
  const docsHref = `${apiBase.replace(/\/$/, "")}/docs`;

  return (
    <header className="site-chrome-header">
      <div className="utility-bar">
        <div className="utility-bar__inner">
          <p className="utility-bar__msg">
            <span className="utility-bar__spark" aria-hidden>
              ✦
            </span>
            Design teams: organize inspiration with AI metadata—built for fast field capture.
          </p>
          <nav className="utility-bar__nav" aria-label="Utility links">
            <a className="utility-bar__link" href="#upload">
              Upload
            </a>
            <a className="utility-bar__link" href="#filters">
              Filters
            </a>
            <a className="utility-bar__link" href="#gallery">
              Gallery
            </a>
            <a className="utility-bar__link" href={docsHref} target="_blank" rel="noopener noreferrer">
              API docs
            </a>
          </nav>
        </div>
      </div>

      <div className="primary-header">
        <div className="primary-header__inner">
          <Link href="/" className="primary-brand">
            <span className="primary-brand__spark" aria-hidden>
              ●
            </span>
            <span className="primary-brand__wordmark">Fashion Studio</span>
          </Link>

          <nav className="primary-nav" aria-label="Primary">
            <Link className="primary-nav__link primary-nav__link--active" href="/">
              Inspiration library
            </Link>
            <a className="primary-nav__link" href="#upload">
              Add looks
            </a>
            <a className="primary-nav__link" href="#filters">
              Browse &amp; filter
            </a>
          </nav>

          <div className="primary-header__actions">
            <span className="status-pill" title={`API: ${apiBase}`}>
              <span className="status-pill__dot" aria-hidden />
              Live catalog
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
