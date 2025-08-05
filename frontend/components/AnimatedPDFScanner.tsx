'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Card from './ui/Card';
import Button from './ui/Button';
import { PhraseExplanation } from '../lib/api';
import { getDefaultStoryboard, extractPDFSections, generateAnimationStoryboard } from '../utils/animationStoryboard';
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
  Zap,
  Star
} from 'lucide-react';

interface AnimatedPDFScannerProps {
  resumeText: string;
  explanations: PhraseExplanation[];
  matchScore: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  uploadedFile?: File;
  resumeData?: any;
  onComplete: () => void;
}

interface AnimationStep {
  timeline: number;
  bubble_position: { x: number; y: number };
  highlight_area?: { x: number; y: number; width: number; height: number };
  tag_text?: string;
  animation_action: 'move' | 'pause' | 'glow' | 'tag_popout' | 'beam_transfer' | 'complete';
  section_type?: 'name' | 'contact' | 'skills' | 'experience' | 'education';
}

export const AnimatedPDFScanner: React.FC<AnimatedPDFScannerProps> = ({
  resumeText = '',
  explanations = [],
  matchScore = 0,
  summary = '',
  strengths = [],
  weaknesses = [],
  suggestions = [],
  uploadedFile,
  resumeData,
  onComplete
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [detectedSections, setDetectedSections] = useState<string[]>([]);
  const [currentHighlight, setCurrentHighlight] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [persistentHighlights, setPersistentHighlights] = useState<Array<{ x: number; y: number; width: number; height: number; section: string }>>([]);
  const [floatingTags, setFloatingTags] = useState<Array<{ id: number; text: string; x: number; y: number; targetX: number; targetY: number }>>([]);
  const [beamActive, setBeamActive] = useState(false);
  const [beamStart, setBeamStart] = useState({ x: 0, y: 0 });
  const [beamEnd, setBeamEnd] = useState({ x: 0, y: 0 });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const pdfContainerRef = useRef<HTMLDivElement>(null);

  // Create PDF URL from uploaded file
  useEffect(() => {
    if (uploadedFile) {
      const url = URL.createObjectURL(uploadedFile);
      setPdfUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [uploadedFile]);

  // Generate animation storyboard based on resume data
  const animationStoryboard = React.useMemo(() => {
    try {
      // Extract sections from resume data
      const sections = extractPDFSections(resumeData);
      
      if (sections.length > 0) {
        // Generate storyboard based on actual PDF content
        return generateAnimationStoryboard(sections, { width: 800, height: 600 });
      } else {
        // Fallback to default storyboard
        return getDefaultStoryboard();
      }
    } catch (error) {
      console.error('Error generating storyboard:', error);
      return getDefaultStoryboard();
    }
  }, [resumeData]);

  const startAnimation = useCallback(() => {
    setIsPlaying(true);
    setCurrentStep(0);
    setDetectedSections([]);
    setFloatingTags([]);
    setBeamActive(false);
    setCurrentHighlight(null);
    setPersistentHighlights([]); // Clear persistent highlights
    // Reset animation timing
    animationRef.current = undefined;
  }, []);

  const stopAnimation = useCallback(() => {
    setIsPlaying(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  const skipToResults = useCallback(() => {
    stopAnimation();
    setShowResults(true);
  }, [stopAnimation]);

  const animate = useCallback((timestamp: number) => {
    if (!isPlaying) return;

    // Calculate elapsed time since animation started
    if (!animationRef.current) {
      animationRef.current = timestamp;
    }
    
    const elapsedTime = timestamp - animationRef.current;
    const currentStepData = animationStoryboard[currentStep];

    if (!currentStepData) {
      setShowResults(true);
      return;
    }

    if (elapsedTime >= currentStepData.timeline) {
      // Execute animation step
      switch (currentStepData.animation_action) {
        case 'move':
          // Just move the bubble
          break;
        case 'pause':
          // Pause and highlight area
          setCurrentHighlight(currentStepData.highlight_area || null);
          // Add to persistent highlights
          if (currentStepData.highlight_area && currentStepData.tag_text) {
            setPersistentHighlights(prev => [...prev, {
              ...currentStepData.highlight_area!,
              section: currentStepData.tag_text
            }]);
          }
          break;
        case 'glow':
          // Continue glowing effect
          break;
        case 'tag_popout':
          // Create floating tag
          if (currentStepData.tag_text) {
            const newTag = {
              id: Date.now(),
              text: currentStepData.tag_text,
              x: currentStepData.bubble_position.x,
              y: currentStepData.bubble_position.y,
              targetX: 800, // Analysis panel x
              targetY: 100 + detectedSections.length * 40 // Analysis panel y
            };
            setFloatingTags(prev => [...prev, newTag]);
            setDetectedSections(prev => [...prev, currentStepData.tag_text!]);
          }
          break;
        case 'beam_transfer':
          // Activate beam animation
          setBeamStart({ x: currentStepData.bubble_position.x, y: currentStepData.bubble_position.y });
          setBeamEnd({ x: 800, y: 100 + detectedSections.length * 40 });
          setBeamActive(true);
          setTimeout(() => setBeamActive(false), 2000); // Match the slower timing
          break;
        case 'complete':
          // Animation complete - automatically show results
          setShowResults(true);
          // Keep the persistent highlights visible
          return;
      }

      setCurrentStep(prev => prev + 1);
    }

    // Draw animation frame
    drawAnimationFrame(currentStepData);
    animationRef.current = requestAnimationFrame(animate);
  }, [isPlaying, currentStep, detectedSections.length, animationStoryboard]);

  const drawAnimationFrame = useCallback((stepData: AnimationStep) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Always draw persistent highlights (even after completion)
    persistentHighlights.forEach((highlight, index) => {
      ctx.save();
      // Use different colors for different sections
      const colors = [
        'rgba(34, 197, 94, 0.2)',   // green for name
        'rgba(59, 130, 246, 0.2)',  // blue for contact
        'rgba(245, 158, 11, 0.2)',  // orange for skills
        'rgba(168, 85, 247, 0.2)',  // purple for experience
        'rgba(236, 72, 153, 0.2)'   // pink for education
      ];
      const strokeColors = [
        'rgba(34, 197, 94, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(236, 72, 153, 0.8)'
      ];
      
      ctx.fillStyle = colors[index % colors.length];
      ctx.strokeStyle = strokeColors[index % strokeColors.length];
      ctx.lineWidth = 2;
      ctx.shadowColor = strokeColors[index % strokeColors.length];
      ctx.shadowBlur = 6;
      
      ctx.fillRect(
        highlight.x,
        highlight.y,
        highlight.width,
        highlight.height
      );
      ctx.strokeRect(
        highlight.x,
        highlight.y,
        highlight.width,
        highlight.height
      );
      ctx.restore();
    });

    // Draw subtle scanning bubble with background color and distortion
    ctx.save();
    
    // Create bubble with background color and slight magnification
    const bubbleRadius = 25;
    const centerX = stepData.bubble_position.x;
    const centerY = stepData.bubble_position.y;
    
    // Create subtle gradient matching background
    const gradient = ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, bubbleRadius
    );
    gradient.addColorStop(0, 'rgba(243, 244, 246, 0.8)'); // gray-100
    gradient.addColorStop(0.7, 'rgba(229, 231, 235, 0.6)'); // gray-200
    gradient.addColorStop(1, 'rgba(209, 213, 219, 0.4)'); // gray-300
    
    // Draw main bubble with distortion effect
    ctx.beginPath();
    ctx.arc(centerX, centerY, bubbleRadius, 0, 2 * Math.PI);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // Add subtle stroke
    ctx.strokeStyle = 'rgba(156, 163, 175, 0.6)'; // gray-400
    ctx.lineWidth = 1;
    ctx.stroke();
    
    // Add distortion effect (slight magnification)
    ctx.beginPath();
    ctx.arc(centerX, centerY, bubbleRadius + 5, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(156, 163, 175, 0.3)';
    ctx.lineWidth = 1;
    ctx.stroke();
    
    // Add scanning lines (subtle)
    ctx.beginPath();
    ctx.arc(centerX, centerY, bubbleRadius + 10, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(156, 163, 175, 0.2)';
    ctx.lineWidth = 0.5;
    ctx.stroke();
    
    ctx.restore();

    // Draw current highlight area if present (more prominent)
    if (stepData.highlight_area) {
      ctx.save();
      ctx.fillStyle = 'rgba(59, 130, 246, 0.25)';
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.9)';
      ctx.lineWidth = 3;
      ctx.shadowColor = 'rgba(59, 130, 246, 0.5)';
      ctx.shadowBlur = 12;
      
      ctx.fillRect(
        stepData.highlight_area.x,
        stepData.highlight_area.y,
        stepData.highlight_area.width,
        stepData.highlight_area.height
      );
      ctx.strokeRect(
        stepData.highlight_area.x,
        stepData.highlight_area.y,
        stepData.highlight_area.width,
        stepData.highlight_area.height
      );
      ctx.restore();
    }

    // Draw beam if active (more subtle)
    if (beamActive) {
      ctx.save();
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.6)';
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 4]);
      
      ctx.beginPath();
      ctx.moveTo(beamStart.x, beamStart.y);
      ctx.lineTo(beamEnd.x, beamEnd.y);
      ctx.stroke();
      ctx.restore();
    }
  }, [beamActive, beamStart, beamEnd]);

  useEffect(() => {
    if (isPlaying) {
      const startTime = performance.now();
      animationRef.current = startTime;
      requestAnimationFrame(animate);
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, animate]);

  if (showResults) {
    return (
      <div className="h-screen flex flex-col">
        {/* Keep the current scanning interface */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h3 className="text-xl font-bold text-gray-900">🔍 Animated PDF Scanner</h3>
              <span className="text-sm text-green-600 bg-green-100 px-2 py-1 rounded">
                Scan Complete
              </span>
            </div>
          </div>
        </div>

        {/* Main Content - Split Layout */}
        <div className="flex-1 flex">
          {/* Left Side - PDF Container (Full Height) */}
          <div className="w-1/2 bg-gray-50 relative">
            <div className="h-full flex flex-col">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Resume PDF</h3>
                </div>
              </div>
              <div className="flex-1 relative">
                {pdfUrl && (
                  <iframe
                    src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0`}
                    className="w-full h-full"
                    title="Resume PDF"
                  />
                )}
                {/* Animation Canvas Overlay - Keep persistent highlights */}
                <canvas
                  ref={canvasRef}
                  className="absolute inset-0 pointer-events-none"
                  width={800}
                  height={600}
                />
              </div>
            </div>
          </div>

          {/* Right Side - Analysis Panel */}
          <div className="w-1/2 bg-white border-l border-gray-200 overflow-y-auto">
            <div className="p-6 space-y-6">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <Star className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Extracted Content</h3>
                </div>
                
                {/* Detected Sections */}
                <div className="space-y-3 mb-6">
                  {detectedSections.map((section, index) => (
                    <div
                      key={index}
                      className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg"
                    >
                      <div className="flex items-center space-x-2 mb-2">
                        <CheckCircle className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">{section}</span>
                        <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                          Highlighted
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Content extracted and analyzed...
                      </div>
                    </div>
                  ))}
                </div>

                {/* Persistent Highlights Status */}
                {persistentHighlights.length > 0 && (
                  <div className="mb-6">
                    <div className="flex items-center space-x-2 mb-3">
                      <Eye className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">Currently Highlighted</span>
                    </div>
                    <div className="space-y-2">
                      {persistentHighlights.map((highlight, index) => (
                        <div
                          key={index}
                          className="p-2 bg-green-50 border border-green-200 rounded text-xs"
                        >
                          <span className="text-green-700">{highlight.section}</span>
                          <span className="text-green-500 ml-2">• Active on PDF</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analysis Results */}
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Target className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">Match Score</span>
                    </div>
                    <div className="text-2xl font-bold text-green-700">{matchScore}%</div>
                  </div>
                  
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-800">Analysis Progress</span>
                    </div>
                    <div className="text-sm text-purple-700">
                      Features Analyzed: {explanations.length}
                    </div>
                    <div className="text-sm text-purple-700">
                      Sections Detected: {detectedSections.length}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section - Automatically appear below */}
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">🎉 Analysis Complete!</h2>
              <p className="text-gray-600">Your resume has been thoroughly analyzed with AI-powered scanning</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Match Score */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200">
                <div className="text-center">
                  <div className="text-5xl font-bold text-green-600 mb-2">{matchScore}%</div>
                  <div className="text-lg font-semibold text-green-800 mb-1">Match Score</div>
                  <div className="text-sm text-green-600">AI-powered analysis</div>
                </div>
              </div>

              {/* Strengths */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 mb-2">{strengths.length}</div>
                  <div className="text-lg font-semibold text-blue-800 mb-1">Strengths</div>
                  <div className="text-sm text-blue-600">Identified areas</div>
                </div>
              </div>

              {/* Improvements */}
              <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-xl border border-orange-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600 mb-2">{suggestions.length}</div>
                  <div className="text-lg font-semibold text-orange-800 mb-1">Suggestions</div>
                  <div className="text-sm text-orange-600">For improvement</div>
                </div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Strengths */}
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                  Key Strengths
                </h3>
                <ul className="space-y-2">
                  {strengths.slice(0, 5).map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Suggestions */}
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
                  Improvement Suggestions
                </h3>
                <ul className="space-y-2">
                  {suggestions.slice(0, 5).map((suggestion, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Summary */}
            <div className="mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-xl border border-purple-200">
              <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
                <Brain className="w-5 h-5 text-purple-600 mr-2" />
                Analysis Summary
              </h3>
              <p className="text-purple-800">{summary}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-xl font-bold text-gray-900">🔍 Animated PDF Scanner</h3>
            {currentHighlight && (
              <span className="text-sm text-primary-600 bg-primary-100 px-2 py-1 rounded">
                Scanning...
              </span>
            )}
          </div>
                  <div className="flex space-x-2">
          <Button
            onClick={isPlaying ? stopAnimation : startAnimation}
            variant={isPlaying ? "warning" : "primary"}
            size="sm"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button
            onClick={skipToResults}
            variant="secondary"
            size="sm"
          >
            <SkipForward className="w-4 h-4" />
          </Button>
          <Button
            onClick={onComplete}
            variant="success"
            size="sm"
          >
            <CheckCircle className="w-4 h-4" />
            View Analysis
          </Button>
        </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-3">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>Progress: {currentStep} / {animationStoryboard.length}</span>
            <span>{Math.round((currentStep / animationStoryboard.length) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / animationStoryboard.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Main Content - Split Layout */}
      <div className="flex-1 flex">
        {/* Left Side - PDF Container (Full Height) */}
        <div className="w-1/2 bg-gray-50 relative">
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">Resume PDF</h3>
              </div>
            </div>
            <div className="flex-1 relative">
              {pdfUrl && (
                <iframe
                  src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0`}
                  className="w-full h-full"
                  title="Resume PDF"
                />
              )}
              {/* Animation Canvas Overlay */}
              <canvas
                ref={canvasRef}
                className="absolute inset-0 pointer-events-none"
                width={800}
                height={600}
              />
            </div>
          </div>
        </div>

        {/* Right Side - Analysis Panel */}
        <div className="w-1/2 bg-white border-l border-gray-200 overflow-y-auto">
          <div className="p-6 space-y-6">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Star className="w-5 h-5 text-primary-600" />
                <h3 className="text-lg font-semibold text-gray-900">Extracted Content</h3>
              </div>
              
              {/* Detected Sections */}
              <div className="space-y-3 mb-6">
                {detectedSections.map((section, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">{section}</span>
                      <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                        Highlighted
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Content extracted and analyzed...
                    </div>
                  </div>
                ))}
                {detectedSections.length === 0 && (
                  <div className="text-gray-500 text-sm text-center py-8 border-2 border-dashed border-gray-200 rounded-lg">
                    <div className="mb-2">📄</div>
                    Waiting for scan results...
                    <div className="text-xs mt-2">The scanner will extract text and bring it here</div>
                  </div>
                )}
              </div>

              {/* Persistent Highlights Status */}
              {persistentHighlights.length > 0 && (
                <div className="mb-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <Eye className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Currently Highlighted</span>
                  </div>
                  <div className="space-y-2">
                    {persistentHighlights.map((highlight, index) => (
                      <div
                        key={index}
                        className="p-2 bg-green-50 border border-green-200 rounded text-xs"
                      >
                        <span className="text-green-700">{highlight.section}</span>
                        <span className="text-green-500 ml-2">• Active on PDF</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Analysis Results */}
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Target className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Match Score</span>
                  </div>
                  <div className="text-2xl font-bold text-green-700">{matchScore}%</div>
                </div>
                
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-800">Analysis Progress</span>
                  </div>
                  <div className="text-sm text-purple-700">
                    Features Analyzed: {explanations.length}
                  </div>
                  <div className="text-sm text-purple-700">
                    Sections Detected: {detectedSections.length}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Tags */}
      {floatingTags.map((tag) => (
        <div
          key={tag.id}
          className="fixed pointer-events-none z-50 animate-pulse"
          style={{
            left: tag.x,
            top: tag.y,
            transform: 'translate(-50%, -50%)'
          }}
        >
          <div className="bg-primary-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
            {tag.text}
          </div>
        </div>
      ))}
    </div>
  );
}; 