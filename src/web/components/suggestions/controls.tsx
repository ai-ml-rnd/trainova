"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

interface SuggestionControlsProps {
  suggestion: {
    id: string;
    type: string;
    content: string;
    metadata: Record<string, any>;
  };
  onAccept: () => void;
  onReject: () => void;
  onSkip: () => void;
}

export function SuggestionControls({ suggestion, onAccept, onReject, onSkip }: SuggestionControlsProps) {
  const { toast } = useToast();
  const [feedback, setFeedback] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (action: "accept" | "reject" | "skip") => {
    if (isSubmitting) return;

    setIsSubmitting(true);
    try {
      // TODO: Submit feedback to API
      await fetch("/api/suggestions/feedback", {
        method: "POST",
        body: JSON.stringify({
          suggestion_id: suggestion.id,
          action,
          feedback,
        }),
      });

      toast({
        title: "Action Submitted",
        description: `Suggestion ${action}ed successfully.`,
      });

      if (action === "accept") {
        onAccept();
      } else if (action === "reject") {
        onReject();
      } else {
        onSkip();
      }

      setFeedback("");
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "An error occurred while submitting your action.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full md:w-80 flex flex-col gap-4 border-l md:border-l-0 md:border-r p-4">
      <div>
        <h2 className="text-lg font-semibold mb-4">Action</h2>

        {/* Feedback */}
        <div className="mb-4">
          <Label htmlFor="feedback" className="mb-2 block">
            Feedback (optional)
          </Label>
          <Textarea
            id="feedback"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Why did you accept/reject/skip this suggestion?"
            className="resize-none"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => handleSubmit("skip")} disabled={isSubmitting}>
          Skip
        </Button>
        <Button variant="destructive" onClick={() => handleSubmit("reject")} disabled={isSubmitting}>
          Reject
        </Button>
        <Button onClick={() => handleSubmit("accept")} disabled={isSubmitting}>
          Accept
        </Button>
      </div>
    </div>
  );
}
