import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import {
  Institution,
  CurrentPositionAnalysis,
  TrajectoryAnalysis,
  StrategicIntelligenceAnalysis,
  StrategicOptionsAnalysis,
  StrategicPlan,
  ExecutionReview,
} from './api/types';

import { AgentHeader } from './components/header/AgentHeader';
import { VignanHeader } from './components/header/VignanHeader';
import { AgentHero } from './components/hero/AgentHero';
import { PipelineStages } from './components/pipeline/PipelineStages';
import { WorkspaceTabs } from './components/navigation/WorkspaceTabs';
import { HighlightsPanel } from './components/highlights/HighlightsPanel';

import { RobotConstellationStage } from './components/chat/RobotConstellationStage';
import { AgenticChatCard } from './components/chat/AgenticChatCard';
import { EventHighlightsPanel } from './components/highlights/EventHighlightsPanel';

import { OverviewDashboard } from './components/overview/OverviewDashboard';
import { CurrentPositionView } from './components/position/CurrentPositionView';
import { TrajectoryView } from './components/trajectory/TrajectoryView';
import { StrategicIntelligenceView } from './components/intelligence/StrategicIntelligenceView';
import { StrategicOptionsView } from './components/options/StrategicOptionsView';
import { StrategicPlanView } from './components/plan/StrategicPlanView';
import { ExecutionReviewView } from './components/review/ExecutionReviewView';

import { LoadingState } from './components/common/LoadingState';
import { ErrorState } from './components/common/ErrorState';
import { EmptyState } from './components/common/EmptyState';
import { ErrorBoundary } from './components/common/ErrorBoundary';

export const App: React.FC = () => {
  // Navigation & Global Context
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedInstitutionId, setSelectedInstitutionId] = useState<string>('');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('2024-2025');
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [isStrategicView, setIsStrategicView] = useState<boolean>(false);

  // Backend Snapshots
  const [currentPosition, setCurrentPosition] = useState<CurrentPositionAnalysis | null>(null);
  const [trajectory, setTrajectory] = useState<TrajectoryAnalysis | null>(null);
  const [intelligence, setIntelligence] = useState<StrategicIntelligenceAnalysis | null>(null);
  const [options, setOptions] = useState<StrategicOptionsAnalysis | null>(null);
  const [plan, setPlan] = useState<StrategicPlan | null>(null);
  const [latestReview, setLatestReview] = useState<ExecutionReview | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial Load: Institutions
  useEffect(() => {
    const fetchInstitutions = async () => {
      try {
        const list = await api.getInstitutions();
        setInstitutions(list);
        if (list.length > 0) {
          // Prefer Vignan's University or primary demo institution
          const preferred = list.find((i) => i.name.toLowerCase().includes('vignan') || i.code.includes('VIGNAN') || i.code.includes('DEMO') || i.code.includes('APEX'));
          setSelectedInstitutionId(preferred ? preferred.id : list[0].id);
        } else {
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Failed to load institutions:', err);
        setError('Unable to load registered institutions. Ensure the Agent 72 backend is online at http://localhost:8000.');
        setIsConnected(false);
        setIsLoading(false);
      }
    };
    fetchInstitutions();
  }, []);

  // 2. Load Snapshots when Institution or Period changes
  useEffect(() => {
    if (!selectedInstitutionId) return;

    const fetchAllSnapshots = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [posList, trajList, intelList, optList, planList] = await Promise.all([
          api.getCurrentPositions(selectedInstitutionId, selectedPeriod),
          api.getTrajectories(selectedInstitutionId, selectedPeriod),
          api.getStrategicIntelligence(selectedInstitutionId, selectedPeriod),
          api.getStrategicOptions(selectedInstitutionId, selectedPeriod),
          api.getPlans(selectedInstitutionId),
        ]);

        let pos = posList.length > 0 ? posList[0] : null;
        let traj = trajList.length > 0 ? trajList[0] : null;
        let intel = intelList.length > 0 ? intelList[0] : null;
        let opt = optList.length > 0 ? optList[0] : null;
        const pl = planList.length > 0 ? planList[0] : null;

        // Graceful fallback if specific period entry is absent
        if (!pos) {
          const fallbackPos = await api.getCurrentPositions(selectedInstitutionId);
          if (fallbackPos.length > 0) pos = fallbackPos[0];
        }
        if (!traj) {
          const fallbackTraj = await api.getTrajectories(selectedInstitutionId);
          if (fallbackTraj.length > 0) traj = fallbackTraj[0];
        }
        if (!intel) {
          const fallbackIntel = await api.getStrategicIntelligence(selectedInstitutionId);
          if (fallbackIntel.length > 0) intel = fallbackIntel[0];
        }
        if (!opt) {
          const fallbackOpt = await api.getStrategicOptions(selectedInstitutionId);
          if (fallbackOpt.length > 0) opt = fallbackOpt[0];
        }

        setCurrentPosition(pos);
        setTrajectory(traj);
        setIntelligence(intel);
        setOptions(opt);
        setPlan(pl);

        // Fetch review if plan exists
        if (pl?.id) {
          try {
            const rev = await api.getLatestExecutionReview(pl.id);
            setLatestReview(rev);
          } catch {
            // Check if plan has reviews array embedded
            if (pl.execution_reviews && pl.execution_reviews.length > 0) {
              setLatestReview(pl.execution_reviews[pl.execution_reviews.length - 1]);
            } else {
              setLatestReview(null);
            }
          }
        } else {
          setLatestReview(null);
        }

        setIsConnected(true);
      } catch (err: any) {
        console.error('Failed loading strategic snapshots:', err);
        setError('Failed connecting to Agent 72 analytical APIs. Please retry.');
        setIsConnected(false);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllSnapshots();
  }, [selectedInstitutionId, selectedPeriod]);

  // Tab View Dispatcher
  const renderActiveView = () => {
    if (error) {
      return (
        <ErrorState
          message={error}
          onRetry={() => {
            setError(null);
            setIsLoading(true);
            setSelectedInstitutionId((prev) => `${prev}`);
          }}
        />
      );
    }

    if (isLoading) {
      return <LoadingState message="Loading institutional strategic data..." />;
    }

    if (institutions.length === 0) {
      return (
        <EmptyState
          title="No Registered Institutions Found"
          description="The database currently has no registered institutional records. Ensure the Agent 72 backend and database are initialized."
        />
      );
    }

    switch (activeTab) {
      case 'overview':
        return (
          <OverviewDashboard
            currentPosition={currentPosition}
            trajectory={trajectory}
            intelligence={intelligence}
            options={options}
            plan={plan}
            latestReview={latestReview}
            onNavigateTab={setActiveTab}
          />
        );
      case 'position':
        return <CurrentPositionView analysis={currentPosition} />;
      case 'trajectory':
        return <TrajectoryView analysis={trajectory} />;
      case 'intelligence':
        return <StrategicIntelligenceView analysis={intelligence} />;
      case 'options':
        return <StrategicOptionsView analysis={options} />;
      case 'plan':
        return <StrategicPlanView plan={plan} />;
      case 'review':
        return <ExecutionReviewView review={latestReview} />;
      default:
        return (
          <OverviewDashboard
            currentPosition={currentPosition}
            trajectory={trajectory}
            intelligence={intelligence}
            options={options}
            plan={plan}
            latestReview={latestReview}
            onNavigateTab={setActiveTab}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col">
      {/* Vignan Header matching reference screenshot */}
      <VignanHeader
        institutions={institutions}
        selectedInstitutionId={selectedInstitutionId}
        onSelectInstitution={setSelectedInstitutionId}
        selectedPeriod={selectedPeriod}
        onSelectPeriod={setSelectedPeriod}
        onToggleStrategicView={() => {
          if (activeTab === 'ask') setActiveTab('overview');
          setIsStrategicView(!isStrategicView);
        }}
        isStrategicView={isStrategicView}
      />

      {isStrategicView ? (
        /* Strategic Governance Workspace View */
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Side: Primary Agent 72 Workspace (68% ~ 8 cols) */}
            <div className="lg:col-span-8 space-y-5">
              <AgentHero />
              <PipelineStages activeTab={activeTab} onSelectTab={setActiveTab} />
              <WorkspaceTabs activeTab={activeTab} onSelectTab={setActiveTab} />
              <div className="pt-2">
                <ErrorBoundary fallbackTitle="Strategic Workspace Error">
                  {renderActiveView()}
                </ErrorBoundary>
              </div>
            </div>

            {/* Right Side: Highlights Panel (32% ~ 4 cols) */}
            <div className="lg:col-span-4 lg:sticky lg:top-20">
              <ErrorBoundary fallbackTitle="Highlights Panel Error">
                <HighlightsPanel
                  currentPosition={currentPosition}
                  trajectory={trajectory}
                  intelligence={intelligence}
                  options={options}
                  activePlan={plan}
                  latestReview={latestReview}
                  onNavigateTab={setActiveTab}
                />
              </ErrorBoundary>
            </div>
          </div>
        </main>
      ) : (
        /* Flagship Interface matching user's exact reference screenshot */
        <main className="flex-1 max-w-[1500px] mx-auto w-full px-4 sm:px-6 py-5">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left Column (approx 60% ~ 7 cols): Robot Constellation Stage + Agentic Chat Card */}
            <div className="lg:col-span-7 space-y-4">
              <RobotConstellationStage />
              <AgenticChatCard
                institutionId={selectedInstitutionId}
                period={selectedPeriod}
              />
            </div>

            {/* Right Column (approx 40% ~ 5 cols): Highlights Panel */}
            <div className="lg:col-span-5">
              <EventHighlightsPanel />
            </div>
          </div>
        </main>
      )}
    </div>
  );
};

export default App;
