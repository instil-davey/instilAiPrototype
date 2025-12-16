'use client';

import { useState } from 'react';
import TextareaAutosize from 'react-textarea-autosize';

interface MessageGeneratorProps {
  constituentId: string;
  initialTone?: 'formal' | 'friendly' | 'professional';
  onMessageGenerated?: (message: string) => void;
}

export default function MessageGenerator({
  constituentId,
  initialTone = 'professional',
  onMessageGenerated,
}: MessageGeneratorProps) {
  const [message, setMessage] = useState<string>('');
  const [tone, setTone] = useState<'formal' | 'friendly' | 'professional'>(initialTone);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateMessage = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`/api/constituents/${constituentId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tone,
          occasion: 'general outreach',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate message');
      }

      const data = await response.json();
      setMessage(data.message);

      if (onMessageGenerated) {
        onMessageGenerated(data.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error generating message:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      setError('Failed to copy to clipboard');
    }
  };

  const regenerateVariation = async () => {
    // Generate with the same settings to get a variation
    await generateMessage();
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
      <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">
            Donor Message Generator
          </h2>
          <div className="flex items-center gap-2">
            <label htmlFor="tone-select" className="text-sm font-medium text-gray-700">
              Tone:
            </label>
            <select
              id="tone-select"
              value={tone}
              onChange={(e) => setTone(e.target.value as typeof tone)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="professional">Professional</option>
              <option value="friendly">Friendly</option>
              <option value="formal">Formal</option>
            </select>
          </div>
        </div>

        {/* Generate Button */}
        <div>
          <button
            onClick={generateMessage}
            disabled={isGenerating}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Generating...
              </span>
            ) : (
              'Generate Message'
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Message Textarea */}
        {message && (
          <div className="space-y-3">
            <label htmlFor="message-textarea" className="block text-sm font-medium text-gray-700">
              Generated Message (editable):
            </label>
            <TextareaAutosize
              id="message-textarea"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              minRows={6}
              className="w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-sans leading-relaxed"
              placeholder="Your generated message will appear here..."
            />

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={copyToClipboard}
                disabled={!message}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isCopied ? (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Copied!
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                      <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                    </svg>
                    Copy Message
                  </>
                )}
              </button>

              <button
                onClick={regenerateVariation}
                disabled={isGenerating}
                className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                    clipRule="evenodd"
                  />
                </svg>
                Regenerate
              </button>
            </div>
          </div>
        )}

        {/* Helper Text */}
        {!message && !isGenerating && (
          <div className="text-center py-8 text-gray-500">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
            <p className="text-lg font-medium">Generate a personalized message</p>
            <p className="text-sm mt-2">
              Select a tone and click the button above to create a message for this donor
            </p>
          </div>
        )}
      </div>

      {/* Info Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">Pro Tips</p>
            <ul className="mt-1 text-sm text-blue-800 list-disc list-inside space-y-1">
              <li>Edit the generated message directly in the textarea</li>
              <li>Try different tones to match your relationship with the donor</li>
              <li>Click "Regenerate" for alternative phrasings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
