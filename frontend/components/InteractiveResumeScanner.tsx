'use client';

import React, { useState, useEffect } from 'react';
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
  ArrowLeft
} from 'lucide-react';

interface InteractiveResumeScannerProps {
  resumeText: string;
  explanations: PhraseExplanation[];
  matchScore: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  onComplete: () => void;
}

export const InteractiveResumeScanner: React.FC<InteractiveResumeScannerProps> = ({
  resumeText = '',
  explanations = [],
  matchScore = 0,
  summary = '',
  strengths = [],
  weaknesses = [],
  suggestions = [],
  onComplete
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [highlightedText, setHighlightedText] = useState(resumeText);
  const [scannedItems, setScannedItems] = useState<PhraseExplanation[]>([]);
  const [showInsights, setShowInsights] = useState(false);

  // Filter explanations to only include positive and significant items
  const significantExplanations = explanations?.filter(exp => exp.weight > 0) || [];

  useEffect(() => {
    if (isPlaying && currentIndex < significantExplanations.length) {
      const timer = setTimeout(() => {
        handleNext();
      }, 2000); // 2 seconds per item
      return () => clearTimeout(timer);
    }
  }, [isPlaying, currentIndex, significantExplanations.length]);

  const highlightCurrentItem = (text: string, currentExp: PhraseExplanation) => {
    const regex = new RegExp(`(${currentExp.phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, `<span class="highlight-current bg-yellow-300 border-2 border-yellow-500 px-1 rounded font-bold">$1</span>`);
  };

  const highlightScannedItems = (text: string) => {
    let highlighted = text;
    scannedItems.forEach((exp, index) => {
      const regex = new RegExp(`(${exp.phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      const weight = exp.weight;
      let className = '';
      if (weight >= 7) className = 'bg-green-200 border-green-500';
      else if (weight >= 4) className = 'bg-blue-200 border-blue-500';
      else className = 'bg-yellow-200 border-yellow-500';
      
      highlighted = highlighted.replace(regex, 
        `<span class="highlight-scanned ${className} border px-1 rounded">$1</span>`
      );
    });
    return highlighted;
  };

  const handleNext = () => {
    if (currentIndex < significantExplanations.length) {
      const currentExp = significantExplanations[currentIndex];
      setScannedItems(prev => [...prev, currentExp]);
      setCurrentIndex(prev => prev + 1);
    } else {
      setIsPlaying(false);
      setShowInsights(true);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
      setScannedItems(prev => prev.slice(0, -1));
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSkip = () => {
    setCurrentIndex(significantExplanations.length);
    setScannedItems(significantExplanations);
    setIsPlaying(false);
    setShowInsights(true);
  };

  const handleComplete = () => {
    onComplete();
  };

  const currentExp = significantExplanations[currentIndex];
  const progress = (currentIndex / significantExplanations.length) * 100;

  if (showInsights) {
    return (
      <div className="space-y-6">
        <Card>
          <div className="text-center mb-6">
            <CheckCircle className="w-16 h-16 text-success-600 mx-auto mb-4" />
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Scan Complete!</h2>
            <p className="text-lg text-gray-600">Analysis finished. Here are your insights:</p>
          </div>
        </Card>

        {/* Match Score */}
        <Card>
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Final Match Score</h3>
            <div className="flex items-center justify-center space-x-4">
              <div className="text-6xl font-bold text-primary-600">{matchScore}%</div>
              <div className="text-left">
                <p className="text-sm text-gray-600">Overall Match</p>
                <p className="text-xs text-gray-500">Based on {scannedItems.length} key factors</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Summary */}
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <Eye className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Analysis Summary</h3>
          </div>
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </Card>

        {/* Strengths and Weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <div className="flex items-center space-x-2 mb-4">
              <TrendingUp className="w-5 h-5 text-success-600" />
              <h3 className="text-lg font-semibold text-gray-900">Strengths Found</h3>
            </div>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-success-500 mt-1 flex-shrink-0" />
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
                  <AlertTriangle className="w-4 h-4 text-warning-500 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">{weakness}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        {/* Suggestions */}
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          </div>
          <ul className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-gray-700">{suggestion}</span>
              </li>
            ))}
          </ul>
        </Card>

        <div className="flex justify-center">
          <Button onClick={handleComplete} size="lg">
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
        <div className="text-center mb-6">
          <Eye className="w-16 h-16 text-primary-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Interactive Resume Scanner</h2>
          <p className="text-lg text-gray-600">
            Click through or auto-scan to see how your resume matches the job requirements
          </p>
        </div>
      </Card>

      {/* Progress */}
      <Card>
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Scanning Progress: {currentIndex + 1} of {significantExplanations.length}
            </span>
            <span className="text-sm font-medium text-primary-600">
              {Math.round(progress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex justify-center space-x-4">
          <Button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            variant="secondary"
            size="sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          
          <Button
            onClick={handlePlayPause}
            variant={isPlaying ? "warning" : "primary"}
            size="sm"
          >
            {isPlaying ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Auto-Scan
              </>
            )}
          </Button>
          
          <Button
            onClick={handleNext}
            disabled={currentIndex >= significantExplanations.length}
            variant="success"
            size="sm"
          >
            <ArrowRight className="w-4 h-4 mr-2" />
            Next
          </Button>
          
          <Button
            onClick={handleSkip}
            variant="secondary"
            size="sm"
          >
            <SkipForward className="w-4 h-4 mr-2" />
            Skip to End
          </Button>
        </div>
      </Card>

      {/* Current Item */}
      {currentExp && (
        <Card>
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Currently Scanning</h3>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-blue-900">
                {currentExp.category.charAt(0).toUpperCase() + currentExp.category.slice(1)}
              </span>
              <span className="text-sm font-bold text-blue-600">
                +{currentExp.weight}/10
              </span>
            </div>
            <p className="text-blue-900 font-medium mb-2">"{currentExp.phrase}"</p>
            <p className="text-blue-700 text-sm">{currentExp.justification}</p>
          </div>
        </Card>
      )}

      {/* Resume Display */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Resume with Highlights</h3>
        <div 
          className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto border"
          dangerouslySetInnerHTML={{ 
            __html: currentExp 
              ? highlightCurrentItem(highlightScannedItems(resumeText), currentExp)
              : highlightScannedItems(resumeText)
          }}
        />
        <div className="mt-4 text-xs text-gray-500">
          <p><strong>Legend:</strong></p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="bg-yellow-300 border-yellow-500 border-2 px-2 rounded font-bold">Currently Scanning</span>
            <span className="bg-green-200 border-green-500 border px-2 rounded">High Impact (+7-10)</span>
            <span className="bg-blue-200 border-blue-500 border px-2 rounded">Medium Impact (+4-6)</span>
            <span className="bg-yellow-200 border-yellow-500 border px-2 rounded">Low Impact (+1-3)</span>
          </div>
        </div>
      </Card>

      {/* Scanned Items Summary */}
      {scannedItems.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Scanned Items ({scannedItems.length})
          </h3>
          <div className="space-y-2">
            {scannedItems.map((exp, index) => (
              <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                <CheckCircle className="w-4 h-4 text-success-500" />
                <span className="text-sm font-medium">{exp.phrase}</span>
                <span className="text-xs text-gray-500">+{exp.weight}/10</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}; 