"use client";

import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

interface LeaderboardControlsProps {
  period: "day" | "week" | "month";
  onPeriodChange: (period: "day" | "week" | "month") => void;
}

export function LeaderboardControls({ period, onPeriodChange }: LeaderboardControlsProps) {
  const periods: ("day" | "week" | "month")[] = ["day", "week", "month"];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          {period.charAt(0).toUpperCase() + period.slice(1)} Period
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {periods.map((p) => (
          <DropdownMenuItem key={p} onClick={() => onPeriodChange(p)}>
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
