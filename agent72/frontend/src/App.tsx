import React, { useEffect, useState, useCallback } from 'react';
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

import { VignanHeader } from './components/header/VignanHeader';
import { AgentHero } from './components/hero/AgentHero';
import { PipelineStages } from './components/pipeline/PipelineStages';
import { WorkspaceTabs } from './components/navigation/WorkspaceTabs';
import { HighlightsPanel } from './components/highlights/HighlightsPanel';

import { OverviewDashboard } from './components/overview/OverviewDashboard';
import { StrategicIntelligenceView } from './components/intelligence/StrategicIntelligenceView';
import { StrategicOptionsView } from './components/options/StrategicOptionsView';
import { StrategicPlanView } from './components/plan/StrategicPlanView';
import { ExecutionReviewView } from './components/review/ExecutionReviewView';
import { AskAgent72View } from './components/chat/AskAgent72View';
import { FloatingAgentBeacon } from './components/chat/FloatingAgentBeacon';

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
          // Prefer Vignan's University with Phase 8 data or primary demo institution
          const preferred =
            list.find((i) => i.code === 'DEMO-VIGNAN-P8') ||
            list.find((i) => i.code === 'DEMO-VIGNAN') ||
            list.find((i) => i.code === 'VIGNAN-P8') ||
            list.find((i) => i.name.toLowerCase().includes('vignan')) ||
            list[0];
          setSelectedInstitutionId(preferred ? preferred.id : list[0].id);
        } else {
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Failed to load institutions:', err);
        setError('Unable to load registered institutions. Ensure the Agent 72 backend is online.');
        setIsConnected(false);
        setIsLoading(false);
      }
    };
    fetchInstitutions();
  }, []);

  // 2. Fetch all analytical snapshots for institution & period
  const fetchAllSnapshots = useCallback(async () => {
    if (!selectedInstitutionId) return;

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

      // Fallbacks if specific period entry is absent
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

      // Find plan with active execution review if available
      let pl: StrategicPlan | null = null;
      let rev: ExecutionReview | null = null;

      const activePlans = planList.filter((p) => p.status === 'ACTIVE');
      const candidatePlans = activePlans.length > 0 ? activePlans : planList;

      for (const candidatePlan of candidatePlans) {
        try {
          const fetchedRev = await api.getLatestExecutionReview(candidatePlan.id);
          if (fetchedRev) {
            pl = candidatePlan;
            rev = fetchedRev;
            break;
          }
        } catch {
          if (candidatePlan.execution_reviews && candidatePlan.execution_reviews.length > 0) {
            pl = candidatePlan;
            rev = candidatePlan.execution_reviews[candidatePlan.execution_reviews.length - 1];
            break;
          }
        }
      }

      if (!pl && planList.length > 0) {
        pl = candidatePlans[0] || planList[0];
      }

      // If pl exists but no review found for it, check if any other plan has a review
      if (pl && !rev) {
        for (const otherPlan of planList) {
          try {
            const fetchedRev = await api.getLatestExecutionReview(otherPlan.id);
            if (fetchedRev) {
              rev = fetchedRev;
              break;
            }
          } catch {}
        }
      }

      setCurrentPosition(pos);
      setTrajectory(traj);
      setIntelligence(intel);
      setOptions(opt);
      setPlan(pl);
      setLatestReview(rev);

      setIsConnected(true);
    } catch (err: any) {
      console.error('Failed loading strategic snapshots:', err);
      setError('Failed connecting to Agent 72 analytical APIs. Please retry.');
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  }, [selectedInstitutionId, selectedPeriod]);

  useEffect(() => {
    fetchAllSnapshots();
  }, [fetchAllSnapshots]);

  // Tab View Dispatcher
  const renderActiveView = () => {
    if (error) {
      return <ErrorState message={error} onRetry={fetchAllSnapshots} />;
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
      case 'intelligence':
        return <StrategicIntelligenceView analysis={intelligence} />;
      case 'options':
        return <StrategicOptionsView analysis={options} />;
      case 'plan':
        return <StrategicPlanView plan={plan} />;
      case 'review':
        return <ExecutionReviewView review={latestReview} />;
      case 'ask':
        return (
          <AskAgent72View
            institutionId={selectedInstitutionId}
            period={selectedPeriod}
          />
        );
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

  const isAskTab = activeTab === 'ask';

  return (
    <div className="min-h-screen bg-main-bg text-primary-text flex flex-col font-sans">
      {/* Vignan CSE Presents / Agentic AI Day 2026 Header */}
      <VignanHeader
        institutions={institutions}
        selectedInstitutionId={selectedInstitutionId}
        onSelectInstitution={setSelectedInstitutionId}
        selectedPeriod={selectedPeriod}
        onSelectPeriod={setSelectedPeriod}
        isConnected={isConnected}
        onRefresh={fetchAllSnapshots}
        onOpenAskAgent={() => setActiveTab('ask')}
        activeTab={activeTab}
      />

      {/* Main Strategic Dashboard: Desktop 68% / 32% Layout (Full 100% width for Ask Agent 72) */}
      <main className="flex-1 max-w-[1600px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Primary Workspace (12 cols on Ask Agent 72 for maximum chatbox width; 8 cols on other tabs) */}
          <div className={`${isAskTab ? 'lg:col-span-12' : 'lg:col-span-8'} space-y-6`}>
            <AgentHero />
            <PipelineStages activeTab={activeTab} onSelectTab={setActiveTab} />
            <WorkspaceTabs activeTab={activeTab} onSelectTab={setActiveTab} />
            <div className="pt-1">
              <ErrorBoundary fallbackTitle="Strategic Workspace Error">
                {renderActiveView()}
              </ErrorBoundary>
            </div>
          </div>

          {/* Independently Scrollable Strategic Highlights Panel (32% ~ 4 cols) - Removed ONLY for Ask Agent 72 */}
          {!isAskTab && (
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
          )}
        </div>
      </main>

      {/* Special Floating Agent 72 Quick-Launch Beacon */}
      <FloatingAgentBeacon
        activeTab={activeTab}
        onOpenAskAgent={() => setActiveTab('ask')}
      />
    </div>
  );
};

export default App;
