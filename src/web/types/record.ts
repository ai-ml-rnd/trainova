export interface Record {
  id: string;
  dataset_id: string;
  text?: string;
  image_url?: string;
  audio_url?: string;
  metadata: Record<string, any>;
  annotated?: boolean;
  submitted_at?: string;
}

export interface Annotation {
  record_id: string;
  annotation: Record<string, any>;
  metadata: Record<string, any>;
}

export interface AnnotationQueue {
  id: string;
  name: string;
  dataset_id: string;
  strategy: string;
  total_records: number;
  annotated_count: number;
}
