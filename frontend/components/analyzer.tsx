'use client';

import { useState, useRef } from 'react';
import { UploadCloud, FileText, ShieldAlert, Copy, FileText as FileTextIcon } from 'lucide-react';
import { jsPDF } from 'jspdf';

interface FraudTransaction {
  trans_num: string;
  trans_date_trans_time: string;
  reason: string;
  confidence: 'low' | 'medium' | 'high';
}

export default function TransactionAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<FraudTransaction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Clear previous results immediately
    setResults([]);
    setError(null);
    setCopied(false);

    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const analyzeFile = async () => {
    if (!file || isLoading) return;

    setResults([]);
    setCopied(false);
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();
      setResults(data.fraud_analysis);
      setCopied(false);
    } catch {
      setError('Unable to analyze the uploaded file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (results.length > 0) {
      const text = results
        .map(
          (r, i) =>
            `${i + 1}. trans_num: ${r.trans_num}\n   trans_date_trans_time: ${r.trans_date_trans_time}\n   Reason: ${r.reason}\n   Confidence: ${r.confidence}`
        )
        .join('\n\n');
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadPDF = () => {
    if (results.length === 0) return;
    const doc = new jsPDF();
    doc.setFontSize(12);
    let y = 10;

    results.forEach((r, i) => {
      const confidenceEmoji =
        r.confidence === 'high' ? '🔴' : r.confidence === 'medium' ? '🟠' : '🟡';

      doc.text(`${i + 1}. ${confidenceEmoji} trans_num: ${r.trans_num}`, 10, y);
      y += 7;
      doc.text(`   trans_date_trans_time: ${r.trans_date_trans_time}`, 10, y);
      y += 7;
      doc.text(`   Reason: ${r.reason}`, 10, y);
      y += 7;
      doc.text(`   Confidence: ${r.confidence}`, 10, y);
      y += 10;
    });

    doc.save('transaction_analysis.pdf');
  };

  return (
    <div className="w-full bg-white rounded-2xl shadow-lg border border-gray-200">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-200 bg-slate-800 text-white rounded-t-2xl">
        <ShieldAlert className="w-6 h-6" />
        <h2 className="text-lg font-semibold">Transaction Risk Analysis</h2>
      </div>

      {/* Upload Section */}
      <div className="p-6 space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-slate-600 transition-colors relative">
          <FileText className="w-10 h-10 mx-auto text-gray-400 mb-3" />

          {/* File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={isLoading}
            className="block w-full text-sm text-gray-600
                       file:mr-4 file:py-2 file:px-4
                       file:rounded-lg file:border-0
                       file:text-sm file:font-medium
                       file:bg-slate-700 file:text-white
                       hover:file:bg-slate-800
                       cursor-pointer
                       file:placeholder-transparent" // hides default filename
          />

          {/* Custom filename + clear button */}
          {file && (
            <div className="absolute top-4 right-4 flex items-center gap-2 bg-gray-100 rounded px-2 py-1">
              <span className="text-gray-800 text-sm">{file.name}</span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-gray-500 hover:text-gray-800 font-bold"
              >
                ✖
              </button>
            </div>
          )}
        </div>

        <button
          onClick={analyzeFile}
          disabled={!file || isLoading}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <UploadCloud className="w-5 h-5" />
          Analyze Transactions
        </button>

        {isLoading && (
          <div className="w-full h-1 bg-gray-200 rounded overflow-hidden">
            <div className="h-full w-2/3 bg-slate-700 animate-pulse" />
          </div>
        )}

        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="border-t border-gray-200 p-6 bg-gray-50 rounded-b-2xl space-y-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase">
            Analysis Output
          </h3>

          <div className="space-y-4">
            {results.map((r, i) => {
              const confidenceEmoji =
                r.confidence === 'high' ? '🔴' : r.confidence === 'medium' ? '🟠' : '🟡';

              return (
                <div key={i} className="bg-white border border-gray-200 rounded-lg p-4">
                  <p>
                    <span className="font-bold">#{i + 1} {confidenceEmoji} trans_num:</span>{' '}
                    {r.trans_num}
                  </p>
                  <p>
                    <span className="font-bold">trans_date_trans_time:</span> {r.trans_date_trans_time}
                  </p>
                  <p>
                    <span className="font-bold">Reason:</span> {r.reason}
                  </p>
                  <p>
                    <span className="font-bold">Confidence:</span> {r.confidence}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Copy / Download Buttons */}
          <div className="flex gap-2 mt-4">
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Copy className="w-4 h-4" />
              {copied ? 'Copied!' : 'Copy'}
            </button>

            <button
              onClick={downloadPDF}
              className="flex items-center gap-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              <FileTextIcon className="w-4 h-4" />
              Download PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
