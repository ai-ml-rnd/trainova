import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface LeaderboardStats {
  totalAnnotations: number;
  avgScore: string;
  topUser: string;
}

interface LeaderboardStatsProps {
  stats: LeaderboardStats;
}

export function LeaderboardStats({ stats }: LeaderboardStatsProps) {
  return (
    <div className="w-full md:w-64 flex flex-col gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-muted-foreground">Total Annotations</p>
            <p className="text-2xl font-bold">{stats.totalAnnotations}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Average Score</p>
            <p className="text-2xl font-bold">{stats.avgScore}</p>
          </div>

          <div>
            <p className="text-sm text-muted-foreground">Top Annotator</p>
            <p className="text-xl font-bold">{stats.topUser}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
