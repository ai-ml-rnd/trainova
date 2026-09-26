"use client";

import { useRef, useState, useCallback } from "react";
import Konva from "konva";
import { Layer, Image as KonvaImage, Rect, Circle, Text } from "react-konva";

interface ImageAnnotationCanvasProps {
  record: {
    id: string;
    image_url?: string;
    annotations?: any[];
    metadata: Record<string, any>;
  };
}

export function ImageAnnotationCanvas({ record }: ImageAnnotationCanvasProps) {
  const imageRef = useRef<Konva.Image | null>(null);
  const [shapes, setShapes] = useState<any[]>(record.annotations || []);
  const [activeTool, setActiveTool] = useState<"bbox" | "polygon" | "keypoint" | "select">("bbox");

  const handleImageLoad = useCallback((e: any) => {
    const img = e.target;
    // Resize to fit canvas while maintaining aspect ratio
    const maxDim = 1024;
    const scale = Math.min(maxDim / img.width, maxDim / img.height, 1);
    img.scale({ x: scale, y: scale });
    img.position({ x: (maxDim - img.width * scale) / 2, y: (maxDim - img.height * scale) / 2 });
    img.cache();
    img.getLayer()?.draw();
  }, []);

  const handleAddShape = useCallback((shape: any) => {
    setShapes((prev) => [...prev, shape]);
  }, []);

  const handleDeleteShape = useCallback((shapeId: string) => {
    setShapes((prev) => prev.filter((s) => s.id !== shapeId));
  }, []);

  return (
    <div className="flex-1 flex flex-col gap-4">
      <div className="border rounded-md overflow-hidden">
        <div className="flex gap-2 border-b p-2 bg-muted/50">
          <button
            onClick={() => setActiveTool("bbox")}
            className={`px-3 py-1 text-sm rounded ${
              activeTool === "bbox" ? "bg-primary text-primary-foreground" : ""
            }`}
          >
            Bounding Box
          </button>
          <button
            onClick={() => setActiveTool("polygon")}
            className={`px-3 py-1 text-sm rounded ${
              activeTool === "polygon" ? "bg-primary text-primary-foreground" : ""
            }`}
          >
            Polygon
          </button>
          <button
            onClick={() => setActiveTool("keypoint")}
            className={`px-3 py-1 text-sm rounded ${
              activeTool === "keypoint" ? "bg-primary text-primary-foreground" : ""
            }`}
          >
            Keypoint
          </button>
          <button
            onClick={() => setActiveTool("select")}
            className={`px-3 py-1 text-sm rounded ${
              activeTool === "select" ? "bg-primary text-primary-foreground" : ""
            }`}
          >
            Select
          </button>
        </div>

        <div className="relative bg-muted/30 flex items-center justify-center">
          <Konva.Stage
            width={1024}
            height={1024}
            className="rounded-md"
            onMouseDown={(e) => {
              if (activeTool === "bbox") {
                const pos = e.target.getStage()?.getPointerPosition();
                if (pos) {
                  handleAddShape({
                    id: crypto.randomUUID(),
                    type: "bbox",
                    x: pos.x,
                    y: pos.y,
                    width: 0,
                    height: 0,
                    stroke: "blue",
                    strokeWidth: 2,
                  });
                }
              }
            }}
            onMouseMove={(e) => {
              if (activeTool === "bbox" && shapes.length > 0) {
                const pos = e.target.getStage()?.getPointerPosition();
                if (pos) {
                  const lastShape = shapes[shapes.length - 1];
                  if (lastShape.type === "bbox" && lastShape.width === 0 && lastShape.height === 0) {
                    setShapes((prev) => {
                      const updated = [...prev];
                      updated[updated.length - 1] = {
                        ...lastShape,
                        width: pos.x - lastShape.x,
                        height: pos.y - lastShape.y,
                      };
                      return updated;
                    });
                  }
                }
              }
            }}
            onMouseUp={(e) => {
              if (activeTool === "bbox" && shapes.length > 0) {
                const pos = e.target.getStage()?.getPointerPosition();
                if (pos) {
                  const lastShape = shapes[shapes.length - 1];
                  if (lastShape.type === "bbox" && lastShape.width === 0 && lastShape.height === 0) {
                    setShapes((prev) => {
                      const updated = [...prev];
                      updated[updated.length - 1] = {
                        ...lastShape,
                        width: Math.abs(pos.x - lastShape.x),
                        height: Math.abs(pos.y - lastShape.y),
                      };
                      return updated;
                    });
                  }
                }
              }
            }}
          >
            <Layer>
              {/* Image */}
              {record.image_url && (
                <KonvaImage
                  ref={imageRef}
                  image={new Image()}
                  src={record.image_url}
                  onLoad={handleImageLoad}
                  draggable
                />
              )}

              {/* Shapes */}
              {shapes.map((shape) => (
                <Rect
                  key={shape.id}
                  x={shape.x}
                  y={shape.y}
                  width={shape.width}
                  height={shape.height}
                  stroke={shape.stroke}
                  strokeWidth={shape.strokeWidth}
                  draggable={shape.type !== "bbox"}
                  onClick={() => handleDeleteShape(shape.id)}
                  onTap={() => handleDeleteShape(shape.id)}
                />
              ))}
            </Layer>
          </Konva.Stage>
        </div>

        <div className="p-2 text-sm text-muted-foreground">
          {shapes.length} shape(s) drawn
        </div>
      </div>

      {/* COCO Export Preview */}
      <div className="border rounded-md p-4">
        <h3 className="text-sm font-medium mb-2">COCO-Style Export Preview</h3>
        <pre className="text-xs font-mono overflow-auto max-h-40">
          {JSON.stringify(
            {
              images: [
                {
                  id: record.id,
                  width: 1024,
                  height: 1024,
                  file_name: record.metadata.original_filename || "",
                },
              ],
              annotations: shapes.map((s) => ({
                id: s.id,
                image_id: record.id,
                category_id: 1,
                bbox: [s.x, s.y, s.width, s.height],
                area: s.width * s.height,
                iscrowd: 0,
              })),
              categories: [{ id: 1, name: "object" }],
            },
            null,
            2
          )}
        </pre>
      </div>
    </div>
  );
}
