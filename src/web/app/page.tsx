import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="flex flex-col items-center justify-center text-center space-y-8">
        <h1 className="text-5xl font-bold tracking-tight">Forge</h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          Unified Data Platform for LLM & VLM Training. Create, curate, generate,
          and annotate datasets for your models.
        </p>
        <div className="flex gap-4">
          <Button asChild size="lg">
            <Link href="/login">Sign In</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/docs">Documentation</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
