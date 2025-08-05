'use client';

import React, { useState, useEffect, useRef } from 'react';
import Card from './ui/Card';
import Button from './ui/Button';
import { PhraseExplanation } from '../lib/api';
import { 
  Play, 
  Pause, 
  SkipForward, 
  Eye, 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  FileText,
  Zap
} from 'lucide-react';

interface LivePDFScannerProps {
  resumeText: string;
  explanations: PhraseExplanation[];
  matchScore: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  uploadedFile?: File;
  onComplete: () => void;
}

export const LivePDFScanner: React.FC<LivePDFScannerProps> = ({
  resumeText = '',
  explanations = [],
  matchScore = 0,
  summary = '',
  strengths = [],
  weaknesses = [],
  suggestions = [],
  uploadedFile,
  onComplete
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scannedItems, setScannedItems] = useState<PhraseExplanation[]>([]);
  const [showInsights, setShowInsights] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [currentHighlight, setCurrentHighlight] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [liveAnalysis, setLiveAnalysis] = useState<string[]>([]);
  const pdfRef = useRef<HTMLIFrameElement>(null);

  // Filter explanations to only include significant items
  const significantExplanations = explanations?.filter(exp => Math.abs(exp.weight) >= 3) || [];

  // Create PDF URL from uploaded file
  useEffect(() => {
    if (uploadedFile) {
      const url = URL.createObjectURL(uploadedFile);
      setPdfUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [uploadedFile]);

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying && currentIndex < significantExplanations.length) {
      const timer = setTimeout(() => {
        handleNext();
      }, 1500); // 1.5 seconds per item
      return () => clearTimeout(timer);
    }
  }, [isPlaying, currentIndex, significantExplanations.length]);

  // Live analysis simulation
  useEffect(() => {
    if (isPlaying && currentIndex < significantExplanations.length) {
      const currentExp = significantExplanations[currentIndex];
      
      // Simulate live analysis
      const analysisSteps = [
        `🔍 Scanning for "${currentExp.phrase}"...`,
        `📊 Analyzing impact: ${currentExp.weight > 0 ? 'Positive' : 'Negative'} match`,
        `💡 Weight assessment: ${currentExp.weight}/10`,
        `📝 Justification: ${currentExp.justification}`,
        `✅ Feature detected and analyzed!`
      ];

      let stepIndex = 0;
      const analysisTimer = setInterval(() => {
        if (stepIndex < analysisSteps.length) {
          setLiveAnalysis(prev => [...prev.slice(-2), analysisSteps[stepIndex]]);
          stepIndex++;
        } else {
          clearInterval(analysisTimer);
        }
      }, 300);

      return () => clearInterval(analysisTimer);
    }
  }, [currentIndex, isPlaying, significantExplanations]);

  const handleNext = () => {
    if (currentIndex < significantExplanations.length) {
      const currentExp = significantExplanations[currentIndex];
      setScannedItems(prev => [...prev, currentExp]);
      setCurrentHighlight(currentExp.phrase);
      setCurrentIndex(prev => prev + 1);
      setAnalysisProgress((currentIndex + 1) / significantExplanations.length * 100);
    } else {
      setIsPlaying(false);
      setShowInsights(true);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
      setScannedItems(prev => prev.slice(0, -1));
      setAnalysisProgress((currentIndex - 1) / significantExplanations.length * 100);
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSkip = () => {
    setShowInsights(true);
    setIsPlaying(false);
  };

  const handleComplete = () => {
    onComplete();
  };

  const getWeightColor = (weight: number) => {
    if (weight >= 7) return 'text-green-600 bg-green-100';
    if (weight >= 4) return 'text-blue-600 bg-blue-100';
    if (weight >= 0) return 'text-yellow-600 bg-yellow-100';
    if (weight >= -3) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getWeightIcon = (weight: number) => {
    if (weight >= 7) return '🟢';
    if (weight >= 4) return '🟡';
    return '🔴';
  };

  if (showInsights) {
    return (
      <div className="space-y-6">
        <Card>
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">🎉 Live Analysis Complete!</h3>
            <p className="text-gray-600 mb-4">Your resume has been scanned and analyzed in real-time</p>
            <div className="flex items-center justify-center space-x-4">
              <div className="text-6xl font-bold text-primary-600">{matchScore}%</div>
              <div className="text-left">
                <p className="text-sm text-gray-600">Final Match Score</p>
                <p className="text-xs text-gray-500">AI-powered analysis</p>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <div className="flex items-center space-x-2 mb-4">
              <TrendingUp className="w-5 h-5 text-success-600" />
              <h3 className="text-lg font-semibold text-gray-900">Strengths Found</h3>
            </div>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">{strength}</span>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <div className="flex items-center space-x-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-warning-600" />
              <h3 className="text-lg font-semibold text-gray-900">Areas for Improvement</h3>
            </div>
            <ul className="space-y-2">
              {weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">{weakness}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <Zap className="w-5 h-5 text-warning-600" />
            <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          </div>
          <ul className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-gray-700">{suggestion}</span>
              </li>
            ))}
          </ul>
        </Card>

        <div className="flex justify-center">
          <Button onClick={handleComplete} variant="primary" size="lg">
            <CheckCircle className="w-5 h-5 mr-2" />
            View Full Analysis
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">🔍 Live PDF Scanner</h3>
          <p className="text-gray-600">Watching AI analyze your resume in real-time</p>
        </div>
      </Card>

      {/* Progress and Controls */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Progress: {currentIndex + 1} / {significantExplanations.length}
            </div>
            <div className="text-sm text-gray-600">
              {Math.round(analysisProgress)}% Complete
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              variant="secondary"
              size="sm"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <Button
              onClick={handlePlayPause}
              variant={isPlaying ? "warning" : "primary"}
              size="sm"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button
              onClick={handleNext}
              disabled={currentIndex >= significantExplanations.length}
              variant="secondary"
              size="sm"
            >
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button
              onClick={handleSkip}
              variant="secondary"
              size="sm"
            >
              <SkipForward className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${analysisProgress}%` }}
          ></div>
        </div>

        {/* Current Item */}
        {currentIndex < significantExplanations.length && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-5 h-5 text-blue-600" />
              <h4 className="font-medium text-blue-900">Currently Scanning:</h4>
            </div>
            <div className="space-y-2">
              <p className="text-blue-800 font-medium">
                "{significantExplanations[currentIndex].phrase}"
              </p>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getWeightColor(significantExplanations[currentIndex].weight)}`}>
                  {getWeightIcon(significantExplanations[currentIndex].weight)} 
                  Weight: {significantExplanations[currentIndex].weight}/10
                </span>
                <span className="text-xs text-blue-600">
                  {significantExplanations[currentIndex].category}
                </span>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Live Analysis Feed */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="w-5 h-5 text-yellow-600" />
          <h3 className="text-lg font-semibold text-gray-900">Live Analysis Feed</h3>
        </div>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-32 overflow-y-auto">
          {liveAnalysis.map((message, index) => (
            <div key={index} className="mb-1">
              <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {message}
            </div>
          ))}
          {liveAnalysis.length === 0 && (
            <div className="text-gray-500">Waiting for analysis to begin...</div>
          )}
        </div>
      </Card>

      {/* PDF Display */}
      {pdfUrl && (
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <FileText className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Resume PDF</h3>
            {currentHighlight && (
              <span className="text-sm text-primary-600 bg-primary-100 px-2 py-1 rounded">
                Highlighting: "{currentHighlight}"
              </span>
            )}
          </div>
          <div className="border rounded-lg overflow-hidden">
            <iframe
              ref={pdfRef}
              src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0`}
              className="w-full h-96"
              title="Resume PDF"
            />
          </div>
        </Card>
      )}

      {/* Scanned Items Summary */}
      <Card>
        <div className="flex items-center space-x-2 mb-4">
          <CheckCircle className="w-5 h-5 text-success-600" />
          <h3 className="text-lg font-semibold text-gray-900">Scanned Features</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scannedItems.map((item, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getWeightColor(item.weight)}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm">"{item.phrase}"</span>
                <span className="text-xs font-bold">
                  {getWeightIcon(item.weight)} {item.weight}/10
                </span>
              </div>
              <p className="text-xs mt-1 opacity-75">{item.category}</p>
            </div>
          ))}
        </div>
        {scannedItems.length === 0 && (
          <p className="text-gray-500 text-sm">No features scanned yet...</p>
        )}
      </Card>
    </div>
  );
}; 