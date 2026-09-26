"use client";

import { useState, useRef, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

interface AnnotatorProps {
  record: {
    id: string;
    text?: string;
    image_url?: string;
    audio_url?: string;
    metadata: Record<string, any>;
  };
}

export function Annotator({ record }: AnnotatorProps) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"text" | "image" | "audio">("text");
  const [text, setText] = useState(record.text || "");

  useEffect(() => {
    setText(record.text || "");
  }, [record]);

  return (
    <div className="flex-1 flex flex-col gap-4">
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b">
        {record.text && (
          <button
            onClick={() => setActiveTab("text")}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === "text" ? "border-b-2 border-primary" : "text-muted-foreground"
            }`}
          >
            Text
          </button>
        )}
        {record.image_url && (
          <button
            onClick={() => setActiveTab("image")}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === "image" ? "border-b-2 border-primary" : "text-muted-foreground"
            }`}
          >
            Image
          </button>
        )}
        {record.audio_url && (
          <button
            onClick={() => setActiveTab("audio")}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === "audio" ? "border-b-2 border-primary" : "text-muted-foreground"
            }`}
          >
            Audio
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="flex-1 min-h-0">
        {activeTab === "text" && (
          <div className="flex-1 flex flex-col">
            <label className="text-sm font-medium mb-2">Input Text</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="flex-1 p-4 border rounded-md font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              spellCheck={false}
              placeholder="Record text content..."
            />
          </div>
        )}

        {activeTab === "image" && record.image_url && (
          <div className="flex-1 flex flex-col">
            <label className="text-sm font-medium mb-2">Input Image</label>
            <img
              src={record.image_url}
              alt="Input"
              className="flex-1 max-h-full object-contain rounded-md"
            />
          </div>
        )}

        {activeTab === "audio" && record.audio_url && (
          <div className="flex-1 flex flex-col">
            <label className="text-sm font-medium mb-2">Input Audio</label>
            <audio controls src={record.audio_url} className="w-full" />
          </div>
        )}
      </div>

      {/* Metadata */}
      {Object.keys(record.metadata).length > 0 && (
        <div className="border rounded-md p-4">
          <h3 className="text-sm font-medium mb-2">Metadata</h3>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(record.metadata).map(([key, value]) => (
              <div key={key}>
                <dt className="text-muted-foreground">{key}</dt>
                <dd className="font-mono">{String(value)}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}
