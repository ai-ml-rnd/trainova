"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Suggestion {
  id: string;
  type: "text" | "image" | "audio";
  content: string;
  confidence: number;
  model: string;
  metadata: Record<string, any>;
}

interface SuggestionListProps {
  suggestions: Suggestion[];
}

export function SuggestionList({ suggestions }: SuggestionListProps) {
  const [activeTab, setActiveTab] = useState("content");

  if (suggestions.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        No suggestions to display
      </div>
    );
  }

  const suggestion = suggestions[0];

  return (
    <div className="flex-1 flex flex-col gap-4">
      {/* Suggestion Header */}
      <div className="flex items-center justify-between">
        <Badge variant="outline" className="text-xs">
          {suggestion.type.toUpperCase()}
        </Badge>
        <Badge variant="secondary" className="text-xs">
          Model: {suggestion.model}
        </Badge>
        <Badge variant={suggestion.confidence > 0.7 ? "default" : "destructive"} className="text-xs">
          Confidence: {suggestion.confidence.toFixed(2)}
        </Badge>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="metadata">Metadata</TabsTrigger>
          <TabsTrigger value="model">Model Details</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="flex-1 flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Suggested Content</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-sm whitespace-pre-wrap p-4 border rounded-md bg-muted/50">
                {suggestion.content}
              </div>
            </CardContent>
          </Card>

          {suggestion.type === "text" && (
            <Card>
              <CardHeader>
                <CardTitle>Model Response</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="font-mono text-sm whitespace-pre-wrap p-4 border rounded-md bg-primary/5">
                  {suggestion.metadata.model_response || "No model response available"}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="metadata">
          <Card>
            <CardHeader>
              <CardTitle>Suggestion Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(suggestion.metadata).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-muted-foreground">{key}</dt>
                    <dd className="font-mono">{String(value)}</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="model">
          <Card>
            <CardHeader>
              <CardTitle>Model Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <dt className="text-muted-foreground">Model Route</dt>
                <dd className="font-mono">{suggestion.metadata.model_route || "N/A"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Temperature</dt>
                <dd className="font-mono">{suggestion.metadata.temperature || "N/A"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Prompt Tokens</dt>
                <dd className="font-mono">{suggestion.metadata.prompt_tokens || "N/A"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Completion Tokens</dt>
                <dd className="font-mono">{suggestion.metadata.completion_tokens || "N/A"}</dd>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
