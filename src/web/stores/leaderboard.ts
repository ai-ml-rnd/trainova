import { create } from "zustand";

interface User {
  name: string;
  annotations: number;
  average_score: number;
}

interface LeaderboardState {
  users: User[];
  period: "day" | "week" | "month";
  isLoading: boolean;
  error: string | null;

  loadLeaderboard: (period: "day" | "week" | "month") => Promise<void>;
  setPeriod: (period: "day" | "week" | "month") => void;
}

export const useLeaderboardStore = create<LeaderboardState>((set, get) => ({
  users: [],
  period: "week",
  isLoading: false,
  error: null,

  loadLeaderboard: async (period: "day" | "week" | "month") => {
    set({ isLoading: true, error: null, period });
    try {
      // TODO: Fetch leaderboard data from API
      const response = await fetch(`/api/leaderboard?period=${period}`);
      const data = await response.json();

      // Sort users by annotations (descending)
      const sortedUsers = data.users.sort((a: User, b: User) => b.annotations - a.annotations);

      // Add ranks
      const rankedUsers = sortedUsers.map((user: User, index: number) => ({
        ...user,
        rank: index + 1,
      }));

      set({
        users: rankedUsers,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to load leaderboard",
        isLoading: false,
      });
    }
  },

  setPeriod: (period: "day" | "week" | "month") => {
    get().loadLeaderboard(period);
  },
}));
