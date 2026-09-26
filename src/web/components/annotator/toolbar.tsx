import { Button } from "@/components/ui/button";

interface AnnotationToolbarProps {
  currentIndex: number;
  totalRecords: number;
  onNext: () => void;
  onPrev: () => void;
}

export function AnnotationToolbar({ currentIndex, totalRecords, onNext, onPrev }: AnnotationToolbarProps) {
  const progress = Math.round(((currentIndex + 1) / totalRecords) * 100);

  return (
    <div className="border-b px-4 py-2 flex items-center justify-between bg-muted/50">
      <div className="flex items-center gap-4">
        <div className="flex flex-col">
          <span className="text-sm font-medium">Record {currentIndex + 1} of {totalRecords}</span>
          <div className="w-32 h-2 bg-muted rounded-full mt-1 overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={onPrev} disabled={currentIndex === 0}>
            Previous
          </Button>
          <Button onClick={onNext} disabled={currentIndex === totalRecords - 1}>
            Next
          </Button>
        </div>
      </div>

      <div className="flex gap-2">
        <Button variant="outline" size="sm">
          Save Draft
        </Button>
        <Button variant="outline" size="sm">
          Skip
        </Button>
        <Button variant="outline" size="sm">
          Quit
        </Button>
      </div>
    </div>
  );
}
