"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface AnnotationControlsProps {
  record: {
    id: string;
    text?: string;
    metadata: Record<string, any>;
  };
  onSubmit: (response: {
    record_id: string;
    annotation: Record<string, any>;
    metadata: Record<string, any>;
  }) => Promise<void>;
}

export function AnnotationControls({ record, onSubmit }: AnnotationControlsProps) {
  const { toast } = useToast();
  const [annotation, setAnnotation] = useState({
    quality_score: 5,
    correctness_score: 5,
    relevance_score: 5,
    feedback: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = useCallback(async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        record_id: record.id,
        annotation: {
          quality_score: annotation.quality_score,
          correctness_score: annotation.correctness_score,
          relevance_score: annotation.relevance_score,
          feedback: annotation.feedback,
        },
        metadata: {
          annotated_at: new Date().toISOString(),
        },
      });

      toast({
        title: "Annotation Submitted",
        description: "Your annotation has been saved.",
      });

      // Reset form
      setAnnotation({
        quality_score: 5,
        correctness_score: 5,
        relevance_score: 5,
        feedback: "",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Submission Failed",
        description: "An error occurred while submitting your annotation.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [annotation, isSubmitting, onSubmit, record.id, toast]);

  return (
    <div className="w-full md:w-80 flex flex-col gap-4 border-l md:border-l-0 md:border-r p-4">
      <div>
        <h2 className="text-lg font-semibold mb-4">Annotation</h2>

        <div className="space-y-4">
          {/* Quality Score */}
          <div>
            <Label className="mb-2 block">
              Quality Score: {annotation.quality_score}
              <Badge variant="outline" className="ml-2">
                {annotation.quality_score >= 4 ? "High" : annotation.quality_score >= 2 ? "Medium" : "Low"}
              </Badge>
            </Label>
            <Slider
              value={[annotation.quality_score]}
              onValueChange={(value) => setAnnotation({ ...annotation, quality_score: value[0] })}
              min={1}
              max={5}
              step={1}
              className="py-2"
            />
          </div>

          {/* Correctness Score */}
          <div>
            <Label className="mb-2 block">
              Correctness Score: {annotation.correctness_score}
            </Label>
            <Slider
              value={[annotation.correctness_score]}
              onValueChange={(value) => setAnnotation({ ...annotation, correctness_score: value[0] })}
              min={1}
              max={5}
              step={1}
              className="py-2"
            />
          </div>

          {/* Relevance Score */}
          <div>
            <Label className="mb-2 block">
              Relevance Score: {annotation.relevance_score}
            </Label>
            <Slider
              value={[annotation.relevance_score]}
              onValueChange={(value) => setAnnotation({ ...annotation, relevance_score: value[0] })}
              min={1}
              max={5}
              step={1}
              className="py-2"
            />
          </div>

          {/* Feedback */}
          <div>
            <Label htmlFor="feedback" className="mb-2 block">
              Feedback (optional)
            </Label>
            <Textarea
              id="feedback"
              value={annotation.feedback}
              onChange={(e) => setAnnotation({ ...annotation, feedback: e.target.value })}
              placeholder="Enter your feedback..."
              className="resize-none"
            />
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full"
      >
        {isSubmitting ? "Submitting..." : "Submit Annotation"}
      </Button>
    </div>
  );
}
