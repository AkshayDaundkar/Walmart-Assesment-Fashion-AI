export type AiAttribute = {
  garment_type: string;
  style: string;
  material: string;
  color_palette: string[];
  pattern: string;
  season: string;
  occasion: string;
  consumer_profile: string;
  trend_notes: string[];
  location_context: {
    continent: string;
    country: string;
    city: string;
  };
  time_context: {
    year: number;
    month: number;
    season: string;
  };
};

export type ClassificationStatus = "pending" | "completed" | "failed";

export type InspirationImage = {
  id: string;
  image_url: string;
  ai_description: string;
  attributes: AiAttribute;
  designer_tags: string[];
  designer_notes: string;
  created_at: string;
  classification_status?: ClassificationStatus;
  classification_error?: string | null;
};

export type FilterFacet = {
  key: string;
  values: readonly string[];
};

export type LibraryResponse = {
  items: InspirationImage[];
  facets: FilterFacet[];
};

export type UpdateAnnotationsPayload = {
  designer_tags: string[];
  designer_notes: string;
};
