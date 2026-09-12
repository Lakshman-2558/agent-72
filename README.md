# Agent 72: Strategic Planning Agent

Agent 72 is an institutional strategic planning agent that provides evidence-based trajectory analysis, strategic options generation, scenario modeling, prioritization, measurable planning, execution tracking, and annual review.

---

## 1. Architectural Overview & Flow

Agent 72 enforces strict Clean Architecture boundaries and a canonical data flow:

```
                 ┌──────────────────────┐
                 │ Institutional Context│
                 │ Institution / Units  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Metric Definitions   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Institutional        │
                 │ Evidence             │
                 │ + Provenance         │
                 │ + Time Series        │
                 └──────────┬───────────┘
                            │
     Future Agents ─────────┘
     (Ingestion Boundary)   │
                            ▼
                 ┌──────────────────────┐
                 │ Strategic Planning   │
                 │ Engine (later)       │
                 └──────────┬───────────┘
                            ▼
                     Strategic Options
                            ▼
                        Scenarios
                            ▼
                     Strategic Plan
                            ▼
                       Objectives
                            ▼
                       Initiatives
                            ▼
                       Milestones
                            ▼
                       Execution
                            ▼
                         Review
```

### Layered Separation
- **`agent72/domain/`**: Pure entities (`Institution`, `OrganizationalUnit`, `MetricDefinition`, `InstitutionalEvidence`, `StrategicPlan`, `PlanObjective`, `PlanInitiative`, `InitiativeMilestone`, `ExecutionReview`) and repository contracts (`IOrganizationRepository`, `IEvidenceRepository`, `IPlanRepository`, `IAIProvider`).
- **`agent72/application/`**: Data Transfer Objects (`EvidenceIngestionDTO`, `EvidenceBatchIngestionDTO`, etc.) and use case services (`OrganizationService`, `EvidenceService`, `StrategicPlanService`, `HealthService`).
- **`agent72/infrastructure/`**: SQLAlchemy 2.0 ORM models, Alembic migrations, concrete repositories, and deterministic AI provider mock.
- **`agent72/api/`**: FastAPI routers (`/api/v1/health`, `/api/v1/organizations`, `/api/v1/evidence`, `/api/v1/plans`), request context middleware, and structured error handlers.
- **`agent72/core/`**: Pydantic settings, structured logging, and exceptions.

---

## 2. Canonical Institutional Data Model (Phase 2)

### A. Institutional Context
- **`institutions`**: Represents the university or college (`id`, `code`, `name`, `institution_type`, `status`).
- **`organizational_units`**: Departments, schools, faculties, or centers (`id`, `institution_id`, `code`, `name`, `unit_type`, `status`, `parent_unit_id`).

### B. Metric Definitions & Time-Series Evidence
- **`metric_definitions`**: Catalogue of institutional indicators (`metric_key`, `name`, `domain`, `default_unit`, `description`).
- **`institutional_evidence`**: Time-series measurements with comprehensive provenance:
  - **Domains**: Academic Performance, Admissions & Market, Placement & Employer Demand, Research, Faculty Capability, Infrastructure, Finance, External/Regulatory, Peer & Competitor.
  - **Provenance**: `source_type` (`AGENT`, `EXTERNAL`, `MANUAL`), `source_name` (e.g. `"Agent 20"`, `"Agent 38"`, `"NIRF 2024"`), `source_reference`, `captured_at`, `as_of_date`, `confidence_score` (0.0 to 1.0), `quality_tier` (`VERIFIED`, `ESTIMATED`, `PROVISIONAL`), `is_stale`.
  - **Temporal Scope**: Canonical academic period e.g. `"2024-2025"` or `"2024-Q1"`.

### C. Strategic Planning & Execution
- **`strategic_plans`**: Master institutional plan (`institution_id`, `title`, `horizon_start_year`, `horizon_end_year`, `existing_commitments`, `review_period`, `status`).
- **`plan_objectives`**: Measurable targets linked to indicators (`metric_key`, `target_period`, `baseline_value`, `target_value`, `weight`, `owner`).
- **`plan_initiatives`**: Programs executing an objective (`budget`, `owner`, `status`, `start_date`, `end_date`).
- **`initiative_milestones`**: Key checkpoints within initiatives (`target_date`, `status`, `completion_date`).
- **`strategic_options`**: Evaluated options (`rationale`, `resource_intensity`, `risk_level`, `estimated_cost`).
- **`plan_scenarios`**: Future projections (`assumptions`, `projected_outcome`).
- **`execution_reviews`**: Annual/periodic progress review (`period`, `review_date`, `progress_summary`, `variance_notes`, `recommendations`).

---

## 3. Canonical Evidence Ingestion Pipeline (Phase 3)

Agent 72 provides a robust, production-grade canonical data engineering pipeline designed to ingest evidence from multiple external source agents and manual inputs without coupling to external agent databases or schemas.

```
                 External Sources
                       │
          ┌────────────┴────────────┐
          │ Agent 20/38/49/50/71/.. │
          └────────────┬────────────┘
                       │
                       ▼
              Canonical DTO
                       │
                       ▼
             ┌─────────────────┐
             │ Validation      │
             ├─────────────────┤
             │ Normalization   │
             ├─────────────────┤
             │ Idempotency     │
             ├─────────────────┤
             │ Provenance      │
             └────────┬────────┘
                      │
             ┌────────▼────────┐
             │ Evidence Store  │
             │ Immutable       │
             │ Time Series     │
             └────────┬────────┘
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       Latest      Historical   Domain/
       Evidence      Series     Filters
          │           │            │
          └───────────┼────────────┘
                      ▼
          EvidenceFreshnessService
                      │
                      ▼
             Dynamic Freshness
           (FRESH / AGING / STALE)
```

### Core Pipeline Capabilities
1. **Validation & Institutional Scope**:
   - Rejects submissions for non-existent institutions or unauthorized departments.
   - Enforces valid academic periods (`YYYY-YYYY`, `YYYY-YY`, `YYYY-Q#`, `YYYY`) and verified metric definitions.
2. **Canonical Normalization**:
   - **Metric Keys**: Lowercased, whitespace-trimmed, non-alphanumerics normalized to dot notation (e.g. `"  RESEARCH.publications_q1 "` → `"research.publications.q1"`).
   - **Domains**: Flexible synonym mapping (e.g. `"research"` → `"RESEARCH_PRODUCTIVITY"`, `"admissions"` → `"ADMISSIONS_MARKET"`).
   - **Units**: Canonical unit mapping (e.g. `"%"`, `"pct"` → `"percent"`, `"cnt"` → `"count"`).
   - **Periods**: Standardizes academic year spans (e.g. `"2024-25"` → `"2024-2025"`).
3. **Deterministic Idempotency (Safe Fingerprinting)**:
   - If `external_record_id` is supplied: `idempotency_key = sha256(source_name:external_record_id)`.
   - Fallback fingerprint: `sha256(source_name:institution_id:unit_id:metric_key:normalized_value:period:as_of_date)`.
   - Incorporating normalized value prevents false-positive duplicate collisions when multiple observations arrive for the same metric/period.
4. **Ingestion Batch Traceability & Audit Logs**:
   - Every ingested evidence item records its `ingestion_batch_id`.
   - Ingestion batches record audit statistics in `ingestion_batch_logs` (`received_count`, `inserted_count`, `duplicate_count`, `rejected_count`, `error_summary`).
5. **No Silent Metric Invention**:
   - `auto_register_metrics = False` by default.
   - When enabled, strictly requires complete metadata (`display_name`, `domain`, `unit`, `description`) or the record is rejected.
6. **Dynamic Query-Time Freshness**:
   - Freshness (`FRESH`, `AGING`, `STALE`) is never statically persisted in the database; it is computed dynamically by `EvidenceFreshnessService` at query time based on `as_of_date` and domain-specific thresholds.
7. **Configuration-Driven Thresholds**:
   - Freshness thresholds configured via `agent72/core/config.py` (`Admissions: 90d`, `Research: 365d`, `Finance: 365d`, `Operations: 30d`, etc.) overridable via environment variables.
8. **Evidence Immutability**:
   - Historical time-series observations are never overwritten by new observations; multiple observations over academic periods form an immutable historical record.
9. **Safe Pagination**:
   - Default page size: 50, maximum limit: 500 on all evidence listing endpoints.

---

### Ingestion Contract Examples

#### Example 1: Agent 71 KPI Evidence
```json
POST /api/v1/evidence/ingest
{
  "institution_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "metric_key": "academic.retention_rate",
  "domain": "ACADEMIC_PERFORMANCE",
  "numeric_value": 89.2,
  "unit": "percent",
  "period": "2024-2025",
  "source_type": "AGENT",
  "source_name": "Agent 71",
  "source_reference": "run-kpi-batch-2024-09",
  "confidence_score": 0.98,
  "quality_tier": "VERIFIED",
  "external_record_id": "agent71-kpi-retention-2024-25"
}
```

#### Example 2: Agent 20 Research Evidence
```json
POST /api/v1/evidence/ingest
{
  "institution_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "metric_key": "research.citations.scopus",
  "domain": "RESEARCH_PRODUCTIVITY",
  "numeric_value": 3420.0,
  "unit": "count",
  "period": "2024-2025",
  "source_type": "AGENT",
  "source_name": "Agent 20",
  "source_reference": "scopus-extract-2024-q3",
  "confidence_score": 0.95,
  "quality_tier": "VERIFIED",
  "external_record_id": "agent20-rec-scopus-3420"
}
```

#### Example 3: Manual Institutional Evidence
```json
POST /api/v1/evidence/ingest
{
  "institution_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "metric_key": "finance.operating_margin",
  "domain": "FINANCE_RESOURCES",
  "numeric_value": 14.8,
  "unit": "percent",
  "period": "2024-2025",
  "source_type": "MANUAL",
  "source_name": "Finance Office Audit Report",
  "source_reference": "FY24-AUDIT-FINAL.pdf",
  "confidence_score": 1.0,
  "quality_tier": "VERIFIED"
}
```

---

## 4. Current Institutional Position Analysis (Phase 4)

Agent 72 provides a 100% deterministic, evidence-based Current Institutional Position Analysis engine. It evaluates institutional performance across registered indicators, isolates data quality deficiencies, and generates immutable strategic position snapshots.

### Core Analysis Capabilities
1. **Metric Directionality / Polarity**:
   - `MetricDefinition.direction`: `HIGHER_IS_BETTER`, `LOWER_IS_BETTER`, `TARGET_RANGE`, `NEUTRAL`.
   - Polarity-aware performance interpretation:
     - `HIGHER_IS_BETTER`: increase = positive performance, decrease = negative performance.
     - `LOWER_IS_BETTER`: decrease = positive performance, increase = negative performance (e.g. dropout rate).
2. **Meaningful Change / Significance Handling**:
   - Configurable threshold (`MIN_SIGNIFICANT_CHANGE_PERCENT = 2.0` by default).
   - Minor fluctuations (e.g. `81.0% → 81.2%`) are not misclassified as strategic strengths.
3. **Deterministic Observation Selection (5-Level Tie-Breaking)**:
   - When multiple observations exist for the same period:
     1. Quality tier priority (`VERIFIED` > `ESTIMATED` > `PROVISIONAL`)
     2. Confidence score (descending)
     3. `as_of_date` (descending)
     4. `captured_at` (descending)
     5. Observation ID (lexicographical ascending for 100% determinism)
4. **Target & Baseline Variance**:
   - Compares latest observation against previous historical observation, configured baselines, and active strategic plan targets.
   - If no valid comparison exists, explicitly returns `comparison_status = "comparison_unavailable"`.
5. **Data Gap Isolation**:
   - Missing evidence, stale observations, and provisional data are isolated into `data_gaps`.
   - Grounded in the principle: **"absence of evidence" ≠ "poor performance"**.
6. **Transparent Factor-Based Confidence**:
   - Scoring based on average evidence confidence, proportion of verified evidence, freshness index, and comparison availability, with penalties for high missing data rates.
7. **Snapshot Immutability**:
   - Persisted in `institutional_analyses` table as finalized, immutable historical snapshots with full traceability to underlying evidence UUIDs.

---

## 5. Institutional Trajectory Analysis (Phase 5)

Agent 72 extends institutional inquiry from *"Where are we now?"* to *"Where are we heading?"* through a 100% deterministic, multi-period trajectory analysis engine.

```
Historical Canonical Evidence
            │
            ▼
┌───────────────────────────────────────┐
│     Trajectory Analysis Engine        │
│                                       │
│ • Chronological Multi-Period Series   │
│ • Polarity-Aware Trend Direction      │
│ • Magnitude (Absolute & Percent)      │
│ • Sign Consistency (HIGH/MOD/LOW)     │
│ • Volatility (Std Dev of Changes)     │
│ • Acceleration / Deceleration         │
│ • Data Limitations (< 2 observations) │
│ • Factor-Based Transparent Confidence │
└───────────────────┬───────────────────┘
                    │
   Current Position │ (Synthesis)
       Snapshot ────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│     Structured Trajectory Signals     │
│                                       │
│ • "Improving but below target"        │
│ • "Declining and below target"        │
│ • "Compounding strength"              │
│ • "Vulnerable strength"               │
│ • "Recovering from weakness"          │
│ • "Persistent negative trajectory"    │
└───────────────────────────────────────┘
```

### Core Trajectory Principles & Calculations
1. **Observation Depth Thresholds**:
   - `0 or 1 observation`: Strictly classified as `TrajectoryStatus.INSUFFICIENT_DATA` and recorded in `data_limitations`. Never treated as a trend or poor performance.
   - `2 observations`: Evaluates basic directional movement against `MIN_SIGNIFICANT_CHANGE_PERCENT = 2.0%`. Consistency and acceleration are flagged `INSUFFICIENT_DATA`.
   - `3+ observations`: Full period-to-period change series ($\Delta_i$), sign consistency rating (`HIGH`, `MODERATE`, `LOW`), sample volatility ($s$), and second-order acceleration ($a = \Delta_{recent} - \Delta_{prior}$).
2. **Polarity-Aware Trend Status**:
   - `HIGHER_IS_BETTER`: Positive change = `IMPROVING`, negative change = `DECLINING`.
   - `LOWER_IS_BETTER`: Negative change = `IMPROVING`, positive change = `DECLINING` (e.g. dropout rate).
   - `TARGET_RANGE` & `NEUTRAL`: Purely descriptive; movement within threshold = `STABLE`.
3. **Transparent Volatility & Volatile Classification**:
   - Sample standard deviation of period-to-period differences: $s = \sqrt{\frac{1}{N-1} \sum (\Delta_i - \bar{\Delta})^2}$.
   - Metrics with large alternating direction reversals and $s > 15.0$ are classified as `TrajectoryStatus.VOLATILE`.
4. **Second-Order Momentum (Acceleration / Deceleration)**:
   - Evaluates whether rate of improvement is speeding up (`ACCELERATING`), slowing down (`DECELERATING`), or constant (`CONSTANT_VELOCITY`).
5. **Synthesis with Current Position (Trajectory Signals)**:
   - When coupled with a Current Position Analysis snapshot, generates structured diagnostic combinations without making prescriptive strategic recommendations:
     - *Target Gap + Improving Trajectory* $\rightarrow$ `"Improving but below target"`
     - *Target Gap + Declining Trajectory* $\rightarrow$ `"Declining and below target"`
     - *Strength + Improving Trajectory* $\rightarrow$ `"Compounding strength"`
     - *Strength + Declining Trajectory* $\rightarrow$ `"Vulnerable strength"`
     - *Weakness + Improving Trajectory* $\rightarrow$ `"Recovering from weakness"`
     - *Weakness + Declining Trajectory* $\rightarrow$ `"Persistent negative trajectory"`
6. **Immutable Snapshot Persistence**:
   - Persisted in `institutional_trajectory_analyses` table as finalized historical snapshots with complete traceability to underlying evidence UUIDs.

---

---

## 6. Strategic Intelligence: Risks, Constraints & External Environment (Phase 6)

Agent 72 transforms:
$$\text{Canonical Evidence} \longrightarrow \text{Phase 4 Current Position} \longrightarrow \text{Phase 5 Trajectory} \longrightarrow \mathbf{Phase\ 6\ Strategic\ Intelligence}$$

Answering:
*"What important strategic issues, risks, constraints, opportunities and external forces should leadership consider?"*

```
   Phase 4 Current Position ──────────┐
                                      ▼
   Phase 5 Trajectory Analysis ───────► Strategic Intelligence Synthesis Engine
                                      ▲  • Diagnostic Issues (Compounding Deficit, Vulnerable Strength)
   Canonical Evidence ────────────────┤  • Multi-Metric Structural Risks (with Correlation vs Causation)
   • Academic, Admissions, Placement  │  • Configuration-Driven Constraints (Capacity, PhD Ratio, Load)
   • Research, Faculty, Infra, Finance│  • External Factors (Freshness Penalties & Market Shifts)
   • Regulatory, Peer/Competitor      │  • Evidence-Backed Opportunities (No Prescriptive Actions)
                                      │  • Deterministic Transparent Risk Scoring (0.10 - 1.00)
                                      │  • Preliminary Priority Signals (Urgency x Impact x Confidence)
                                      │  • Transparent Uncertainty (Missing != Poor Performance)
                                      ▼
                      Immutable Strategic Intelligence Snapshot
                      (Persisted in institutional_strategic_intelligence_analyses)
```

### Core Strategic Intelligence Principles & Detection Logic
1. **Prerequisite Snapshots**:
   - Resolves Phase 4 Current Position and Phase 5 Trajectory snapshots via explicit IDs or matching `(institution_id, organizational_unit_id, analysis_period)`. Fails cleanly with descriptive validation error if prerequisites do not exist.
2. **Diagnostic Combinations (No Prescriptive Recommendations)**:
   - *Current Gap + Declining Trajectory* $\rightarrow$ `"Compounding deficit below target"`
   - *Current Gap + Improving Trajectory* $\rightarrow$ `"Narrowing deficit below target"`
   - *Current Strength + Declining Trajectory* $\rightarrow$ `"Vulnerable institutional strength"`
   - *Current Weakness + Declining Trajectory* $\rightarrow$ `"Persistent negative trajectory"`
3. **Multi-Metric Structural Risks & Correlation vs. Causation**:
   - Detects structural risks **only when multiple evidence signals corroborate them** (e.g. declining admissions yield + rising dropout rate; placement downturn + weakening employer hiring demand).
   - Every risk explicitly states: *"Observed concurrent movement indicates multi-domain vulnerability; correlation does not imply direct mechanistic causation without controlled longitudinal cohort validation."*
4. **Configuration-Driven Operational Constraints**:
   - Infrastructure utilization $\ge$ `settings.INFRASTRUCTURE_CAPACITY_THRESHOLD` ($85\%$) $\rightarrow$ `INFRASTRUCTURE_CAPACITY`.
   - Faculty PhD ratio $<$ `settings.FACULTY_PHD_MIN_THRESHOLD` ($70\%$) $\rightarrow$ `FACULTY_CAPABILITY`.
   - Student-Faculty ratio $\ge$ `settings.STUDENT_FACULTY_RATIO_THRESHOLD` ($18:1$) $\rightarrow$ `FACULTY_LOAD`.
   - **Critical Rule**: Never infer constraints from missing data! Missing data is isolated as a data limitation / uncertainty.
5. **External Environmental Factors & Freshness Penalties**:
   - Monitors `EXTERNAL_REGULATORY`, `PEER_COMPETITOR`, `ADMISSIONS_MARKET`, and `PLACEMENT_EMPLOYER_DEMAND`.
   - Stale observations ($> 365$ days old) receive a confidence penalty ($0.85\times$) and increment the uncertainty score.
6. **Deterministic, Transparent Risk Scoring**:
   - $\text{Score} = [(\text{Impact} \times 0.45) + (\text{Likelihood} \times 0.35) + (0.20 \times \text{Structural})] \times \text{Trajectory Multiplier} \times \text{Confidence Factor}$.
   - Trajectory Multiplier: $1.20\times$ if `DECLINING`, $1.15\times$ if `VOLATILE`, $0.85\times$ if `IMPROVING`.
   - Thresholds mapped to `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` with complete scoring rationale stored.
7. **Preliminary Priority Signals**:
   - Transparent urgency ranking for executive attention. Explicitly distinct from Phase 7 strategic options or final plan generation.
8. **AI Synthesis Guardrails**:
   - If `include_ai_synthesis=True`, AI may ONLY group and summarize already detected deterministic findings. The deterministic engine remains the sole source of truth; AI is strictly forbidden from altering scores, inventing evidence, or generating recommendations.
9. **Scope Isolation & Snapshot Immutability**:
   - Scoped strictly by `institution_id` and `organizational_unit_id`. Persisted in `institutional_strategic_intelligence_analyses` table with complete JSON audit trails.

---

## 7. Relational Database Strategy

- **Dual-Environment Support**:
  - **Local Development & Automated Tests**: SQLite (`sqlite:///./agent72.db` or `sqlite:///:memory:`). Foreign keys enforced on connect via `PRAGMA foreign_keys=ON;`.
  - **Production Deployment**: **Neon PostgreSQL**. Automated `pool_pre_ping=True` and connection recycling prevent stale idle disconnections.
- **Protocol Normalization**:
  - Cloud provider connection URLs starting with `postgres://` or `postgresql://` are automatically normalized to `postgresql+psycopg://`.
- **Zero SQLite Coupling**:
  - Schema uses vendor-agnostic DDL and indexes.
- **Secret Hygiene**:
  - Database credentials are kept in `.env` (ignored by `.gitignore`) and documented in `.env.example`.

---

## 8. Getting Started

### Installation
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
## 7. Strategic Options, Scenarios & Prioritization (Phase 7)

Agent 72 transforms:
$$\text{Strategic Intelligence} \longrightarrow \text{Strategic Options} \longrightarrow \text{Scenario Analysis} \longrightarrow \text{Option Evaluation} \longrightarrow \mathbf{Prioritized\ Options}$$

Answering:
*"What strategic choices are available, what could happen under different conditions, and which options appear most suitable for leadership consideration?"*

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Phase 6 Strategic Intelligence                    │
│                                                                        │
│ • Strategic Issues: Gaps, Declining Trajectories, Vulnerable Strengths │
│ • Structural Risks: Placement & Employer Contraction, Capacity Strain  │
│ • Binding Constraints: Lab Utilization (>85%), Faculty PhD (<70%)      │
│ • Emerging Opportunities: Research Momentum (+62.5% Publications)      │
│ • External Forces: AI Curriculum Mandates, Market & Demographic Shifts │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             Evidence-Grounded Strategic Options (3–8 Options)          │
│                                                                        │
│ • Alternative A: Curriculum Transformation & Experiential Learning     │
│ • Alternative B: Corporate Co-Op & Enterprise Internship Partnerships  │
│ • Capability Option: Phased Lab Modernization & Intelligent Space      │
│ • Growth Option: Research Innovation Cluster & Grant Accelerator       │
│ • Risk Mitigation Option: AI Ethics & Regulatory Compliance Framework  │
│ • Improvement Option: Admissions Yield Stabilization Program           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             Conditional Scenario Projections (4 per Option)            │
│                                                                        │
│ • BASELINE: Continuation under current external/institutional trends   │
│ • UPSIDE: Favorable external environment & accelerated internal uptake │
│ • DOWNSIDE: Plausible adverse headwinds, resistance & delayed impact   │
│ • STRESS: Severe macroeconomic/regulatory shocks & resource diversion  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             Deterministic 7-Dimension Option Evaluation                │
│                                                                        │
│ 1. Strategic Alignment (Weight: 0.20)                                  │
│ 2. Expected Impact (Weight: 0.20)                                      │
│ 3. Feasibility (Weight: 0.15)                                          │
│ 4. Resource Efficiency (Weight: 0.10)                                  │
│ 5. Implementation Risk Profile (Weight: 0.10 - higher score = less risk)│
│ 6. Urgency (Weight: 0.10)                                              │
│ 7. Evidence Strength (Weight: 0.15)                                    │
│                                                                        │
│ Formula: Total Score = Σ (Dimension_i × Weight_i)                      │
│ Priority: CRITICAL (>=85), HIGH (>=70), MEDIUM (>=50), LOW (<50)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Prioritized Decision-Support Recommendation              │
│                                                                        │
│ "Strategic options and priority signals are decision-support outputs.   │
│ Final strategic decisions remain with institutional leadership/bodies." │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-org/agent-72.git
cd agent-72

# Create virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

pip install -r requirements-dev.txt
cp .env.example .env
```

### Database Migrations
```bash
# Apply migrations to head
alembic upgrade head

# Rollback to baseline (if needed)
alembic downgrade 001_initial_schema
```

### Run the API Server
```bash
uvicorn agent72.main:app --host 0.0.0.0 --port 8000 --reload
```

---

---

## 8. Strategic Plan Generation & Execution Framework (Phase 8)

Agent 72 completes the institutional transformation pipeline:
$$\text{Canonical Evidence} \longrightarrow \text{Phase 4 Position} \longrightarrow \text{Phase 5 Trajectory} \longrightarrow \text{Phase 6 Intelligence} \longrightarrow \text{Phase 7 Options} \longrightarrow \mathbf{Phase\ 8\ Strategic\ Plan\ \&\ Execution}$$

Answering:
*"What should the strategic plan contain, how will success be measured, who owns each initiative, when should milestones occur, what dependencies exist, and how should execution progress be reviewed against evidence?"*

```
   Phase 7 Prioritized Options ───────┐
                                      ▼
   Leadership Option Selection ───────► Strategic Plan Generation Engine
                                      ▲  • Domain Clustering (Unified Objectives)
   Canonical Evidence & Metrics ──────┤  • Measurable Targets with Direction-Aware Gaps (Agent 71 Boundary)
   • MetricDefinition Directionality  │  • Explicit Percentage Points Notation for % Indicators
   • Real Unit Ownership Allocation   │  • Actionable Initiatives & Phased Milestones (2026-H1, 2026-H2)
                                      │  • Categorical Resource Uncertainty (LOW, MED, HIGH, UNKNOWN)
                                      │  • Leadership Governance Lifecycle (DRAFT -> APPROVED -> ACTIVE)
                                      │  • Mandatory Decision-Support Disclaimer on all artifacts
                                      ▼
                     ┌───────────────────────────────────────┐
                     │       Strategic Execution Plan        │
                     │                                       │
                     │ • Objectives & Canonical Targets      │
                     │ • Unit Owners & Dependencies          │
                     │ • Phased Milestone Deliverables       │
                     │ • Governance Decision Audit Trail     │
                     └───────────────────────────────────────┘
                                      │
                                      ▼
   Observed Execution Evidence ───────► Deterministic Execution Review Engine
                                         • Direction-Aware Variances (ON_TRACK, AT_RISK, OFF_TRACK)
                                         • Non-Punitive Missing Evidence (INSUFFICIENT_EVIDENCE)
                                         • Delayed Milestone Detection
                                         • Diagnostic Signals & Corrective Action Proposals
```

### Core Execution Principles
1. **Option Clustering & Unified Objectives**:
   - Groups related Phase 7 strategic options by strategic theme into cohesive, non-duplicative objectives with full upstream provenance.
2. **Measurable Targets & Agent 71 Linkage**:
   - Anchors targets directly to canonical `MetricDefinition` records.
   - For percentage metrics (`%`), variances and proposed gaps are explicitly formulated in **percentage points** (e.g. `+10.0 percentage points`).
   - If a metric definition is missing, Agent 72 sets `target_status = PROPOSED_WITHOUT_CANONICAL_DEFINITION` without inventing numbers.
3. **Actionable Initiatives & Unit Ownership**:
   - Assigns lead ownership to existing institutional departments (`Training & Placement`, `School of Engineering`, `Admissions Office`).
   - Milestones are scheduled across half-year operational cycles (`2026-H1`, `2026-H2`, `2027-H1`, `2028-H2`).
   - Resource requirements are classified categorically (`LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`). If specific cost estimates are unverified, Agent 72 uses `UNKNOWN` and notes the uncertainty rather than fabricating financial amounts.
4. **Leadership Decision Boundary**:
   - Plans initialize in `DRAFT` status. Only explicit leadership governance actions (`APPROVE`, `ACTIVATE`) promote the plan to active execution.
   - Mandatory disclaimer is embedded on every generated plan and review:
     > *"Strategic plans generated by Agent 72 are decision-support artifacts. Final approval, resource allocation and institutional strategy remain with institutional leadership/governing bodies."*
5. **Deterministic Execution Review**:
   - Evaluates performance against targets and schedules deterministically without LLM guesswork.
   - Missing observations are treated as `INSUFFICIENT_EVIDENCE` (data limitation) rather than operational failure.
   - Automatically formulates candidate corrective actions requiring leadership approval.

---

## 9. Running Tests

```bash
pytest tests -v
```

All **118 unit and integration tests** run against an in-memory SQLite database in ~8 seconds:
- **Phase 1 (Organizations & Baseline Plans)**: 12 tests passed
- **Phase 2 & 3 (Evidence Ingestion & Freshness)**: 18 tests passed
- **Phase 4 (Current Institutional Position)**: 14 tests passed
- **Phase 5 (Institutional Trajectory Analysis)**: 16 tests passed
- **Phase 6 (Strategic Intelligence)**: 17 tests passed
- **Phase 7 (Strategic Options & Prioritization)**: 24 tests passed
- **Phase 8 (Strategic Plan Generation & Execution Framework)**: 17 tests passed (13 unit + 4 integration)

### Demo Scripts

1. **Phase 8 Strategic Plan Generation & Execution Framework Demo (Complete 5-Stage Pipeline)**:
   ```bash
   python scripts/seed_demo_strategic_plan.py
   ```
   Runs multi-domain evidence seeding $\rightarrow$ Current Position $\rightarrow$ Trajectory $\rightarrow$ Strategic Intelligence $\rightarrow$ Strategic Options $\rightarrow$ **Leadership Selection** $\rightarrow$ **Plan Generation (Draft)** $\rightarrow$ **Governance Decision Lifecycle (APPROVE, ACTIVATE)** $\rightarrow$ **Observed Evidence Ingestion** $\rightarrow$ **Deterministic Execution Review**.

2. **Phase 7 Strategic Options & Prioritization Demo**:
   ```bash
   python scripts/seed_demo_strategic_options.py
   ```

3. **Phase 6 Strategic Intelligence Demo**:
   ```bash
   python scripts/seed_demo_strategic_intelligence.py
   ```

4. **Phase 5 Trajectory Demo**:
   ```bash
   python scripts/seed_demo_trajectory.py
   ```

---

## 10. Interactive API Documentation

Once the server is running:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Key Endpoints

| Category | Method | Path | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/v1/health` | Readiness probe (DB & AI provider) |
| | `GET` | `/api/v1/health/live` | Liveness probe |
| **Organizations**| `POST` | `/api/v1/organizations/institutions` | Register an institution |
| | `GET` | `/api/v1/organizations/institutions` | List institutions |
| | `POST` | `/api/v1/organizations/units` | Create department/unit under institution |
| | `GET` | `/api/v1/organizations/institutions/{id}/units` | List units of an institution |
| **Evidence & Catalog** | `POST` | `/api/v1/evidence/metrics` | Register a metric definition (with `direction`) |
| | `GET` | `/api/v1/evidence/metrics` | List metric definitions |
| | `POST` | `/api/v1/evidence/ingest` | Ingest single evidence record |
| | `POST` | `/api/v1/evidence/ingest/batch` | Bulk ingest evidence records with partial failure handling |
| | `GET` | `/api/v1/evidence` | Query time-series evidence records (paginated: default 50, max 500) |
| | `GET` | `/api/v1/evidence/series` | Query ordered historical time-series for a metric |
| | `GET` | `/api/v1/evidence/latest` | Retrieve latest recorded observation with dynamic freshness |
| | `GET` | `/api/v1/evidence/batches/{batch_id}` | Retrieve audit log for an ingestion batch |
| | `GET` | `/api/v1/evidence/batches` | List recent ingestion batch audit logs |
| **Current Position Analysis** | `POST` | `/api/v1/analysis/current-position` | Generate & persist deterministic current position analysis |
| | `GET` | `/api/v1/analysis/current-position/{analysis_id}` | Retrieve immutable current position snapshot by ID |
| | `GET` | `/api/v1/analysis/current-position` | List historical position analyses with filtering & pagination |
| **Institutional Trajectory Analysis** | `POST` | `/api/v1/analysis/trajectory` | Generate & persist multi-period trajectory analysis with position signals |
| | `GET` | `/api/v1/analysis/trajectory/{analysis_id}` | Retrieve immutable trajectory snapshot by ID |
| | `GET` | `/api/v1/analysis/trajectory` | List historical trajectory analyses with filtering & pagination |
| **Strategic Intelligence (Phase 6)** | `POST` | `/api/v1/analysis/strategic-intelligence` | Generate & persist strategic intelligence snapshot (issues, risks, constraints, opportunities) |
| | `GET` | `/api/v1/analysis/strategic-intelligence/{analysis_id}` | Retrieve immutable strategic intelligence snapshot by ID |
| | `GET` | `/api/v1/analysis/strategic-intelligence` | List historical strategic intelligence analyses with filtering & pagination |
| **Strategic Options & Prioritization (Phase 7)** | `POST` | `/api/v1/analysis/strategic-options` | Generate & persist strategic choices, 4 scenarios per option, 7-dimension evaluation, and prioritized recommendations |
| | `GET` | `/api/v1/analysis/strategic-options/{analysis_id}` | Retrieve immutable strategic options snapshot by ID |
| | `GET` | `/api/v1/analysis/strategic-options` | List historical strategic options analyses with filtering & pagination |
| **Strategic Plan Execution (Phase 8)** | `POST` | `/api/v1/plans/generate` | Generate draft strategic plan from Phase 7 prioritized options |
| | `POST` | `/api/v1/plans/{plan_id}/decision` | Record explicit leadership governance decision (`APPROVE`, `ACTIVATE`, etc.) |
| | `POST` | `/api/v1/plans/{plan_id}/review` | Run automated execution review for a period (variances, signals, corrective actions) |
| **Strategic Plans (Phase 1 Compatibility)** | `POST` | `/api/v1/plans` | Create manual plan (objectives, initiatives, milestones, scenarios) |
| | `GET` | `/api/v1/plans` | List plans (paginated with status/institution filters) |
| | `GET` | `/api/v1/plans/{id}` | Get plan with nested hierarchy |
| | `PUT` | `/api/v1/plans/{id}` | Update manual plan metadata |
| | `DELETE` | `/api/v1/plans/{id}` | Delete manual plan |
| | `POST` | `/api/v1/plans/{id}/reviews` | Record Phase 1 periodic manual execution review |

