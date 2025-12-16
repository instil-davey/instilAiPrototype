'use client';

import { useState } from 'react';
import { ConstituentModal } from '@/components/ConstituentModal';
import { Users, Sparkles } from 'lucide-react';

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedConstituentId, setSelectedConstituentId] = useState<number>(1);

  const handleOpenModal = (id: number) => {
    setSelectedConstituentId(id);
    setIsModalOpen(true);
  };

  const handleGenerateMessage = (constituentId: number) => {
    console.log('Generate message for constituent:', constituentId);
    // In production, this would open a message composition interface
    alert(`Opening message composer for constituent ${constituentId}`);
  };

  const mockConstituents = [
    {
      id: 1,
      name: 'Sarah Chen',
      type: 'Major Donor',
      totalGiven: 45000,
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 2,
      name: 'Michael Rodriguez',
      type: 'Donor',
      totalGiven: 8500,
      color: 'from-purple-500 to-purple-600',
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Constituent Briefing Modal
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Click on any constituent card below to view their full briefing with
            AI-generated insights, giving breakdown, engagement timeline, and suggested
            actions.
          </p>
        </div>

        {/* Feature Highlights */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
            <p className="text-sm text-gray-600">
              Get intelligent summaries and suggested actions based on constituent data
            </p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Complete Profile View</h3>
            <p className="text-sm text-gray-600">
              See giving history, engagement timeline, and segment classification
            </p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg
                className="w-5 h-5 text-purple-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Smooth Animations</h3>
            <p className="text-sm text-gray-600">
              iOS-inspired fade and scale animations for a premium experience
            </p>
          </div>
        </div>

        {/* Constituent Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {mockConstituents.map((constituent) => (
            <div
              key={constituent.id}
              className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer border border-gray-200 hover:border-blue-300"
              onClick={() => handleOpenModal(constituent.id)}
            >
              <div
                className={`h-32 bg-gradient-to-r ${constituent.color} p-6 flex items-center justify-between`}
              >
                <div className="text-white">
                  <h3 className="text-2xl font-bold mb-1">{constituent.name}</h3>
                  <p className="text-sm text-white/80">{constituent.type}</p>
                </div>
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                  <Users className="w-8 h-8 text-white" />
                </div>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Lifetime Giving</p>
                    <p className="text-3xl font-bold text-gray-900">
                      ${constituent.totalGiven.toLocaleString()}
                    </p>
                  </div>
                  <button
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors group-hover:shadow-lg"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenModal(constituent.id);
                    }}
                  >
                    View Briefing
                  </button>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
                    Active Donor
                  </span>
                  <span className="px-3 py-1 bg-green-50 text-green-700 text-xs font-medium rounded-full">
                    High Engagement
                  </span>
                  <span className="px-3 py-1 bg-purple-50 text-purple-700 text-xs font-medium rounded-full">
                    Segment: {constituent.type}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Technical Specs */}
        <div className="mt-12 bg-white rounded-xl p-8 shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Technical Specifications</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Components</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                    components/ConstituentModal.tsx
                  </code>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                    components/BriefingSection.tsx
                  </code>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">API Endpoint</h3>
              <div className="bg-gray-50 rounded-lg p-4 font-mono text-xs">
                <code className="text-blue-600">GET</code>{' '}
                <code className="text-gray-800">/api/constituents/:id/briefing</code>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>✓ Full-screen responsive modal</li>
                <li>✓ Framer Motion animations</li>
                <li>✓ AI-generated summaries</li>
                <li>✓ Giving & engagement analytics</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Tech Stack</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Next.js 14 + TypeScript</li>
                <li>• Tailwind CSS</li>
                <li>• Framer Motion</li>
                <li>• Lucide React Icons</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <ConstituentModal
        constituentId={selectedConstituentId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onGenerateMessage={handleGenerateMessage}
      />
    </main>
  );
}
