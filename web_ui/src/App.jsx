import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Upload, MessageSquare, CheckCircle, Download, AlertCircle, Loader2, ChevronRight } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const API_BASE = "http://localhost:8000";

export default function App() {
  const [step, setStep] = useState(1); // 1: Upload, 2: Clarification, 3: Success
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [clarifications, setClarifications] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentClarificationIdx, setCurrentClarificationIdx] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const resp = await axios.post(`${API_BASE}/upload`, formData);
      setSessionId(resp.data.session_id);

      // Merge AI clarifications with general preferences
      const tasks = [
        ...resp.data.clarifications,
        { field: "difficulty", question: "Is this subject difficult? (yes/no)" },
        { field: "revision", question: "Do you want dedicated revision weeks? (yes/no)" }
      ];

      setClarifications(tasks);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to process syllabus.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (answer) => {
    const currentTask = clarifications[currentClarificationIdx];
    setAnswers({ ...answers, [currentTask.field]: answer });

    if (currentClarificationIdx < clarifications.length - 1) {
      setCurrentClarificationIdx(currentClarificationIdx + 1);
    } else {
      finishRefinement();
    }
  };

  const finishRefinement = async () => {
    setLoading(true);
    try {
      const resp = await axios.post(`${API_BASE}/refine`, {
        session_id: sessionId,
        answers: answers
      });
      setResult(resp.data);
      setStep(3);
    } catch (err) {
      setError("Failed to generate plan.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-3xl w-full bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-primary-600/20 rounded-2xl border border-primary-500/30">
            <Upload className="w-6 h-6 text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Semester Planner AI</h1>
            <p className="text-slate-400 text-sm">Convert your raw syllabus into a structured study schedule.</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-3 text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Step 1: Upload */}
        {step === 1 && (
          <div className="space-y-6">
            <div
              className="relative group border-2 border-dashed border-slate-700 hover:border-primary-500/50 rounded-3xl p-12 transition-all flex flex-col items-center justify-center text-center bg-slate-800/20 hover:bg-slate-800/40"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files[0];
                if (file) handleFileUpload({ target: { files: [file] } });
              }}
            >
              <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleFileUpload}
                accept=".pdf,.docx,.png,.jpg,.jpeg"
              />
              <div className="p-4 bg-slate-700/30 rounded-full mb-4 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8 text-slate-400 group-hover:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Upload Syllabus</h3>
              <p className="text-slate-400 text-sm mb-4">PDF, Word, or Image files supported.</p>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <span className="px-2 py-1 bg-slate-800 rounded">PDF</span>
                <span className="px-2 py-1 bg-slate-800 rounded">DOCX</span>
                <span className="px-2 py-1 bg-slate-800 rounded">JPG/PNG</span>
              </div>
            </div>

            {loading && (
              <div className="flex flex-col items-center gap-4 py-4 animate-in fade-in transition-all">
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                <p className="text-slate-400 animate-pulse text-sm">Analyzing syllabus content via OCR & AI...</p>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Clarification */}
        {step === 2 && (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 transition-all">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2 font-mono">
              <span>AGENT DIALOGUE</span>
              <span>{currentClarificationIdx + 1} / {clarifications.length}</span>
            </div>

            <div className="p-6 bg-slate-800/40 rounded-3xl border border-white/5 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <MessageSquare className="w-20 h-20" />
              </div>
              <div className="relative z-10">
                <h3 className="text-lg text-white font-medium mb-1">
                  {clarifications[currentClarificationIdx]?.question}
                </h3>
                {clarifications[currentClarificationIdx]?.context && (
                  <p className="text-slate-400 text-sm mb-6 bg-slate-900/50 p-2 rounded inline-block">
                    Context: {clarifications[currentClarificationIdx].context}
                  </p>
                )}

                <div className="flex flex-col gap-3">
                  <input
                    autoFocus
                    type="text"
                    className="w-full bg-slate-950 border border-slate-700 rounded-2xl p-4 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all outline-none"
                    placeholder="Type your answer here..."
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        handleAnswer(e.target.value);
                        e.target.value = "";
                      }
                    }}
                  />
                  <div className="flex justify-between items-center text-xs text-slate-500 px-2 mt-2">
                    <p>Press Enter to continue</p>
                    <button
                      onClick={() => {
                        const input = document.querySelector('input[type="text"]');
                        if (input.value.trim()) {
                          handleAnswer(input.value);
                          input.value = "";
                        }
                      }}
                      className="text-primary-400 hover:text-primary-300 flex items-center gap-1 transition-colors"
                    >
                      Submit <ChevronRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {loading && (
              <div className="flex justify-center gap-4 py-4 animate-in fade-in transition-all">
                <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
                <p className="text-slate-400">Finalizing your study cycle...</p>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Success */}
        {step === 3 && (
          <div className="text-center space-y-8 animate-in zoom-in-95 duration-300">
            <div className="flex justify-center">
              <div className="p-6 bg-green-500/10 rounded-full border border-green-500/20">
                <CheckCircle className="w-16 h-16 text-green-400" />
              </div>
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Plan Generated!</h2>
              <p className="text-slate-400">Version {result?.version} is ready for download.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-6 bg-slate-800/40 rounded-3xl border border-white/5 text-left">
                <h4 className="text-xs font-mono text-slate-500 mb-2">FILE STATS</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Format:</span>
                    <span className="text-white">Excel (XLSX)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Version:</span>
                    <span className="text-white">{result?.version}</span>
                  </div>
                </div>
              </div>

              <a
                href={`${API_BASE}/download/${result?.version}`}
                download
                className="flex flex-col items-center justify-center p-6 bg-primary-600 hover:bg-primary-500 text-white rounded-3xl border border-primary-400/30 transition-all shadow-lg hover:shadow-primary-500/20 group"
              >
                <Download className="w-8 h-8 mb-2 group-hover:bounce" />
                <span className="font-semibold">Download Planner</span>
              </a>
            </div>

            <button
              onClick={() => {
                setStep(1);
                setFile(null);
                setAnswers({});
                setCurrentClarificationIdx(0);
                setResult(null);
              }}
              className="text-slate-500 hover:text-white transition-colors text-sm underline underline-offset-4"
            >
              Process another syllabus
            </button>
          </div>
        )}
      </div>

      <p className="mt-8 text-slate-600 text-xs font-mono">
        GEMINI POWERED • LOCAL DEPLOYMENT • v2.0
      </p>
    </div>
  );
}
