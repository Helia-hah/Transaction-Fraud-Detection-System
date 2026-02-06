import TransactionAnalyzer from '@/components/analyzer';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-gray-100 to-slate-200 text-gray-900">
      
      {/* Header */}
      <header className="w-full bg-gradient-to-r from-slate-800 to-slate-900 text-white">
        <div className="mx-auto max-w-6xl px-6 py-12 flex flex-col items-center text-center gap-3">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight">
            AI Transaction Guardian
          </h1>
          <p className="text-base md:text-lg text-slate-300 max-w-xl">
            Securely analyze transaction data and identify suspicious or potentially fraudulent activity using AI.
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto max-w-6xl px-6 py-16">
        <div className="bg-white rounded-3xl shadow-lg border border-gray-200 p-8 md:p-12">
          <TransactionAnalyzer />
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-6 text-center text-sm text-gray-500">
        Built with Next.js · Tailwind CSS · OpenAI
      </footer>
    </div>
  );
}
