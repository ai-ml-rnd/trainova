import { ImageAnnotationCanvas } from "@/components/multimodal/canvas";
import { AnnotationControls } from "@/components/annotator/controls";
import { useAnnotationStore } from "@/stores/annotation";
import { useToast } from "@/hooks/use-toast";

export default function ImageAnnotationPage() {
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
      <div className="border-b px-4 py-2 flex items-center justify-between bg-muted/50">
        <div className="flex items-center gap-4">
          <div className="flex flex-col">
            <span className="text-sm font-medium">Record {currentIndex + 1} of {totalRecords}</span>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={handlePrev} disabled={currentIndex === 0}>
              Previous
            </Button>
            <Button onClick={handleNext} disabled={currentIndex === totalRecords - 1}>
              Next
            </Button>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">Save Draft</Button>
          <Button variant="outline" size="sm">Skip</Button>
          <Button variant="outline" size="sm">Quit</Button>
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 overflow-hidden">
        <ImageAnnotationCanvas record={currentRecord} />

        <AnnotationControls record={currentRecord} onSubmit={submitResponse} />
      </div>
    </div>
  );
}
