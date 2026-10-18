'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CitedClaim {
  claim: string;
  source_url: string;
  quote: string;
  confidence: number;
  category: string;
}

interface CheckedClaim extends CitedClaim {
  verdict: 'verified' | 'contested' | 'unsupported';
  kind?: 'fact' | 'claim';
  checker_note: string;
  checker_source_url?: string;
  checker_quote?: string;
}

interface TraceStep {
  agent: string;
  action: string;
  detail: string;
}

interface DueDiligenceReport {
  product_name: string;
  product_url: string;
  verdict: string;
  checked_claims: CheckedClaim[];
  trace: TraceStep[];
}

const VERDICT_STYLE: Record<string, string> = {
  verified: 'bg-green-100 text-green-800 border-green-200',
  contested: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  unsupported: 'bg-red-100 text-red-800 border-red-200',
};

const VERDICT_LABEL: Record<string, string> = {
  verified: 'Verified',
  contested: 'Contested',
  unsupported: 'Unsupported',
};

const KIND_LABEL: Record<string, string> = {
  fact: 'Fact — from source page',
  claim: 'Claim — independently checked',
};

const CATEGORY_COLORS: Record<string, string> = {
  price: 'bg-blue-50 text-blue-700',
  material: 'bg-purple-50 text-purple-700',
  review: 'bg-yellow-50 text-yellow-700',
  availability: 'bg-teal-50 text-teal-700',
  spec: 'bg-gray-100 text-gray-700',
  sustainability: 'bg-green-50 text-green-700',
};

function ClaimCard({ claim }: { claim: CheckedClaim }) {
  const [expanded, setExpanded] = useState(false);
  const verdictClass = VERDICT_STYLE[claim.verdict] || VERDICT_STYLE.unsupported;
  const catClass = CATEGORY_COLORS[claim.category] || 'bg-gray-100 text-gray-700';

  return (
    <div className={`rounded-xl border p-4 ${verdictClass} mb-3`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${verdictClass}`}>
              {VERDICT_LABEL[claim.verdict]}
            </span>
            {claim.kind && (
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${claim.kind === 'fact' ? 'bg-gray-50 text-gray-600 border-gray-200' : 'bg-indigo-50 text-indigo-700 border-indigo-200'}`}>
                {KIND_LABEL[claim.kind]}
              </span>
            )}
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${catClass}`}>
              {claim.category}
            </span>
            <span className="text-xs text-gray-500">
              confidence: {Math.round(claim.confidence * 100)}%
            </span>
          </div>
          <p className="font-medium text-gray-900 text-sm">{claim.claim}</p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-400 hover:text-gray-700 shrink-0 mt-1"
        >
          {expanded ? 'hide' : 'sources'}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 space-y-2 text-xs border-t border-black/10 pt-3">
          <div>
            <div className="font-semibold text-gray-600 mb-0.5">Agent source</div>
            <a href={claim.source_url} target="_blank" rel="noopener noreferrer"
              className="text-blue-600 underline break-all">{claim.source_url}</a>
            <blockquote className="mt-1 pl-2 border-l-2 border-gray-300 text-gray-600 italic">
              "{claim.quote}"
            </blockquote>
          </div>

          {claim.checker_source_url && (
            <div>
              <div className="font-semibold text-gray-600 mb-0.5">Fact-checker source</div>
              <a href={claim.checker_source_url} target="_blank" rel="noopener noreferrer"
                className="text-blue-600 underline break-all">{claim.checker_source_url}</a>
              {claim.checker_quote && (
                <blockquote className="mt-1 pl-2 border-l-2 border-gray-300 text-gray-600 italic">
                  "{claim.checker_quote}"
                </blockquote>
              )}
            </div>
          )}

          <div className="text-gray-500 italic">{claim.checker_note}</div>
        </div>
      )}
    </div>
  );
}

function TracePanel({ steps }: { steps: TraceStep[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-6 border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-3 bg-gray-50 text-sm font-semibold text-gray-700 hover:bg-gray-100"
      >
        <span>Research trace ({steps.length} steps)</span>
        <span className="text-gray-400">{open ? '▲' : '▼'}</span>
      </button>
      {open && (
        <div className="divide-y divide-gray-100">
          {steps.map((step, i) => (
            <div key={i} className="flex gap-3 px-5 py-3 text-xs">
              <span className="font-mono text-gray-400 shrink-0 w-24">{step.agent}</span>
              <span className={`shrink-0 font-semibold w-20 ${
                step.action === 'challenge' ? 'text-yellow-600' :
                step.action === 'error' ? 'text-red-500' :
                step.action === 'complete' ? 'text-green-600' : 'text-gray-500'
              }`}>{step.action}</span>
              <span className="text-gray-600">{step.detail}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DueDiligencePage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<DueDiligenceReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const runResearch = useCallback(async (productUrl: string) => {
    if (!productUrl.trim()) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await axios.post(`${API_URL}/api/due-diligence`, { product_url: productUrl }, { timeout: 300000 });
      setReport(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initialUrl = new URLSearchParams(window.location.search).get('url');
    if (!initialUrl) return;
    setUrl(initialUrl);
    void runResearch(initialUrl);
  }, [runResearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void runResearch(url);
  };

  const verdictBg = report?.verdict.startsWith('Worth')
    ? 'bg-green-50 border-green-300 text-green-800'
    : report?.verdict.startsWith('Skip')
    ? 'bg-red-50 border-red-300 text-red-800'
    : 'bg-yellow-50 border-yellow-300 text-yellow-800';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={() => router.push('/')} className="text-sm text-gray-500 hover:text-gray-900">
            ← FashnAI
          </button>
          <h1 className="font-bold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Product Due Diligence
          </h1>
          <div />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-10">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Is it worth buying?</h2>
          <p className="text-gray-500 text-sm max-w-xl mx-auto">
            Three AI agents research the product. A fourth independently verifies every claim.
            Each source is clickable.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2 mb-8">
          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="Paste a product URL..."
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm"
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl disabled:opacity-50 text-sm"
          >
            {loading ? 'Researching...' : 'Analyse'}
          </button>
        </form>

        <button
          type="button"
          onClick={() => setUrl('https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M')}
          className="block mx-auto mb-8 text-xs text-blue-500 underline"
        >
          Try example: North Face Limbara jacket
        </button>

        {loading && (
          <div className="text-center py-16">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-600 font-medium">Agents are researching and fact-checking...</p>
            <p className="text-xs text-gray-400 mt-1">This takes 60–120 seconds</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">{error}</div>
        )}

        {report && (
          <div>
            <div className={`border rounded-2xl p-5 mb-6 ${verdictBg}`}>
              <div className="text-xs font-semibold uppercase tracking-wide mb-1 opacity-60">Verdict</div>
              <div className="text-xl font-bold">{report.verdict}</div>
              <div className="text-sm mt-1 opacity-70">{report.product_name}</div>
            </div>

            <div className="mb-4 flex gap-4 text-sm text-gray-600">
              <span className="text-green-700 font-semibold">
                {report.checked_claims.filter(c => c.verdict === 'verified').length} verified
              </span>
              <span className="text-yellow-700 font-semibold">
                {report.checked_claims.filter(c => c.verdict === 'contested').length} contested
              </span>
              <span className="text-red-700 font-semibold">
                {report.checked_claims.filter(c => c.verdict === 'unsupported').length} unsupported
              </span>
            </div>

            <div>
              {['contested', 'unsupported', 'verified'].map(v =>
                report.checked_claims
                  .filter(c => c.verdict === v)
                  .map((c, i) => <ClaimCard key={`${v}-${i}`} claim={c} />)
              )}
            </div>

            <TracePanel steps={report.trace} />
          </div>
        )}
      </main>
    </div>
  );
}
