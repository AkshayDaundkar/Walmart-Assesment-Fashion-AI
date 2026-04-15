import { CollapsibleFilterPanel } from "@/components/collapsible-filter-panel";
import { Gallery } from "@/components/gallery";
import { UploadForm } from "@/components/upload-form";
import { fetchLibrary, type LibraryQueryParams } from "@/lib/api";

type HomePageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function readParam(
  params: Record<string, string | string[] | undefined>,
  key: string,
): string | undefined {
  const value = params[key];
  return typeof value === "string" && value.trim().length > 0 ? value : undefined;
}

function buildLibraryQuery(params: Record<string, string | string[] | undefined>): LibraryQueryParams {
  const out: LibraryQueryParams = {};
  for (const key of Object.keys(params)) {
    const value = readParam(params, key);
    if (value !== undefined) {
      out[key] = value;
    }
  }
  return out;
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = (await searchParams) ?? {};
  const query = buildLibraryQuery(params);
  const activeFilterCount = Object.keys(query).length;
  const library = await fetchLibrary(query);

  return (
    <main className="page-main" id="main-content">
      <div className="page-hero">
        <h1>Your inspiration library</h1>
        <p>
          Upload field photos, get structured garment metadata, and filter the same way you’d browse a
          retail catalog—fast, scannable, and ready for your design workflow.
        </p>
      </div>

      <section className="panel" id="upload">
        <h2 className="panel__title">
          Add inspiration
          <span className="panel__title-badge">Upload</span>
        </h2>
        <UploadForm />
      </section>

      <CollapsibleFilterPanel
        defaultExpanded={activeFilterCount > 0}
        activeFilterCount={activeFilterCount}
        resultCount={library.items.length}
      >
        <form method="get" className="filter-grid">
          <div className="field filter-search">
            <label className="field__label" htmlFor="filter-q">
              Search
            </label>
            <input
              id="filter-q"
              className="input"
              name="q"
              placeholder='Try "embroidered neckline" or "artisan market"'
              defaultValue={readParam(params, "q")}
            />
          </div>
          {library.facets.map((facet) => (
            <div key={facet.key} className="field">
              <label className="field__label" htmlFor={`facet-${facet.key}`}>
                {facet.key.replaceAll("_", " ")}
              </label>
              <select
                id={`facet-${facet.key}`}
                className="select"
                name={facet.key}
                defaultValue={readParam(params, facet.key) ?? ""}
              >
                <option value="">All</option>
                {facet.values.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          ))}
          <div className="filter-actions">
            <button type="submit" className="btn btn--primary">
              Apply filters
            </button>
            <a className="btn btn--secondary" href="/">
              Clear all
            </a>
          </div>
        </form>
      </CollapsibleFilterPanel>

      <section aria-label="Image gallery" id="gallery">
        <Gallery items={library.items} />
      </section>
    </main>
  );
}
