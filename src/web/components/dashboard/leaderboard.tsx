"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface User {
  name: string;
  annotations: number;
  average_score: number;
  rank?: number;
}

interface LeaderboardProps {
  users: User[];
}

export function Leaderboard({ users }: LeaderboardProps) {
  return (
    <div className="flex-1 flex flex-col gap-4">
      <h2 className="text-lg font-semibold">Leaderboard</h2>

      <div className="flex-1 overflow-y-auto space-y-2">
        {users.map((user, index) => (
          <Card key={user.name} className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="w-8 justify-center">
                #{user.rank || index + 1}
              </Badge>

              <Avatar>
                <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`} />
                <AvatarFallback>{user.name.substring(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>

              <div>
                <h3 className="font-medium">{user.name}</h3>
                <p className="text-sm text-muted-foreground">
                  Average Score: {user.average_score.toFixed(2)}
                </p>
              </div>
            </div>

            <div className="ml-auto text-right">
              <p className="text-lg font-bold">{user.annotations}</p>
              <p className="text-sm text-muted-foreground">Annotations</p>
            </div>
          </Card>
        ))}

        {users.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No users yet. Start annotating to appear on the leaderboard!
          </div>
        )}
      </div>
    </div>
  );
}
