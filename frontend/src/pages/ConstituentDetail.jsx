import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  constituentsAPI,
  contributionsAPI,
  interactionsAPI,
  tasksAPI,
  voiceAPI,
} from '../services/api'

const prompts = [
  {
    key: 'interactionDetails',
    label: 'Interaction Details',
    question: 'Tell me about the interaction you had with this constituent.',
    callLine: (constituent) =>
      `Can you walk me through your most recent touchpoint with ${constituent?.first_name || 'this constituent'}?`,
  },
  {
    key: 'interactionOutcome',
    label: 'How it Went',
    question: 'How did the interaction go? How did the constituent respond?',
    callLine: (constituent) =>
      `How did ${constituent?.first_name || 'they'} respond and how did the conversation feel to you?`,
  },
  {
    key: 'nextSteps',
    label: 'Next Steps',
    question: 'Are there any follow-up tasks or commitments?',
    callLine: () => 'What next steps or follow-ups should I capture and assign?',
  },
]

export default function ConstituentDetail() {
  const { id } = useParams()
  const [constituent, setConstituent] = useState(null)
  const [summary, setSummary] = useState(null)
  const [contributions, setContributions] = useState([])
  const [interactions, setInteractions] = useState([])
  const [loading, setLoading] = useState(true)
  const [briefing, setBriefing] = useState(null)
  const [briefingError, setBriefingError] = useState('')
  const [briefingLoading, setBriefingLoading] = useState(false)
  const [isBriefingOpen, setBriefingOpen] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [segmentSuggestion, setSegmentSuggestion] = useState(null)
  const [segmentError, setSegmentError] = useState('')
  const [isVoiceModalOpen, setVoiceModalOpen] = useState(false)
  const [voiceResponses, setVoiceResponses] = useState({
    interactionDetails: '',
    interactionOutcome: '',
    nextSteps: '',
  })
  const [currentPromptIndex, setCurrentPromptIndex] = useState(-1)
  const [isRecording, setIsRecording] = useState(false)
  const [recognitionSupported, setRecognitionSupported] = useState(false)
  const recognitionRef = useRef(null)
  const [voiceError, setVoiceError] = useState('')
  const [conversationLog, setConversationLog] = useState([])
  const [callStage, setCallStage] = useState('idle')
  const [manualResponse, setManualResponse] = useState('')
  const [callSaving, setCallSaving] = useState(false)
  const [createdTasks, setCreatedTasks] = useState([])
  const audioRef = useRef(null)

  const appendConversationLog = (speaker, text) => {
    if (!text) return
    setConversationLog((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${prev.length}`,
        speaker,
        text,
      },
    ])
  }

  const stopVoicePlayback = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
  }

  const playVoiceLine = async (text, options = {}) => {
    const { surfaceCallError = true } = options
    if (!text) return
    stopVoicePlayback()
    try {
      const response = await voiceAPI.speak({ text })
      await new Promise((resolve, reject) => {
        const audio = new Audio(
          `data:${response.data.mime_type};base64,${response.data.audio_base64}`
        )
        audioRef.current = audio
        audio.onended = () => {
          audioRef.current = null
          resolve()
        }
        audio.onerror = (event) => {
          audioRef.current = null
          reject(event)
        }
        audio.play()
      })
    } catch (error) {
      console.error('Voice playback failed:', error)
      if (surfaceCallError) {
        setVoiceError('Unable to play AI audio. Continue typing responses while we retry.')
      }
      throw error
    }
  }

  const parseTasksFromText = (text) => {
    if (!text) return []
    return text
      .split(/\n|•|-|\u2022/g)
      .map((item) => item.replace(/^[0-9.)\-\s]+/, '').trim())
      .filter(Boolean)
  }

  const buildInteractionNotes = () => {
    const sections = []
    if (voiceResponses.interactionDetails) {
      sections.push(`Interaction summary: ${voiceResponses.interactionDetails}`)
    }
    if (voiceResponses.interactionOutcome) {
      sections.push(`How it went: ${voiceResponses.interactionOutcome}`)
    }
    if (voiceResponses.nextSteps) {
      sections.push(`Next steps mentioned: ${voiceResponses.nextSteps}`)
    }
    return sections.join('\n\n')
  }

  const resetVoiceConversation = () => {
    setVoiceResponses({
      interactionDetails: '',
      interactionOutcome: '',
      nextSteps: '',
    })
    setConversationLog([])
    setVoiceError('')
    setManualResponse('')
    setCallStage('idle')
    setCurrentPromptIndex(-1)
    setCreatedTasks([])
    setCallSaving(false)
  }

  const startRecordingForPrompt = () => {
    if (!recognitionSupported || !recognitionRef.current) return
    const recognition = recognitionRef.current
    const tryStart = () => {
      try {
        recognition.start()
        setIsRecording(true)
      } catch (error) {
        console.error('Unable to start recording:', error)
        setIsRecording(false)
      }
    }

    // If the recognition engine is already running, stop it first to avoid
    // InvalidStateError before starting a new capture session.
    if (isRecording) {
      try {
        recognition.stop()
      } catch {
        // ignore stop failure and attempt restart
      }
      // give the browser a moment to settle before restarting
      setTimeout(tryStart, 150)
    } else {
      tryStart()
    }
  }

  const askPrompt = async (index) => {
    if (!constituent) return
    if (index >= prompts.length) {
      await finalizeVoiceCall()
      return
    }
    setCurrentPromptIndex(index)
    setCallStage('prompting')
    const prompt = prompts[index]
    const spokenLine =
      typeof prompt.callLine === 'function'
        ? prompt.callLine(constituent)
        : prompt.callLine
    appendConversationLog('AI', spokenLine)
    try {
      await playVoiceLine(spokenLine)
    } catch {
      // Already surfaced via voiceError state; continue silently
    }
    setCallStage('listening')
    setManualResponse('')
    startRecordingForPrompt()
  }

  const finalizeVoiceCall = async () => {
    if (!voiceResponses.interactionDetails) {
      setVoiceError('I need the interaction details before I can log this call.')
      setCurrentPromptIndex(0)
      setCallStage('prompting')
      return
    }
    setCallStage('saving')
    const closingLine = 'Thanks for sharing. I\'m logging this interaction and follow-ups for you.'
    appendConversationLog('AI', closingLine)
    try {
      await playVoiceLine(closingLine)
    } catch {
      // continue even if voice playback fails
    }
    await saveInteractionAndTasks(true)
  }

  const handlePromptResponse = async (text) => {
    if (!text?.trim()) {
      setVoiceError('Please provide a response before continuing.')
      return
    }
    if (currentPromptIndex === -1) {
      setVoiceError('Start the AI call to capture your update.')
      return
    }
    const cleaned = text.trim()
    const prompt = prompts[currentPromptIndex]
    setVoiceResponses((prev) => ({ ...prev, [prompt.key]: cleaned }))
    appendConversationLog('You', cleaned)
    setVoiceError('')
    setManualResponse('')
    setIsRecording(false)

    const nextIndex = currentPromptIndex + 1
    if (nextIndex < prompts.length) {
      await askPrompt(nextIndex)
    } else {
      await finalizeVoiceCall()
    }
  }

  const saveInteractionAndTasks = async (autoTriggered = false) => {
    if (!voiceResponses.interactionDetails) {
      setVoiceError('Tell me about the interaction so I can log it.')
      return
    }

    setCallSaving(true)
    try {
      const notes = buildInteractionNotes()
      const payload = {
        constituent_id: Number(id),
        interaction_type: 'call',
        interaction_date: new Date().toISOString(),
        subject: `AI voice log for ${constituent?.first_name || 'constituent'}`,
        notes,
        outcome: voiceResponses.nextSteps ? 'Follow-up needed' : 'Completed',
      }
      const response = await interactionsAPI.create(payload)
      setInteractions((prev) => [response.data, ...prev])

      const taskDescriptions = parseTasksFromText(voiceResponses.nextSteps)
      const created = []
      for (const description of taskDescriptions) {
        try {
          const taskResp = await tasksAPI.create({
            constituent_id: Number(id),
            description,
          })
          created.push(taskResp.data)
        } catch (taskError) {
          console.error('Task creation failed:', taskError)
        }
      }
      setCreatedTasks(created)
      setCallStage('complete')
      if (autoTriggered) {
        const confirmation =
          created.length > 0
            ? `All set. I added ${created.length} follow-up task${
                created.length === 1 ? '' : 's'
              } and logged the interaction.`
            : 'All set. I logged the interaction and no extra tasks were needed.'
        appendConversationLog('AI', confirmation)
        try {
          await playVoiceLine(confirmation)
        } catch {
          // ignore playback failure for confirmation line
        }
      }
    } catch (error) {
      console.error('Error saving interaction:', error)
      setVoiceError('Unable to automatically save the interaction. Update the notes and try again.')
      setCallStage('idle')
    } finally {
      setCallSaving(false)
    }
  }

  const startVoiceCall = async () => {
    if (!constituent || callSaving) return
    setVoiceError('')
    setCreatedTasks([])
    setCallStage('intro')
    const contactName = constituent?.first_name || 'your constituent'
    const greeting = `Hi, I'm your Instil AI call scribe for ${contactName}. Let's capture what happened.`
    appendConversationLog('AI', greeting)
    try {
      await playVoiceLine(greeting)
    } catch {
      // continue even if audio fails
    }
    await askPrompt(0)
  }

  const handleRestartCall = () => {
    resetVoiceConversation()
    startVoiceCall()
  }

  useEffect(() => {
    Promise.all([
      constituentsAPI.get(id),
      constituentsAPI.getSummary(id),
      contributionsAPI.list({ constituent_id: id }),
      interactionsAPI.list({ constituent_id: id, limit: 10 }),
    ])
      .then(([constRes, summaryRes, contribRes, intRes]) => {
        setConstituent(constRes.data)
        setSummary(summaryRes.data)
        setContributions(contribRes.data)
        setInteractions(intRes.data)
      })
      .catch((error) => console.error('Error loading constituent:', error))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    setSegmentSuggestion(null)
    setSegmentError('')
    constituentsAPI
      .getSegmentSuggestion(id)
      .then((response) => setSegmentSuggestion(response.data))
      .catch((error) => {
        if (error?.response?.status !== 404) {
          setSegmentError('Unable to load AI segment insight right now.')
          console.error('Segment suggestion error:', error)
        }
      })
  }, [id])

  useEffect(() => {
    return () => {
      stopVoicePlayback()
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  useEffect(() => {
    if (!isVoiceModalOpen) {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
        recognitionRef.current = null
      }
      return
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setRecognitionSupported(false)
      return
    }

    setRecognitionSupported(true)
    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(' ')
      handlePromptResponse(transcript)
    }
    recognition.onerror = (event) => {
      setVoiceError(event.error || 'Voice capture error')
      setIsRecording(false)
    }
    recognition.onend = () => {
      setIsRecording(false)
    }

    recognitionRef.current = recognition
  }, [isVoiceModalOpen, currentPromptIndex])

  useEffect(() => {
    if (
      isVoiceModalOpen &&
      recognitionSupported &&
      recognitionRef.current &&
      callStage === 'listening' &&
      !isRecording
    ) {
      startRecordingForPrompt()
    }
  }, [isVoiceModalOpen, recognitionSupported, callStage, isRecording])

  const handleGenerateBriefing = async () => {
    setBriefingError('')
    setBriefingLoading(true)
    try {
      const response = await constituentsAPI.getBriefing(id)
      setBriefing(response.data)
      setBriefingOpen(true)
    } catch (error) {
      console.error('Error generating briefing:', error)
      setBriefingError(
        error?.response?.data?.detail?.error ||
          error?.response?.data?.detail ||
          'Unable to generate briefing right now.'
      )
    } finally {
      setBriefingLoading(false)
    }
  }

  const closeBriefing = () => {
    setBriefingOpen(false)
    stopVoicePlayback()
    setIsSpeaking(false)
  }

  const handleSpeakBriefing = async () => {
    if (!briefing) return
    const narration = `Summary: ${briefing.summary}. Giving Summary: ${briefing.giving_summary}. Engagement Pattern: ${briefing.engagement_pattern}. Why they matter: ${briefing.why_they_matter}. Suggested action: ${briefing.suggested_action}.`
    setBriefingError('')
    setIsSpeaking(true)
    try {
      await playVoiceLine(narration, { surfaceCallError: false })
    } catch (error) {
      console.error('Unable to play briefing audio:', error)
      setBriefingError('Unable to read the briefing aloud. Please try again.')
    } finally {
      setIsSpeaking(false)
    }
  }

  const openVoiceModal = () => {
    setVoiceModalOpen(true)
    handleRestartCall()
  }

  const closeVoiceModal = () => {
    setVoiceModalOpen(false)
    setIsRecording(false)
    stopVoicePlayback()
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    resetVoiceConversation()
  }

  const handleVoiceInputChange = (key, value) => {
    setVoiceResponses((prev) => ({ ...prev, [key]: value }))
  }

  const startRecording = () => {
    if (currentPromptIndex === -1) {
      setVoiceError('Start the AI call before recording your response.')
      return
    }
    if (!recognitionSupported || !recognitionRef.current) {
      setVoiceError('Voice recognition is not supported in this browser.')
      return
    }
    setVoiceError('')
    startRecordingForPrompt()
  }

  const handleManualSubmit = () => {
    handlePromptResponse(manualResponse)
  }

  if (loading) return <div className="loading">Loading constituent...</div>
  if (!constituent) return <div className="error">Constituent not found</div>

  return (
    <div className="constituent-detail">
      <div className="page-header">
        <div>
          <Link to="/constituents" className="back-link">
            ← Back to Constituents
          </Link>
          <h1>
            {constituent.first_name} {constituent.last_name}
          </h1>
        </div>
        <div className="action-buttons">
          <button className="btn-secondary" onClick={openVoiceModal}>
            Log Interaction (Voice)
          </button>
          <button
            className="btn-primary"
            onClick={handleGenerateBriefing}
            disabled={briefingLoading}
          >
            {briefingLoading ? 'Generating briefing...' : 'Generate AI Briefing'}
          </button>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h2>Contact Information</h2>
          <div className="info-row">
            <span className="label">Email:</span>
            <span>{constituent.email}</span>
          </div>
          <div className="info-row">
            <span className="label">Phone:</span>
            <span>{constituent.phone}</span>
          </div>
          <div className="info-row">
            <span className="label">Address:</span>
            <span>
              {constituent.address}
              <br />
              {constituent.city}, {constituent.state} {constituent.zip_code}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Type:</span>
            <span className={`badge badge-${constituent.constituent_type}`}>
              {constituent.constituent_type}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Status:</span>
            <span className={`status-${constituent.status}`}>
              {constituent.status}
            </span>
          </div>
        </div>

        <div className="detail-card">
          <h2>Giving Summary</h2>
          <div className="info-row">
            <span className="label">Total Contributions:</span>
            <span className="highlight">
              ${Number(summary?.total_contributions || 0).toLocaleString()}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Number of Gifts:</span>
            <span>{summary?.contribution_count || 0}</span>
          </div>
          <div className="info-row">
            <span className="label">Average Gift:</span>
            <span>
              ${Number(summary?.average_contribution || 0).toLocaleString()}
            </span>
          </div>
          <div className="info-row">
            <span className="label">Last Gift Date:</span>
            <span>
              {summary?.last_contribution_date
                ? new Date(summary.last_contribution_date).toLocaleDateString()
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {constituent.notes && (
        <div className="detail-card">
          <h2>Notes</h2>
          <p>{constituent.notes}</p>
        </div>
      )}

      {(segmentSuggestion || segmentError) && (
        <div className="detail-card">
          <h2>AI Segment Insight</h2>
          {segmentError && <p className="error-message">{segmentError}</p>}
          {segmentSuggestion && (
            <>
              <div className="info-row">
                <span className="label">Segment:</span>
                <span className="highlight">{segmentSuggestion.segment_name}</span>
              </div>
              <div className="info-row">
                <span className="label">Why this segment:</span>
                <span>{segmentSuggestion.segment_reason}</span>
              </div>
              <div className="info-row">
                <span className="label">Constituent insight:</span>
                <span>{segmentSuggestion.constituent_reason}</span>
              </div>
              {segmentSuggestion.suggested_action && (
                <div className="info-row">
                  <span className="label">Suggested action:</span>
                  <span>{segmentSuggestion.suggested_action}</span>
                </div>
              )}
            </>
          )}
        </div>
      )}

      <div className="detail-card">
        <h2>Recent Contributions</h2>
        {contributions.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Type</th>
                <th>Campaign</th>
              </tr>
            </thead>
            <tbody>
              {contributions.map((contribution) => (
                <tr key={contribution.contribution_id}>
                  <td>
                    {new Date(contribution.contribution_date).toLocaleDateString()}
                  </td>
                  <td className="highlight">
                    ${Number(contribution.amount).toLocaleString()}
                  </td>
                  <td>{contribution.contribution_type}</td>
                  <td>{contribution.campaign || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="no-data">No contributions recorded</p>
        )}
      </div>

      <div className="detail-card">
        <h2>Recent Interactions</h2>
        {interactions.length > 0 ? (
          <div className="activity-list">
            {interactions.map((interaction) => (
              <div key={interaction.interaction_id} className="activity-item">
                <div className="activity-title">{interaction.subject}</div>
                <div className="activity-meta">
                  {interaction.interaction_type} •{' '}
                  {new Date(interaction.interaction_date).toLocaleDateString()}
                </div>
                {interaction.notes && (
                  <div className="activity-notes">{interaction.notes}</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">No interactions recorded</p>
        )}
      </div>

      {briefingError && (
        <div className="alert alert-error">
          <strong>Briefing Error:</strong> {briefingError}
        </div>
      )}

      {isBriefingOpen && briefing && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-content">
            <div className="modal-header">
              <div>
                <h2>AI Briefing</h2>
                <p className="modal-subtitle">
                  Generated for {constituent.first_name} {constituent.last_name} on{' '}
                  {new Date(briefing.metadata.generated_at).toLocaleString()}
                </p>
              </div>
              <div className="modal-actions">
                <button className="btn-secondary" onClick={handleSpeakBriefing} disabled={isSpeaking}>
                  {isSpeaking ? 'Reading…' : 'Read Briefing'}
                </button>
                <button className="btn-tertiary" onClick={closeBriefing}>
                  Close
                </button>
              </div>
            </div>

            <div className="briefing-section">
              <h3>Executive Summary</h3>
              <p>{briefing.summary}</p>
            </div>
            <div className="briefing-section">
              <h3>Giving Insights</h3>
              <p>{briefing.giving_summary}</p>
            </div>
            <div className="briefing-section">
              <h3>Engagement Pattern</h3>
              <p>{briefing.engagement_pattern}</p>
            </div>
            <div className="briefing-section">
              <h3>Why They Matter</h3>
              <p>{briefing.why_they_matter}</p>
            </div>
            <div className="briefing-section">
              <h3>Segment Rationale</h3>
              <p>{briefing.segment_reason}</p>
            </div>
            <div className="briefing-section">
              <h3>Suggested Action</h3>
              <p>{briefing.suggested_action}</p>
            </div>

            <div className="metadata-grid">
              {Object.entries(briefing.metadata.data_points || {}).map(([key, value]) => (
                <div key={key} className="metadata-item">
                  <span className="metadata-label">{key}</span>
                  <span className="metadata-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {isVoiceModalOpen && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-content voice-modal-content">
            <div className="modal-header">
              <div>
                <h2>Voice Interaction Logger</h2>
                <p className="modal-subtitle">
                  The AI agent will lead a call-style conversation, capture your notes, and create tasks automatically.
                </p>
              </div>
              <div className="modal-actions">
                <button className="btn-tertiary" onClick={closeVoiceModal}>
                  Close
                </button>
              </div>
            </div>
            {voiceError && <p className="error-message">{voiceError}</p>}

            <div className="call-assistant-panel">
              <div className="call-status-row">
                <span className={`call-status-badge call-stage-${callStage}`}>
                  {callStage === 'saving'
                    ? 'Logging interaction...'
                    : callStage === 'complete'
                      ? 'Call complete'
                      : callStage === 'listening'
                        ? 'Listening for your answer'
                        : callStage === 'prompting'
                          ? 'Asking next question'
                          : 'Connecting to AI agent'}
                </span>
                <button
                  className="btn-secondary"
                  onClick={handleRestartCall}
                  disabled={callSaving}
                >
                  Restart Call
                </button>
              </div>

              <div className="conversation-log" aria-live="polite">
                {conversationLog.length === 0 ? (
                  <p className="conversation-placeholder">Connecting you to the AI scribe…</p>
                ) : (
                  conversationLog.map((entry) => (
                    <div key={entry.id} className={`conversation-entry conversation-${entry.speaker === 'AI' ? 'ai' : 'user'}`}>
                      <span className="conversation-speaker">{entry.speaker}</span>
                      <p>{entry.text}</p>
                    </div>
                  ))
                )}
              </div>

              <div className="call-input-bar">
                <textarea
                  rows={2}
                  placeholder={
                    currentPromptIndex >= 0
                      ? prompts[currentPromptIndex].question
                      : 'Waiting for the AI agent…'
                  }
                  value={manualResponse}
                  onChange={(e) => setManualResponse(e.target.value)}
                  disabled={callStage === 'saving'}
                />
                <div className="call-input-actions">
                  <button
                    className="btn-secondary"
                    onClick={startRecording}
                    disabled={
                      !recognitionSupported ||
                      isRecording ||
                      callStage === 'saving' ||
                      callStage === 'complete'
                    }
                  >
                    {isRecording ? 'Listening…' : 'Record Answer'}
                  </button>
                  <button
                    className="btn-primary"
                    onClick={handleManualSubmit}
                    disabled={!manualResponse.trim() || callStage === 'saving'}
                  >
                    Send Response
                  </button>
                </div>
                {!recognitionSupported && (
                  <p className="modal-subtitle">
                    Voice capture is not available in this browser, but you can type your response and press “Send Response”.
                  </p>
                )}
              </div>
            </div>

            <div className="voice-prompts">
              <h3>Captured Notes</h3>
              {prompts.map((prompt, index) => (
                <div
                  key={prompt.key}
                  className={`voice-prompt ${index === currentPromptIndex ? 'active' : ''}`}
                >
                  <div className="voice-prompt-header">
                    <strong>{prompt.label}</strong>
                    {index === currentPromptIndex && recognitionSupported && (
                      <button
                        className="btn-secondary"
                        onClick={startRecording}
                        disabled={isRecording || callStage === 'saving'}
                      >
                        {isRecording ? 'Listening…' : 'Record'}
                      </button>
                    )}
                  </div>
                  <p className="voice-question">{prompt.question}</p>
                  <textarea
                    rows={3}
                    value={voiceResponses[prompt.key]}
                    onChange={(e) => handleVoiceInputChange(prompt.key, e.target.value)}
                    placeholder="Your response..."
                  />
                </div>
              ))}
            </div>

            {callStage === 'complete' && (
              <div className="call-summary-card">
                <p>
                  Interaction logged for {constituent?.first_name || 'this constituent'}. {createdTasks.length > 0
                    ? `Created ${createdTasks.length} follow-up task${createdTasks.length === 1 ? '' : 's'}.`
                    : 'No additional tasks were created.'}
                </p>
                {createdTasks.length > 0 && (
                  <ul>
                    {createdTasks.map((task) => (
                      <li key={task.task_id}>{task.description}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <div className="modal-actions" style={{ justifyContent: 'flex-end' }}>
              <button
                className="btn-primary"
                onClick={() => saveInteractionAndTasks(false)}
                disabled={!voiceResponses.interactionDetails || callSaving}
              >
                {callSaving ? 'Saving…' : callStage === 'complete' ? 'Save Again' : 'Log Interaction Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
