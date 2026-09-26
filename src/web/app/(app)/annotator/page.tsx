import { Annotator } from "@/components/annotator/annotator";
import { AnnotationControls } from "@/components/annotator/controls";
import { AnnotationToolbar } from "@/components/annotator/toolbar";
import { useAnnotationStore } from "@/stores/annotation";
import { useToast } from "@/hooks/use-toast";

export default function AnnotatorPage() {
  const { toast } = useToast();
  const { currentRecord, currentIndex, totalRecords, nextRecord, prevRecord, submitResponse } = useAnnotationStore();

  const handleNext = () => {
    if (currentIndex < totalRecords - 1) {
      nextRecord();
    } else {
      toast({
        title: "Annotation Complete",
        description: "All records have been annotated.",
      });
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      prevRecord();
    }
  };

  if (!currentRecord) {
    return <div className="flex items-center justify-center h-full">Loading records...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <AnnotationToolbar
        currentIndex={currentIndex}
        totalRecords={totalRecords}
        onNext={handleNext}
        onPrev={handlePrev}
      />

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 overflow-hidden">
        <Annotator record={currentRecord} />

        <AnnotationControls
          record={currentRecord}
          onSubmit={submitResponse}
        />
      </div>
    </div>
  );
}
