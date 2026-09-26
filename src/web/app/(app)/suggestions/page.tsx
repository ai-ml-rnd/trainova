import { SuggestionList } from "@/components/suggestions/list";
import { SuggestionControls } from "@/components/suggestions/controls";
import { useSuggestionStore } from "@/stores/suggestion";
import { useToast } from "@/hooks/use-toast";

export default function SuggestionsPage() {
  const { toast } = useToast();
  const { currentSuggestion, nextSuggestion, accept, reject, skip } = useSuggestionStore();

  const handleAccept = () => {
    accept(currentSuggestion?.id);
    nextSuggestion();
  };

  const handleReject = () => {
    reject(currentSuggestion?.id);
    nextSuggestion();
  };

  const handleSkip = () => {
    skip(currentSuggestion?.id);
    nextSuggestion();
  };

  if (!currentSuggestion) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-xl font-semibold">No more suggestions</h2>
          <p className="text-muted-foreground mt-2">All suggestions have been reviewed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b px-4 py-2 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Active Learning Suggestions</h1>
        <div className="text-sm text-muted-foreground">
          {currentSuggestion?.score ? `Confidence: ${currentSuggestion.score.toFixed(2)}` : "Confidence: N/A"}
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 overflow-hidden">
        <SuggestionList suggestions={[currentSuggestion]} />

        <SuggestionControls
          suggestion={currentSuggestion}
          onAccept={handleAccept}
          onReject={handleReject}
          onSkip={handleSkip}
        />
      </div>
    </div>
  );
}
