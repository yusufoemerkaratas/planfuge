export interface PlanMetadata {
  plan_id?: string;
  file_path?: string;
  image_width_px?: number;
  image_height_px?: number;
  source_type?: string;
  original_pdf_available?: boolean;
  scale_text_visible?: string;
  contains_red_markups?: boolean;
  notes?: string;
}

interface MetadataApiResponse {
  plan_id?: string;
  exists?: boolean;
  metadata?: PlanMetadata;
  warnings?: string[];
  errors?: string[];
}

export type MetadataResult =
  | { kind: "available"; metadata: PlanMetadata }
  | { kind: "missing"; message: string }
  | { kind: "error"; message: string };

export function parseMetadataResponse(
  response: MetadataApiResponse,
): MetadataResult {
  if (response.exists && response.metadata) {
    return { kind: "available", metadata: response.metadata };
  }

  if (response.errors?.length) {
    return { kind: "error", message: response.errors.join("; ") };
  }

  return {
    kind: "missing",
    message:
      response.warnings?.join("; ") ||
      "Metadata is not available for this plan.",
  };
}
