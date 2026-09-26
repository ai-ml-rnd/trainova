import { create } from "zustand";
import { Record } from "@/types/record";

interface AnnotationState {
  records: Record[];
  currentIndex: number;
  currentRecord: Record | null;
  isLoading: boolean;
  error: string | null;

  loadQueue: (queueId: string) => Promise<void>;
  nextRecord: () => void;
  prevRecord: () => void;
  submitResponse: (response: {
    record_id: string;
    annotation: Record<string, any>;
    metadata: Record<string, any>;
  }) => Promise<void>;
}

export const useAnnotationStore = create<AnnotationState>((set, get) => ({
  records: [],
  currentIndex: 0,
  currentRecord: null,
  isLoading: false,
  error: null,

  loadQueue: async (queueId: string) => {
    set({ isLoading: true, error: null });
    try {
      // TODO: Fetch queue records from API
      const response = await fetch(`/api/annotation-queues/${queueId}/records`);
      const data = await response.json();

      set({
        records: data.records,
        currentIndex: 0,
        currentRecord: data.records[0] || null,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load annotation queue",
        isLoading: false,
      });
    }
  },

  nextRecord: () => {
    const { currentIndex, records } = get();
    if (currentIndex < records.length - 1) {
      set({ currentIndex: currentIndex + 1, currentRecord: records[currentIndex + 1] });
    }
  },

  prevRecord: () => {
    const { currentIndex } = get();
    if (currentIndex > 0) {
      set({ currentIndex: currentIndex - 1, currentRecord: records[currentIndex - 1] });
    }
  },

  submitResponse: async (response) => {
    const { records, currentIndex } = get();
    try {
      // TODO: Submit response to API
      await fetch("/api/annotations", {
        method: "POST",
        body: JSON.stringify(response),
      });

      // Update current record with submission metadata
      const updatedRecords = [...records];
      if (updatedRecords[currentIndex]) {
        updatedRecords[currentIndex].metadata = {
          ...updatedRecords[currentIndex].metadata,
          annotated: true,
          submitted_at: new Date().toISOString(),
        };
      }

      set({ records: updatedRecords });
    } catch (error) {
      throw error;
    }
  },
}));
