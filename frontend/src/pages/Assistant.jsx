import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { miniAssistantAPI } from '../api';
import { API_CONFIG } from '../api/config';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User as UserIcon, PlugZap, Shield, Copy, ThumbsUp, ThumbsDown, StopCircle, RotateCcw, ChevronDown, ChevronUp, Plus, Menu, Trash } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

function AutoTextarea({ value, onChange, className, ...props }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = 'auto';
    ref.current.style.height = Math.min(ref.current.scrollHeight, 160) + 'px';
  }, [value]);
  return <textarea ref={ref} value={value} onChange={onChange} className={className} {...props} rows={1} />;
}

const Assistant = () => {
  const qc = useQueryClient();

  // UI state
  const [message, setMessage] = useState('');
  const [typing, setTyping] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [useContext, setUseContext] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showTools, setShowTools] = useState(true);
  const [typingDots, setTypingDots] = useState('.');
  const [atBottom, setAtBottom] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeSessionIndex, setActiveSessionIndex] = useState(null);

  const abortRef = useRef(null);
  const endRef = useRef(null);
  const chatScrollRef = useRef(null);

  // Data
  const { data: assistant } = useQuery({
    queryKey: ['miniAssistant'],
    queryFn: miniAssistantAPI.getMiniAssistant,
    retry: 0,
  });

  const { data: interactions = [] } = useQuery({
    queryKey: ['miniAssistantInteractions'],
    queryFn: miniAssistantAPI.getInteractions,
    enabled: !!assistant,
    staleTime: 30_000,
  });

  const { data: tools = [] } = useQuery({
    queryKey: ['assistantTools'],
    queryFn: miniAssistantAPI.listTools,
    staleTime: 60_000,
  });

  const sortedInteractions = useMemo(() => {
    if (!interactions?.length) return [];
    return [...interactions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  }, [interactions]);

  const createInteraction = useMutation({
    mutationFn: miniAssistantAPI.createInteraction,
    onSuccess: () => qc.invalidateQueries(['miniAssistantInteractions']),
  });

  const execTool = useMutation({
    mutationFn: ({ tool, params }) => miniAssistantAPI.executeTool(tool, params),
    onSuccess: () => qc.invalidateQueries(['miniAssistantInteractions']),
  });

  const [pendingTool, setPendingTool] = useState(null);
  const [toolParams, setToolParams] = useState({});

  // Auto-scroll to bottom on changes
  useEffect(() => {
    if (endRef.current) endRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [sortedInteractions, typing, streamText]);

  // Typing dots animation
  useEffect(() => {
    if (!typing && !isStreaming) return;
    const iv = setInterval(() => {
      setTypingDots((d) => (d.length >= 3 ? '.' : d + '.'));
    }, 400);
    return () => clearInterval(iv);
  }, [typing, isStreaming]);

  // Scroll position tracking
  useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;
    const onScroll = () => {
      const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
      setAtBottom(nearBottom);
    };
    el.addEventListener('scroll', onScroll);
    onScroll();
    return () => el.removeEventListener('scroll', onScroll);
  }, [chatScrollRef, sortedInteractions, streamText]);

  // Sessions
  const sessions = useMemo(() => {
    const items = sortedInteractions;
    if (!items.length) return [];
    const groups = [];
    let current = { title: 'New chat', startIdx: 0, endIdx: items.length, created_at: items[0]?.created_at };
    items.forEach((it, idx) => {
      const meta = it.metadata || {};
      if (it.interaction_type === 'system' && meta.new_session) {
        current.endIdx = idx;
        if (idx > current.startIdx) groups.push(current);
        current = { title: meta.title || 'New chat', startIdx: idx + 1, endIdx: items.length, created_at: it.created_at };
      }
    });
    if (items.length >= current.startIdx) groups.push(current);
    return groups.map((g) => {
      const firstUser = items.slice(g.startIdx, g.endIdx).find((x) => x.interaction_type.includes('user'));
      const title = firstUser?.content?.slice(0, 40) || g.title || 'New chat';
      return { ...g, title };
    });
  }, [sortedInteractions]);

  const displayedMessages = useMemo(() => {
    const items = sortedInteractions;
    if (!sessions.length) return items;
    const idx = activeSessionIndex == null ? sessions.length - 1 : activeSessionIndex;
    const safeIdx = Math.min(Math.max(idx, 0), sessions.length - 1);
    const s = sessions[safeIdx];
    if (!s) return items; // fallback guard
    return items.slice(s.startIdx, s.endIdx);
  }, [sortedInteractions, sessions, activeSessionIndex]);

  useEffect(() => {
    if (sessions.length && activeSessionIndex == null) setActiveSessionIndex(sessions.length - 1);
  }, [sessions, activeSessionIndex]);

  // Handlers
  const onSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    // Add user message first
    await createInteraction.mutateAsync({ content: message, interaction_type: 'user_message' });
  const prompt = message;
    setMessage('');
    setTyping(true);
    setStreamText('');
    setIsStreaming(true);
    try {
      const base = API_CONFIG.FULL_BASE_URL;
      const token = localStorage.getItem('access_token');
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      const res = await fetch(`${base}/mini-assistant/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ prompt, include_context: useContext, context_type: 'general', route: window.location.pathname }),
        signal: ctrl.signal,
      });
      if (!res.ok || !res.body) throw new Error('Failed to stream response');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let acc = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        setStreamText(acc);
        if (typing) setTyping(false);
      }
      // Persist assistant message
      if (acc) await miniAssistantAPI.createInteraction({ interaction_type: 'assistant_message', content: acc });
      qc.invalidateQueries(['miniAssistantInteractions']);
    } catch (err) {
      console.error('Assistant stream error', err);
      if (err?.name === 'AbortError') {
        toast.success('Generation stopped');
        if (streamText) {
          await miniAssistantAPI.createInteraction({ interaction_type: 'assistant_message', content: streamText });
          qc.invalidateQueries(['miniAssistantInteractions']);
        }
      } else {
        toast.error('Failed to get response');
      }
    } finally {
      setTyping(false);
      setStreamText('');
      setIsStreaming(false);
      abortRef.current = null;
    }
  };

  const stopStreaming = () => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
      setIsStreaming(false);
      setTyping(false);
    }
  };

  const regenerateLast = async () => {
    const lastUser = [...sortedInteractions].reverse().find((it) => it.interaction_type.includes('user'));
    if (!lastUser) return toast('No message to regenerate');
    setMessage(lastUser.content);
    setTimeout(() => {
      const fakeEvent = { preventDefault: () => {} };
      onSubmit(fakeEvent);
    }, 50);
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard');
    } catch (_) {
      toast.error('Copy failed');
    }
  };

  const deleteSession = async (idx) => {
    try {
      if (!sessions.length) return;
      const items = sortedInteractions;
      const s = sessions[Math.min(Math.max(idx, 0), sessions.length - 1)];
      if (!s) return;
      const slice = items.slice(s.startIdx, s.endIdx);
      const ids = slice.map((x) => x.id).filter(Boolean);
      if (!ids.length) {
        toast('Nothing to delete in this chat');
        return;
      }
      const ok = window.confirm('Delete this chat? This will remove all messages in this conversation.');
      if (!ok) return;
      await miniAssistantAPI.bulkDeleteInteractions(ids);
      await qc.invalidateQueries(['miniAssistantInteractions']);
      // Move selection to previous session if possible
      const nextIdx = sessions.length > 1 ? Math.min(idx, sessions.length - 2) : null;
      setActiveSessionIndex(nextIdx);
      toast.success('Chat deleted');
    } catch (e) {
      console.error('Delete chat failed', e);
      toast.error('Failed to delete chat');
    }
  };

  const Header = () => (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 text-white flex items-center justify-center">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">{assistant?.name || 'Assistant'}</h1>
          <p className="text-sm text-gray-600 dark:text-gray-300">{assistant?.personality || 'Helpful and friendly'} • Model: smart • Context: {useContext ? 'On' : 'Off'}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button type="button" className="lg:hidden inline-flex items-center gap-2 px-2 py-1 rounded-md border border-gray-300 dark:border-gray-700" onClick={() => setSidebarOpen((s) => !s)}>
          <Menu className="w-4 h-4" />
        </button>
        <label className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
          <PlugZap className="w-4 h-4" />
          <input type="checkbox" checked={useContext} onChange={(e) => setUseContext(e.target.checked)} />
          Use context
        </label>
      </div>
    </div>
  );

  return (
    <div className="min-h-[70vh] mx-auto max-w-6xl">
      <Header />
      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-4">
        {/* Sidebar */}
        <div className={`border rounded-lg bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 overflow-hidden ${sidebarOpen ? 'block' : 'hidden'} lg:block`}>
          <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <div className="font-semibold text-gray-900 dark:text-gray-100">Chats</div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="inline-flex items-center gap-2 px-2 py-1 rounded-md border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800"
                onClick={async () => {
                  const ok = window.confirm('Delete all chats? This will remove all your conversations.');
                  if (!ok) return;
                  try {
                    await miniAssistantAPI.deleteAllInteractions();
                    await qc.invalidateQueries(['miniAssistantInteractions']);
                    setActiveSessionIndex(null);
                    toast.success('All chats deleted');
                  } catch (e) {
                    console.error(e);
                    toast.error('Failed to delete all chats');
                  }
                }}
                title="Delete all chats"
              >
                <Trash className="w-4 h-4" />
              </button>
              <button
              type="button"
              className="inline-flex items-center gap-2 px-2 py-1 rounded-md bg-blue-600 text-white hover:bg-blue-700"
              onClick={async () => {
                await miniAssistantAPI.createInteraction({ interaction_type: 'system', content: 'New chat', metadata: { new_session: true, title: 'New chat' } });
                qc.invalidateQueries(['miniAssistantInteractions']);
                setActiveSessionIndex(null); // let effect select latest safely
                setSidebarOpen(false);
              }}
            >
              <Plus className="w-4 h-4" /> New chat
              </button>
            </div>
          </div>
          <div className="max-h-[60vh] overflow-y-auto divide-y divide-gray-200 dark:divide-gray-800">
            {sessions.map((s, i) => (
              <div
                key={`${s.created_at}-${i}`}
                className={`flex items-center gap-2 px-2 py-2 hover:bg-gray-50 dark:hover:bg-gray-800 ${i === activeSessionIndex ? 'bg-gray-100 dark:bg-gray-800 font-semibold' : ''}`}
                title={new Date(s.created_at).toLocaleString()}
              >
                <button
                  type="button"
                  className="flex-1 text-left px-1 text-sm"
                  onClick={() => { setActiveSessionIndex(i); setSidebarOpen(false); }}
                >
                  <div className="truncate text-gray-800 dark:text-gray-200">{s.title}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{new Date(s.created_at).toLocaleDateString()}</div>
                </button>
                <button
                  type="button"
                  onClick={() => deleteSession(i)}
                  className="p-1 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30"
                  aria-label="Delete chat"
                  title="Delete chat"
                >
                  <Trash className="w-4 h-4" />
                </button>
              </div>
            ))}
            {!sessions.length && <div className="p-3 text-sm text-gray-500 dark:text-gray-400">No chats yet. Start a new conversation.</div>}
          </div>
        </div>

        {/* Main */}
        <div>
          {/* Tools */}
          <div className="mb-3">
            <button
              type="button"
              className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
              onClick={() => setShowTools((s) => !s)}
            >
              {showTools ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />} Tools
            </button>
            {showTools && (
              <div className="mt-2 flex flex-wrap gap-2">
                {tools.map((t) => (
                  <button
                    type="button"
                    key={t.name}
                    className="px-3 py-1.5 rounded-md border text-sm bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 hover:bg-gray-50"
                    onClick={() => { setPendingTool(t); setToolParams({}); }}
                  >
                    {t.title}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Chat */}
          <div className="border rounded-lg bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 overflow-hidden">
            <div ref={chatScrollRef} className="h-[60vh] p-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
              <div className="mx-auto max-w-2xl mb-4 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
                <Shield className="w-3 h-3" /> The assistant may use your saved goals, skills, habits, mood and finance context when enabled.
              </div>

              {displayedMessages.map((it) => {
                const isUser = it.interaction_type.includes('user');
                return (
                  <motion.div
                    key={it.id}
                    className={`mb-3 flex ${isUser ? 'justify-end' : 'justify-start'}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}>
                        {isUser ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>
                      <div className={`group rounded-lg px-3 py-2 ${isUser ? 'bg-blue-600 text-white' : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100'}`}>
                        <ReactMarkdown className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : 'dark:prose-invert'}`}>
                          {it.content || ''}
                        </ReactMarkdown>
                        {!isUser && (
                          <div className="mt-2 hidden group-hover:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                            <button type="button" className="hover:text-gray-700 dark:hover:text-gray-200" onClick={() => handleCopy(it.content)}><Copy className="w-3.5 h-3.5" /></button>
                            <button type="button" className="hover:text-gray-700 dark:hover:text-gray-200"><ThumbsUp className="w-3.5 h-3.5" /></button>
                            <button type="button" className="hover:text-gray-700 dark:hover:text-gray-200"><ThumbsDown className="w-3.5 h-3.5" /></button>
                            <span className="ml-auto">{new Date(it.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}

              {(typing || isStreaming) && (
                <div className="mb-3 flex justify-start">
                  <div className="flex gap-3 max-w-[85%]">
                    <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="rounded-lg px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                      <div className="text-sm">Thinking{typingDots}</div>
                    </div>
                  </div>
                </div>
              )}

              {streamText && (
                <div className="mb-3 flex justify-start">
                  <div className="flex gap-3 max-w-[85%]">
                    <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="rounded-lg px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100">
                      <ReactMarkdown className="prose prose-sm max-w-none dark:prose-invert">{streamText}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}

              <div ref={endRef} />

              {!atBottom && (
                <div className="sticky bottom-4 flex justify-center">
                  <button
                    type="button"
                    className="px-3 py-1.5 rounded-full bg-gray-800 text-white text-xs shadow hover:bg-gray-700"
                    onClick={() => { if (chatScrollRef.current) chatScrollRef.current.scrollTo({ top: chatScrollRef.current.scrollHeight, behavior: 'smooth' }); }}
                  >
                    Jump to latest
                  </button>
                </div>
              )}
            </div>

            {/* Composer */}
            <div className="border-t border-gray-200 dark:border-gray-700 p-3">
              <div className="flex items-end gap-2">
                <AutoTextarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      onSubmit(e);
                    }
                  }}
                  placeholder="Message Assistant…"
                  className="flex-1 px-3 py-2 rounded-md bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 resize-none max-h-40"
                />
                {isStreaming ? (
                  <button type="button" onClick={stopStreaming} className="px-3 py-2 rounded-md bg-red-600 text-white hover:bg-red-700 inline-flex items-center gap-2">
                    <StopCircle className="w-4 h-4" /> Stop
                  </button>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={regenerateLast}
                      title="Regenerate"
                      className="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 inline-flex items-center gap-2"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                    <button type="button" onClick={onSubmit} className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center gap-2">
                      <Send className="w-4 h-4" /> Send
                    </button>
                  </>
                )}
              </div>
              <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">Press Enter to send • Shift+Enter for newline</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tool modal */}
      {pendingTool && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="w-full max-w-md bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{pendingTool.title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{pendingTool.description}</p>
            <div className="space-y-2 mb-4">
              {Object.entries(pendingTool.params || {}).map(([key, spec]) => {
                const type = spec.type;
                const isEnum = Array.isArray(spec.enum);
                const inputType = type === 'number' ? 'number' : spec.format === 'date-time' ? 'datetime-local' : 'text';
                return (
                  <div key={key}>
                    <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                      {key}
                      {spec.required ? ' *' : ''}
                    </label>
                    {isEnum ? (
                      <select
                        className="w-full px-2 py-1.5 rounded-md bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                        value={toolParams[key] ?? ''}
                        onChange={(e) => setToolParams((p) => ({ ...p, [key]: e.target.value }))}
                      >
                        <option value="">Select…</option>
                        {spec.enum.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={inputType}
                        className="w-full px-2 py-1.5 rounded-md bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100"
                        value={toolParams[key] ?? ''}
                        onChange={(e) => setToolParams((p) => ({ ...p, [key]: e.target.value }))}
                        placeholder={spec.type}
                      />
                    )}
                  </div>
                );
              })}
            </div>
            <div className="flex justify-end gap-2">
              <button type="button" className="px-3 py-1.5 rounded-md border border-gray-300 dark:border-gray-700" onClick={() => setPendingTool(null)}>
                Cancel
              </button>
              <button
                type="button"
                className="px-3 py-1.5 rounded-md bg-blue-600 text-white hover:bg-blue-700"
                disabled={execTool.isLoading}
                onClick={async () => {
                  const res = await execTool.mutateAsync({ tool: pendingTool.name, params: toolParams });
                  const content = res?.ok
                    ? `✅ ${pendingTool.title} succeeded: ${JSON.stringify(res.result)}`
                    : `❌ ${pendingTool.title} failed: ${res?.error || 'unknown error'}`;
                  await miniAssistantAPI.createInteraction({ interaction_type: 'assistant_message', content });
                  qc.invalidateQueries(['miniAssistantInteractions']);
                  setPendingTool(null);
                }}
              >
                {execTool.isLoading ? 'Running…' : 'Run'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assistant;
