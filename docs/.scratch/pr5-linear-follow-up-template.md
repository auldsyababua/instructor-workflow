# PR #5 Linear Follow-up Template (When Linear Configured)

**Status**: Template ready for Linear team configuration
**Use Case**: When Linear is enabled for the Instructor Workflow project

---

## Linear Issue Template

### Main Issue: Monitor PR #5 Grafana Baseline

**Issue ID**: TBD (When Linear configured)
**Title**: Monitor PR #5 Grafana baseline for 1 week

**Description**:
```
# Monitor PR #5 Grafana Baseline (1-Week Observation Period)

## Objective
Monitor the llm-guard-scanner-health dashboard for 7 days to establish baseline metrics and determine if threshold tuning is needed.

## Context
- PR #5 introduces Prometheus/Grafana observability for LLM Guard Scanner
- Grafana dashboard: `llm-guard-scanner-health.json`
- Baseline metrics needed before production deployment
- False positive rate target: < 5%

## Metrics to Monitor (Week 1: 2025-11-17 to 2025-11-24)
- **False Positive Rate**: Baseline tolerance (target < 2%)
- **False Negative Rate**: Expected 0%
- **Detection Rate**: Normal variation pattern
- **Check Duration (p95)**: Baseline latency for future alerts

## Acceptance Criteria
- [ ] Dashboard data displayed (no "No Data" after 3 minutes)
- [ ] Prometheus scraping operational (all targets UP)
- [ ] 7 days of continuous metrics collected
- [ ] Baseline thresholds documented
- [ ] No critical errors in metric collection

## Timeline
- **Start**: 2025-11-17 (PR #5 merged)
- **Week 1 End**: 2025-11-24 (Assessment phase)
- **Week 2**: Analyze baseline data
- **Week 3**: Tune thresholds if needed
- **Week 4**: Mark production-ready

## Next Steps
1. Import dashboard to Grafana
2. Add Prometheus datasource
3. Begin daily monitoring
4. Document findings on 2025-11-24

## References
- **Dashboard File**: `observability/grafana-dashboards/llm-guard-scanner-health.json`
- **Setup Guide**: `docs/.scratch/pr5-completion-summary.md`
- **PR**: #5 Enhanced Observability with Prometheus and Grafana
```

**Priority**: Medium
**Due Date**: 2025-11-24
**Labels**: `observability`, `monitoring`, `pr-followup`, `baseline`
**Estimated Hours**: 1 (monitoring only, no implementation)

---

## Child Issues (Sub-tasks)

### Child 1: Import Grafana Dashboard

**Title**: Import llm-guard-scanner-health dashboard to Grafana
**Description**: Complete the Grafana setup steps to enable monitoring
**Acceptance Criteria**:
- [ ] Prometheus datasource added to Grafana
- [ ] Dashboard JSON imported successfully
- [ ] Dashboard displays metrics (data appears within 3 minutes)
- [ ] All 4 panels show data:
  - Scanner Failure Rate (Last Hour)
  - Consecutive Failures
  - Total Failures (Last Hour)
  - Failure Rate by Error Type

**Estimated Hours**: 0.5

### Child 2: Establish Baseline Metrics (Week 1)

**Title**: Monitor and document baseline metrics for 1 week
**Description**: Collect 7 days of baseline data (2025-11-17 to 2025-11-24)
**Acceptance Criteria**:
- [ ] Daily dashboard check (no missing data)
- [ ] Prometheus targets remain UP (check targets page)
- [ ] Baseline values documented:
  - False positive rate (%): ___
  - False negative rate (%): ___
  - Detection rate (attacks/min): ___
  - Check duration p95 (ms): ___
- [ ] No scrape errors in Prometheus
- [ ] Results documented in comment by 2025-11-24

**Estimated Hours**: 0.5 (daily 5-minute checks)

### Child 3: Assess Baseline and Plan Adjustments (Week 2)

**Title**: Assess Week 1 baseline and determine threshold tuning needs
**Description**: Analyze collected metrics and decide if thresholds need adjustment
**Acceptance Criteria**:
- [ ] Week 1 baseline data analyzed
- [ ] False positive rate baseline documented
- [ ] Decision made: tuning needed or acceptable?
  - [ ] If < 5%: Proceed to Week 4 (production ready)
  - [ ] If >= 5%: Plan threshold tuning (proceed to Child 4)
- [ ] Assessment documented in comment

**Estimated Hours**: 1

### Child 4: Tune Thresholds (Week 3, Only If Needed)

**Title**: Tune Grafana dashboard thresholds based on baseline
**Description**: Update dashboard JSON with tuned thresholds (only if Week 2 assessment requires)
**Acceptance Criteria**:
- [ ] Baseline values confirmed from Week 2 assessment
- [ ] Thresholds calculated:
  - Warning threshold: baseline + 2%
  - Critical threshold: baseline + 5%
- [ ] Dashboard JSON updated
- [ ] Re-imported to Grafana
- [ ] Alert thresholds tested with mock data
- [ ] Tuning documented in comment

**Estimated Hours**: 1.5

### Child 5: Mark Observability Production-Ready (Week 4)

**Title**: Complete PR #5 observability monitoring - production ready
**Description**: Final sign-off after 4-week monitoring cycle
**Acceptance Criteria**:
- [ ] Week 1: Baseline established
- [ ] Week 2: Assessment complete
- [ ] Week 3: Thresholds tuned (if needed)
- [ ] Dashboard stable and displaying metrics
- [ ] Prometheus scraping reliable (0 errors)
- [ ] `.project-context.md` updated with baseline metrics
- [ ] All checks pass

**Estimated Hours**: 0.5

---

## Dependency Graph

```
Main Issue (Monitor PR #5 Baseline)
    ├── Child 1: Import Dashboard (blocks others)
    │   └── Child 2: Establish Baseline (blocked by Child 1)
    │       └── Child 3: Assess Baseline
    │           ├── Child 4: Tune Thresholds (conditional)
    │           │   └── Child 5: Mark Production-Ready
    │           └── Child 5: Mark Production-Ready (if no tuning needed)
```

---

## Success Criteria (Main Issue)

All of the following must be TRUE:

1. ✅ **Dashboard Data Flowing** (Week 1)
   - Prometheus metrics exported
   - Grafana dashboard shows data
   - No "No Data" messages after initialization

2. ✅ **Baseline Established** (Week 1-2)
   - 7+ days of metrics collected
   - False positive rate < 5%
   - False negative rate = 0%

3. ✅ **Thresholds Acceptable** (Week 2-3)
   - If baseline < 5%: thresholds unchanged, proceed to production
   - If baseline >= 5%: thresholds tuned, alarm-tested

4. ✅ **Monitoring Reliable** (Week 4)
   - Prometheus scrape errors: 0
   - Dashboard uptime: 100%
   - Metrics freshness: < 2 minutes old

5. ✅ **Documentation Complete** (Week 4)
   - Baseline metrics documented
   - Threshold values finalized
   - `.project-context.md` updated
   - Setup guide verified (pr5-completion-summary.md)

---

## Comment Template for Status Updates

Use this template when updating the Linear issue with progress:

```
[Week: 1 of 4]
[Date: YYYY-MM-DD]

Progress:
- [x] Dashboard imported
- [x] Metrics flowing
- [ ] Baseline metrics documented

Current Baseline (as of today):
- False Positive Rate: X.X%
- False Negative Rate: X.X%
- Detection Rate: X per minute
- Check Duration (p95): X ms

Observations:
[Notes about metric behavior]

Next: [Next week's focus]

Threshold Tuning Needed: [Yes/No]
```

---

## Integration with Project Tracking

**When Linear is configured**, this issue should be:

1. **Created** under the IW project team
2. **Linked** to PR #5 (main feature issue)
3. **Assigned** to observability team member
4. **Scheduled** for Week 1 start (2025-11-17)
5. **Monitored** via dashboard status updates

---

## File References

- **Completion Summary**: `docs/.scratch/pr5-completion-summary.md`
- **Dashboard**: `observability/grafana-dashboards/llm-guard-scanner-health.json`
- **Project Context**: `.project-context.md`

---

## Linear Configuration Requirements

When Linear is enabled for IW:

1. **Workspace Setup**:
   - Create IW team in Linear workspace
   - Configure project for this repository
   - Set up issue template with this structure

2. **Team Configuration**:
   - Assign observability owner
   - Set up notification rules
   - Configure automation

3. **Integration**:
   - Link GitHub branch to issue
   - Enable PR linking
   - Configure merge commit messages

---

**Template Version**: 1.0
**Created**: 2025-11-17
**Status**: Ready for Linear integration
