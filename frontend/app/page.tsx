'use client';

import { useState } from 'react';
import { Search, TrendingUp, Shield, Zap } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [productUrl, setProductUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productUrl.trim()) return;

    setIsLoading(true);
    
    // Carry the product URL into the due-diligence workflow.
    const encodedUrl = encodeURIComponent(productUrl);
    router.push(`/due-diligence?url=${encodedUrl}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">F</span>
              </div>
              <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                FashnAI
              </h1>
            </div>
            <nav className="hidden md:flex space-x-6">
              <a href="/" className="text-gray-600 hover:text-gray-900">Home</a>
              <a href="/product" className="text-blue-600 font-semibold hover:text-blue-800">Product comparison ↗</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Fashion due diligence.
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Know before you buy.
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Independent research checks a product's price, details, availability, and reviews against multiple sources, so you can make a more informed decision.
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-3xl mx-auto mb-16">
          <form onSubmit={handleSearch} className="relative">
            <div className="flex items-center bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden hover:shadow-3xl transition-shadow">
              <div className="pl-6 pr-4">
                <Search className="w-6 h-6 text-gray-400" />
              </div>
              <input
                type="text"
                value={productUrl}
                onChange={(e) => setProductUrl(e.target.value)}
                placeholder="Paste a product URL to start your due diligence..."
                className="flex-1 py-5 px-2 text-lg focus:outline-none"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !productUrl.trim()}
                className="m-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Starting research...' : 'Start due diligence'}
              </button>
            </div>
          </form>
          <button
            type="button"
            onClick={() => setProductUrl('https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG?color=JK3&size=M')}
            className="block mx-auto mt-5 px-5 py-3 bg-white/80 border border-gray-200 rounded-xl text-left hover:border-blue-400 hover:shadow-md transition-all group"
          >
            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1 group-hover:text-blue-600">
              Try a sample product
            </span>
            <span className="block text-sm text-gray-700 font-mono">
              https://www.thenorthface.com/de-de/p/herren-211701/limbara-isolierjacke-fur-herren-NF0A89EG
            </span>
          </button>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold mb-2">Research across sources</h3>
            <p className="text-gray-600">
              Parallel research gathers product details, prices, availability, and customer feedback from source pages.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold mb-2">Independent verification</h3>
            <p className="text-gray-600">
              A separate fact-checker looks for outside evidence that confirms or challenges the research findings.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold mb-2">Evidence behind the verdict</h3>
            <p className="text-gray-600">
              Inspect verdicts, confidence estimates, source quotes, and the research trace before making a decision.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-3xl p-12 shadow-xl">
          <h3 className="text-3xl font-bold text-center mb-12">A clearer picture before you buy</h3>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h4 className="font-semibold mb-2">Choose a product</h4>
              <p className="text-sm text-gray-600">Start with a product page URL</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h4 className="font-semibold mb-2">Research in parallel</h4>
              <p className="text-sm text-gray-600">Specialist agents examine price, reviews, and product details</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h4 className="font-semibold mb-2">Verify findings</h4>
              <p className="text-sm text-gray-600">A fact-checker seeks independent confirmation or contradiction</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-pink-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                4
              </div>
              <h4 className="font-semibold mb-2">Review the evidence</h4>
              <p className="text-sm text-gray-600">Explore source quotes, confidence, verdicts, and research trace</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-20 py-8 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p>&copy; 2026 FashnAI. Independent fashion product due diligence.</p>
        </div>
      </footer>
    </div>
  );
}
