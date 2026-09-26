import { Leaderboard } from "@/components/dashboard/leaderboard";
import { LeaderboardStats } from "@/components/dashboard/stats";
import { LeaderboardControls } from "@/components/dashboard/controls";
import { useLeaderboardStore } from "@/stores/leaderboard";
import { useToast } from "@/hooks/use-toast";

export default function LeaderboardPage() {
  const { toast } = useToast();
  const { users, period, setPeriod } = useLeaderboardStore();

  const handlePeriodChange = (newPeriod: "day" | "week" | "month") => {
    setPeriod(newPeriod);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b px-4 py-2 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Annotation Leaderboard</h1>
        <LeaderboardControls period={period} onPeriodChange={handlePeriodChange} />
      </div>

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 overflow-hidden">
        <Leaderboard users={users} />

        <LeaderboardStats stats={getLeaderboardStats(users)} />
      </div>
    </div>
  );
}

function getLeaderboardStats(users: Array<{ name: string; annotations: number; average_score: number }>) {
  const totalAnnotations = users.reduce((sum, user) => sum + user.annotations, 0);
  const avgScore = users.reduce((sum, user) => sum + user.average_score, 0) / users.length;
  const topUser = users[0];

  return {
    totalAnnotations,
    avgScore: avgScore.toFixed(2),
    topUser: topUser?.name || "N/A",
  };
}
