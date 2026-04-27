import { SharedButton } from "@swipelearn/ui/button";
import { SharedCard } from "@swipelearn/ui/card";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-12 p-8">
      {/* Hero */}
      <div className="text-center space-y-4 max-w-2xl">
        <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-[var(--text-secondary)]">
          <span>📚</span>
          <span>Knowledge Cards for the curious mind</span>
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-[var(--foreground)]">
          Swipe through the{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)]">
            best ideas
          </span>{" "}
          on the internet
        </h1>
        <p className="text-lg text-[var(--text-secondary)]">
          Paste any blog URL. AI extracts the key insights. Swipe through them
          like TikTok.
        </p>
        <div className="flex gap-4 justify-center">
          <SharedButton appName="web" variant="primary">
            Get the App
          </SharedButton>
          <SharedButton appName="web" variant="ghost">
            Learn More
          </SharedButton>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        <SharedCard>
          <div className="text-2xl mb-3">🔗</div>
          <h3 className="font-bold text-[var(--foreground)] mb-2">Paste Any URL</h3>
          <p className="text-sm text-[var(--text-secondary)]">
            Drop in any blog post URL from any creator. We handle the rest.
          </p>
        </SharedCard>
        <SharedCard>
          <div className="text-2xl mb-3">✨</div>
          <h3 className="font-bold text-[var(--foreground)] mb-2">AI Extracts Insights</h3>
          <p className="text-sm text-[var(--text-secondary)]">
            GPT-4o-mini distills every post into a TL;DR, key points, and a
            steal insight.
          </p>
        </SharedCard>
        <SharedCard>
          <div className="text-2xl mb-3">👆</div>
          <h3 className="font-bold text-[var(--foreground)] mb-2">Swipe & Learn</h3>
          <p className="text-sm text-[var(--text-secondary)]">
            Navigate cards like TikTok. Save the ones you want to revisit.
          </p>
        </SharedCard>
      </div>
    </main>
  );
}
