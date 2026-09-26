import { create } from "zustand";

interface Suggestion {
  id: string;
  type: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

interface SuggestionState {
  suggestions: Suggestion[];
  currentIndex: number;
  currentSuggestion: Suggestion | null;
  isLoading: boolean;
  error: string | null;

  loadSuggestions: (datasetId: string) => Promise<void>;
  nextSuggestion: () => void;
  accept: (suggestionId: string) => void;
  reject: (suggestionId: string) => void;
  skip: (suggestionId: string) => void;
}

export const useSuggestionStore = create<SuggestionState>((set, get) => ({
  suggestions: [],
  currentIndex: 0,
  currentSuggestion: null,
  isLoading: false,
  error: null,

  loadSuggestions: async (datasetId: string) => {
    set({ isLoading: true, error: null });
    try {
      // TODO: Fetch active learning suggestions from API
      const response = await fetch(`/api/datasets/${datasetId}/suggestions`);
      const data = await response.json();

      set({
        suggestions: data.suggestions,
        currentIndex: 0,
        currentSuggestion: data.suggestions[0] || null,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load suggestions",
        isLoading: false,
      });
    }
  },

  nextSuggestion: () => {
    const { currentIndex, suggestions } = get();
    if (currentIndex < suggestions.length - 1) {
      set({ currentIndex: currentIndex + 1, currentSuggestion: suggestions[currentIndex + 1] });
    } else {
      set({ currentSuggestion: null });
    }
  },

  accept: (suggestionId: string) => {
    // TODO: Submit accept action to API
    console.log("Accept suggestion:", suggestionId);
  },

  reject: (suggestionId: string) => {
    // TODO: Submit reject action to API
    console.log("Reject suggestion:", suggestionId);
  },

  skip: (suggestionId: string) => {
    // TODO: Submit skip action to API
    console.log("Skip suggestion:", suggestionId);
  },
}));
