import Link from "next/link";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function SiteFooter() {
  const base = apiBase.replace(/\/$/, "");
  const docsHref = `${base}/docs`;
  const healthHref = `${base}/health`;

  return (
    <footer className="site-footer">
      <div className="site-footer__main">
        <div className="site-footer__grid">
          <div className="site-footer__col">
            <h2 className="site-footer__heading">Get started</h2>
            <ul className="site-footer__list">
              <li>
                <Link href="/">Inspiration library</Link>
              </li>
              <li>
                <a href="#upload">Upload garments</a>
              </li>
              <li>
                <a href="#filters">Search &amp; filters</a>
              </li>
            </ul>
          </div>
          <div className="site-footer__col">
            <h2 className="site-footer__heading">Resources</h2>
            <ul className="site-footer__list">
              <li>
                <a href={docsHref} target="_blank" rel="noopener noreferrer">
                  OpenAPI (Swagger)
                </a>
              </li>
              <li>
                <a href={healthHref} target="_blank" rel="noopener noreferrer">
                  Service health
                </a>
              </li>
              <li>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer">
                  Repository
                </a>
              </li>
            </ul>
          </div>
          <div className="site-footer__col">
            <h2 className="site-footer__heading">Trust &amp; privacy</h2>
            <ul className="site-footer__list">
              <li>
                <span className="site-footer__muted">Demo Build for Assessment.</span>
              </li>
              
            </ul>
          </div>
          <div className="site-footer__col site-footer__col--brand">
            <div className="site-footer__logo">
              <span className="site-footer__logo-mark" aria-hidden>
                F
              </span>
              <span className="site-footer__logo-text">Fashion Inspiration Studio</span>
            </div>
            <p className="site-footer__blurb">
              Retail-grade layout patterns for a design-case study: clear hierarchy, scannable filters, and
              card-based discovery.
            </p>
          </div>
        </div>
      </div>
      <div className="site-footer__legal">
        <div className="site-footer__legal-inner">
          <p>© {new Date().getFullYear()} Fashion Inspiration Studio · Demo application</p>
          <p className="site-footer__legal-links">
            <span>Not affiliated with Walmart Inc.</span>
            <span aria-hidden> · </span>
            <span>Inspired by retail UX best practices</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
