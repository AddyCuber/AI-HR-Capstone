import React, { useState } from 'react';
import { Target, TrendingUp, AlertTriangle, CheckCircle, XCircle, Lightbulb, BookOpen } from 'lucide-react';
import { MatchResponse, EnhancedResumeResponse } from '../lib/api';
import Card from './ui/Card';
import dynamic from 'next/dynamic';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false }) as any;

interface AnalysisResultsProps {
  matchResults: MatchResponse;
  enhancedResume?: EnhancedResumeResponse;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ matchResults, enhancedResume }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'strengths' | 'improvements' | 'enhancements'>('overview');

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600';
    if (score >= 60) return 'text-warning-600';
    return 'text-danger-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-success-100';
    if (score >= 60) return 'bg-warning-100';
    return 'bg-danger-100';
  };

  const gaugeData = {
    type: 'indicator',
    mode: 'gauge+number+delta',
    value: matchResults.match_score,
    domain: { x: [0, 1], y: [0, 1] },
    title: { text: 'Match Score', font: { size: 24 } },
    delta: { reference: 50 },
    gauge: {
      axis: { range: [null, 100], tickwidth: 1, tickcolor: 'darkblue' },
      bar: { color: 'darkblue' },
      bgcolor: 'white',
      borderwidth: 2,
      bordercolor: 'gray',
      steps: [
        { range: [0, 50], color: 'lightgray' },
        { range: [50, 75], color: 'yellow' },
        { range: [75, 100], color: 'green' }
      ],
      threshold: {
        line: { color: 'red', width: 4 },
        thickness: 0.75,
        value: 90
      }
    }
  };

  const gaugeLayout = {
    width: 400,
    height: 300,
    margin: { t: 25, r: 25, l: 25, b: 25 }
  };

  return (
    <div className="space-y-6">
      {/* Score Overview */}
      <Card title="📊 Analysis Results" subtitle="AI-powered resume analysis">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="metric-card text-center">
            <div className={`text-3xl font-bold ${getScoreColor(matchResults.match_score)}`}>
              {matchResults.match_score}%
            </div>
            <div className="text-sm text-gray-600">Overall Match</div>
          </div>
          
          <div className="metric-card text-center">
            <div className="text-2xl font-bold text-success-600">
              {matchResults.strengths.length}
            </div>
            <div className="text-sm text-gray-600">Strengths</div>
          </div>
          
          <div className="metric-card text-center">
            <div className="text-2xl font-bold text-warning-600">
              {matchResults.missing.length}
            </div>
            <div className="text-sm text-gray-600">Areas to Improve</div>
          </div>
          
          <div className="metric-card text-center">
            <div className="text-2xl font-bold text-primary-600">
              {matchResults.skill_gap_suggestions.length}
            </div>
            <div className="text-sm text-gray-600">Suggestions</div>
          </div>
        </div>

        {/* Gauge Chart */}
        <div className="flex justify-center mb-6">
          <Plot
            data={[gaugeData]}
            layout={gaugeLayout}
            config={{ displayModeBar: false }}
            className="w-full max-w-md"
          />
        </div>
      </Card>

      {/* Detailed Analysis Tabs */}
      <Card>
        <div className="border-b border-gray-200 mb-4">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Target },
              { id: 'strengths', label: 'Strengths', icon: CheckCircle },
              { id: 'improvements', label: 'Improvements', icon: AlertTriangle },
              { id: 'enhancements', label: 'Enhancements', icon: Lightbulb },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">AI Reasoning</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-2">Skills Match</h5>
                    <p className="text-sm text-blue-700">{matchResults.reasoning.skills_match}</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h5 className="font-medium text-green-900 mb-2">Experience Alignment</h5>
                    <p className="text-sm text-green-700">{matchResults.reasoning.experience_alignment}</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h5 className="font-medium text-purple-900 mb-2">Project Relevance</h5>
                    <p className="text-sm text-purple-700">{matchResults.reasoning.project_relevance}</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h5 className="font-medium text-orange-900 mb-2">Bonus Factors</h5>
                    <p className="text-sm text-orange-700">{matchResults.reasoning.bonus_factors}</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Learning Resources</h4>
                <div className="space-y-2">
                  {matchResults.learning_resources.map((resource, index) => (
                    <a
                      key={index}
                      href={resource.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <BookOpen className="w-4 h-4 text-primary-600" />
                      <span className="text-sm text-gray-700">{resource.topic}</span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'strengths' && (
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Candidate Strengths</h4>
              <div className="space-y-3">
                {matchResults.strengths.map((strength, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-success-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-success-600 mt-0.5" />
                    <span className="text-success-800">{strength}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'improvements' && (
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Areas for Improvement</h4>
              <div className="space-y-3">
                {matchResults.missing.map((improvement, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-warning-50 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-warning-600 mt-0.5" />
                    <span className="text-warning-800">{improvement}</span>
                  </div>
                ))}
              </div>

              <div className="mt-6">
                <h5 className="text-md font-semibold text-gray-900 mb-3">Skill Gap Suggestions</h5>
                <div className="space-y-2">
                  {matchResults.skill_gap_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
                      <span className="text-blue-800">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'enhancements' && enhancedResume && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Enhanced Bullet Points</h4>
                <div className="space-y-3">
                  {enhancedResume.enhanced_bullet_points.map((bullet, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-success-50 rounded-lg">
                      <TrendingUp className="w-5 h-5 text-success-600 mt-0.5" />
                      <span className="text-success-800">{bullet}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="text-md font-semibold text-gray-900 mb-3">Power Verbs</h5>
                  <div className="flex flex-wrap gap-2">
                    {enhancedResume.power_verbs.map((verb, index) => (
                      <span key={index} className="skill-tag-success">
                        {verb}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h5 className="text-md font-semibold text-gray-900 mb-3">Quantified Achievements</h5>
                  <div className="space-y-2">
                    {enhancedResume.quantified_achievements.map((achievement, index) => (
                      <div key={index} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                        {achievement}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <h5 className="text-md font-semibold text-gray-900 mb-3">Skill Improvements</h5>
                <div className="space-y-2">
                  {enhancedResume.skill_improvements.map((skill, index) => (
                    <div key={index} className="flex items-start space-x-3 p-2 bg-blue-50 rounded">
                      <Lightbulb className="w-4 h-4 text-blue-600 mt-0.5" />
                      <span className="text-sm text-blue-800">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="text-md font-semibold text-gray-900 mb-3">Formatting Suggestions</h5>
                <div className="space-y-2">
                  {enhancedResume.formatting_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-3 p-2 bg-purple-50 rounded">
                      <BookOpen className="w-4 h-4 text-purple-600 mt-0.5" />
                      <span className="text-sm text-purple-800">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default AnalysisResults; 