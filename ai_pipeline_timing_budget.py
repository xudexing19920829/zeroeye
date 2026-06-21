#!/usr/bin/env python3
"""
AI Pipeline Timing Budget Summary.

This script analyzes AI pipeline execution times and generates
a timing budget summary with performance insights.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TimingBudget:
    """Timing budget for a pipeline stage."""
    stage: str
    budget_ms: float
    actual_ms: float
    variance_ms: float
    variance_percent: float
    status: str  # "within_budget", "over_budget", "under_budget"


@dataclass
class PipelineTiming:
    """Complete pipeline timing analysis."""
    pipeline_id: str
    start_time: str
    end_time: str
    total_duration_ms: float
    stages: List[TimingBudget]
    overall_status: str
    recommendations: List[str]


class AIPipelineTimingAnalyzer:
    """Analyze AI pipeline timing budgets."""
    
    def __init__(self):
        self.budgets = {
            "data_loading": 1000,      # 1 second
            "preprocessing": 2000,     # 2 seconds
            "model_inference": 5000,   # 5 seconds
            "postprocessing": 1000,    # 1 second
            "output_generation": 500   # 0.5 seconds
        }
    
    def analyze_stage(self, stage: str, actual_ms: float) -> TimingBudget:
        """Analyze a single pipeline stage."""
        budget_ms = self.budgets.get(stage, 1000)
        variance_ms = actual_ms - budget_ms
        variance_percent = (variance_ms / budget_ms) * 100
        
        if variance_ms > 0:
            status = "over_budget"
        elif variance_ms < -budget_ms * 0.5:  # More than 50% under budget
            status = "under_budget"
        else:
            status = "within_budget"
        
        return TimingBudget(
            stage=stage,
            budget_ms=budget_ms,
            actual_ms=actual_ms,
            variance_ms=variance_ms,
            variance_percent=variance_percent,
            status=status
        )
    
    def analyze_pipeline(self, pipeline_id: str, stage_times: Dict[str, float]) -> PipelineTiming:
        """Analyze complete pipeline timing."""
        stages = []
        total_duration = 0
        
        for stage, actual_ms in stage_times.items():
            timing = self.analyze_stage(stage, actual_ms)
            stages.append(timing)
            total_duration += actual_ms
        
        # Determine overall status
        over_budget_count = sum(1 for s in stages if s.status == "over_budget")
        if over_budget_count > 0:
            overall_status = "over_budget"
        elif any(s.status == "under_budget" for s in stages):
            overall_status = "optimized"
        else:
            overall_status = "within_budget"
        
        # Generate recommendations
        recommendations = self.generate_recommendations(stages)
        
        return PipelineTiming(
            pipeline_id=pipeline_id,
            start_time=datetime.now().isoformat(),
            end_time=datetime.now().isoformat(),
            total_duration_ms=total_duration,
            stages=stages,
            overall_status=overall_status,
            recommendations=recommendations
        )
    
    def generate_recommendations(self, stages: List[TimingBudget]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        for stage in stages:
            if stage.status == "over_budget":
                recommendations.append(
                    f"Optimize {stage.stage}: {stage.variance_percent:.1f}% over budget "
                    f"({stage.actual_ms:.0f}ms vs {stage.budget_ms:.0f}ms budget)"
                )
            elif stage.status == "under_budget":
                recommendations.append(
                    f"Consider increasing budget for {stage.stage}: "
                    f"{abs(stage.variance_percent):.1f}% under budget"
                )
        
        return recommendations
    
    def generate_summary(self, pipeline: PipelineTiming) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Pipeline Timing Budget Summary",
            f"=" * 40,
            f"Pipeline ID: {pipeline.pipeline_id}",
            f"Total Duration: {pipeline.total_duration_ms:.0f}ms",
            f"Overall Status: {pipeline.overall_status}",
            "",
            "Stage Breakdown:",
            "-" * 40
        ]
        
        for stage in pipeline.stages:
            status_icon = "✅" if stage.status == "within_budget" else "⚠️" if stage.status == "over_budget" else "💡"
            lines.append(
                f"{status_icon} {stage.stage}: {stage.actual_ms:.0f}ms "
                f"(budget: {stage.budget_ms:.0f}ms, "
                f"variance: {stage.variance_percent:+.1f}%)"
            )
        
        if pipeline.recommendations:
            lines.extend([
                "",
                "Recommendations:",
                "-" * 40
            ])
            for rec in pipeline.recommendations:
                lines.append(f"• {rec}")
        
        return "\n".join(lines)


def main():
    """Main function."""
    analyzer = AIPipelineTimingAnalyzer()
    
    # Example pipeline timing data
    stage_times = {
        "data_loading": 800,
        "preprocessing": 2500,
        "model_inference": 4800,
        "postprocessing": 1200,
        "output_generation": 400
    }
    
    # Analyze pipeline
    pipeline = analyzer.analyze_pipeline("pipeline-001", stage_times)
    
    # Generate summary
    summary = analyzer.generate_summary(pipeline)
    print(summary)
    
    # Save to file
    output_file = "pipeline_timing_report.json"
    with open(output_file, "w") as f:
        json.dump(asdict(pipeline), f, indent=2)
    
    print(f"\nDetailed report saved to: {output_file}")
    
    # Exit with status
    if pipeline.overall_status == "over_budget":
        print("\n⚠️  Pipeline is over budget!")
        sys.exit(1)
    else:
        print("\n✅ Pipeline is within budget!")
        sys.exit(0)


if __name__ == "__main__":
    main()
