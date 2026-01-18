'use client'

import { useState } from 'react'
import axios from 'axios'

interface AnalysisResult {
  ticker: string
  financial_analysis?: {
    assessment: string
    valuation: string
    trend: string
    strengths: string[]
    concerns: string[]
  }
  sentiment_analysis?: {
    overall_mood: string
    sentiment_score: number
    article_count: number
    key_themes: string[]
  }
  recommendation?: {
    action: string
    confidence: number
    reasoning: string
    risk_level: string
    time_horizon: string
    key_factors: string[]
    entry_strategy: string
    watch_for: string[]
  }
  errors: string[]
}

export default function Home() {
  const [ticker, setTicker] = useState('')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState('')

  const analyzeStock = async () => {
    if (!ticker.trim()) {
      setError('Please enter a stock ticker')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post('http://localhost:8000/analyze', {
        ticker: ticker.toUpperCase(),
        user_query: query || undefined
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze stock')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Investment Research Co-Pilot
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Stock Analysis & Recommendations
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stock Ticker
              </label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="e.g., AAPL, NVDA, TSLA"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Question (Optional)
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Is this a good long-term investment?"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
            </div>

            <button
              onClick={analyzeStock}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 text-lg"
            >
              {loading ? 'Analyzing...' : 'Analyze Stock'}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Running multi-agent analysis...</p>
            <p className="text-gray-500 text-sm mt-2">This may take 10-30 seconds</p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6">
            {/* Recommendation Card */}
            {result.recommendation && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  🎯 Final Recommendation
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Action</p>
                    <p className={`text-2xl font-bold ${
                      result.recommendation.action === 'BUY' ? 'text-green-600' :
                      result.recommendation.action === 'SELL' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {result.recommendation.action}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Confidence</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {(result.recommendation.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Risk Level</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.recommendation.risk_level}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Time Horizon</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {result.recommendation.time_horizon.split('(')[0]}
                    </p>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Reasoning:</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {result.recommendation.reasoning}
                  </p>
                </div>

                {result.recommendation.key_factors.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Key Factors:</h3>
                    <ul className="space-y-1">
                      {result.recommendation.key_factors.map((factor, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-blue-600 mr-2">•</span>
                          <span className="text-gray-700">{factor}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.recommendation.entry_strategy && (
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Entry Strategy:</h3>
                    <p className="text-gray-700">{result.recommendation.entry_strategy}</p>
                  </div>
                )}

                {result.recommendation.watch_for && result.recommendation.watch_for.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Risks to Monitor:</h3>
                    <ul className="space-y-1">
                      {result.recommendation.watch_for.map((risk, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-red-600 mr-2">⚠</span>
                          <span className="text-gray-700">{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Financial Analysis */}
            {result.financial_analysis && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  📊 Financial Analysis
                </h2>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <p className="text-sm text-gray-600">Valuation</p>
                    <p className="text-xl font-bold text-gray-900">
                      {result.financial_analysis.valuation}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Trend</p>
                    <p className="text-xl font-bold text-gray-900">
                      {result.financial_analysis.trend}
                    </p>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Assessment:</h3>
                  <p className="text-gray-700">{result.financial_analysis.assessment}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold text-green-700 mb-2">Strengths</h3>
                    <ul className="space-y-1">
                      {result.financial_analysis.strengths.map((strength, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-green-600 mr-2">✓</span>
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-700 mb-2">Concerns</h3>
                    <ul className="space-y-1">
                      {result.financial_analysis.concerns.map((concern, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-red-600 mr-2">⚠</span>
                          <span className="text-gray-700">{concern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Sentiment Analysis */}
            {result.sentiment_analysis && (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  📰 Sentiment Analysis
                </h2>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Overall Mood</p>
                    <p className="text-xl font-bold text-gray-900">
                      {result.sentiment_analysis.overall_mood}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Sentiment Score</p>
                    <p className="text-xl font-bold text-blue-600">
                      {result.sentiment_analysis.sentiment_score.toFixed(2)}/1.0
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Articles Analyzed</p>
                    <p className="text-xl font-bold text-gray-900">
                      {result.sentiment_analysis.article_count}
                    </p>
                  </div>
                </div>

                {result.sentiment_analysis.key_themes.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Key Themes:</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.sentiment_analysis.key_themes.map((theme, i) => (
                        <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Errors */}
            {result.errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="font-semibold text-red-900 mb-2">Errors:</h3>
                <ul className="space-y-1">
                  {result.errors.map((err, i) => (
                    <li key={i} className="text-red-700 text-sm">{err}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}