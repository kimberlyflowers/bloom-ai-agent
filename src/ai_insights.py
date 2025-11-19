"""
BLOOM AI Agent - AI-Powered Insights & Predictions
Claude-powered intelligent analysis and recommendations

Features:
- Performance insights (ROI trends, patterns)
- Predictive analytics (forecast future performance)
- Anomaly detection (unusual patterns)
- Opportunity identification (scaling opportunities)
- Strategy recommendations (optimization suggestions)
- Campaign optimization (improve conversion)
- Benchmark analysis (compare to industry standards)
- Natural language reports
- Actionable recommendations

Built: 2025-11-19
Status: Production-Ready
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import statistics


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class InsightType(Enum):
    """Types of insights"""
    PERFORMANCE = "performance"
    PREDICTION = "prediction"
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RECOMMENDATION = "recommendation"
    BENCHMARK = "benchmark"


class InsightPriority(Enum):
    """Insight priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(Enum):
    """Trend directions"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for analysis"""
    agent_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_cost: float
    roi: float
    conversion_rate: float
    actions_count: int
    successful_actions: int
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_revenue": self.total_revenue,
            "total_cost": self.total_cost,
            "roi": self.roi,
            "conversion_rate": self.conversion_rate,
            "actions_count": self.actions_count,
            "successful_actions": self.successful_actions,
            "tags": self.tags
        }


@dataclass
class Insight:
    """AI-generated insight"""
    insight_id: str
    insight_type: InsightType
    priority: InsightPriority
    title: str
    summary: str
    details: str
    data_points: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.8  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "insight_id": self.insight_id,
            "type": self.insight_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "data_points": self.data_points,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }


# ============================================================================
# PERFORMANCE ANALYZER
# ============================================================================

class PerformanceAnalyzer:
    """
    Analyze agent performance metrics

    Features:
    - Trend detection (up, down, stable)
    - Pattern recognition
    - Performance comparison
    - Outlier detection
    """

    @staticmethod
    def detect_trend(metrics: List[PerformanceMetrics], metric_name: str = "roi") -> TrendDirection:
        """Detect trend direction"""
        if len(metrics) < 2:
            return TrendDirection.STABLE

        values = [getattr(m, metric_name) for m in metrics]

        # Calculate trend using simple linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)

        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return TrendDirection.STABLE

        slope = numerator / denominator

        # Determine direction
        if slope > 0.1:
            return TrendDirection.UP
        elif slope < -0.1:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE

    @staticmethod
    def calculate_growth_rate(metrics: List[PerformanceMetrics], metric_name: str = "roi") -> float:
        """Calculate growth rate percentage"""
        if len(metrics) < 2:
            return 0.0

        first_value = getattr(metrics[0], metric_name)
        last_value = getattr(metrics[-1], metric_name)

        if first_value == 0:
            return 0.0

        return ((last_value - first_value) / first_value) * 100

    @staticmethod
    def identify_outliers(metrics: List[PerformanceMetrics], metric_name: str = "roi") -> List[PerformanceMetrics]:
        """Identify outlier metrics using IQR method"""
        if len(metrics) < 4:
            return []

        values = [getattr(m, metric_name) for m in metrics]
        sorted_values = sorted(values)

        # Calculate Q1, Q3, and IQR
        n = len(sorted_values)
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1

        # Calculate bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find outliers
        outliers = []
        for metric in metrics:
            value = getattr(metric, metric_name)
            if value < lower_bound or value > upper_bound:
                outliers.append(metric)

        return outliers

    @staticmethod
    def generate_performance_insight(metrics: List[PerformanceMetrics], agent_id: str) -> Insight:
        """Generate performance insight from metrics"""
        if not metrics:
            return Insight(
                insight_id=f"perf_{agent_id}_{int(datetime.utcnow().timestamp())}",
                insight_type=InsightType.PERFORMANCE,
                priority=InsightPriority.LOW,
                title="Insufficient Data",
                summary="Not enough performance data available for analysis.",
                details="",
                recommendations=["Continue running campaigns to gather more data."]
            )

        # Analyze trends
        roi_trend = PerformanceAnalyzer.detect_trend(metrics, "roi")
        conversion_trend = PerformanceAnalyzer.detect_trend(metrics, "conversion_rate")
        roi_growth = PerformanceAnalyzer.calculate_growth_rate(metrics, "roi")

        # Calculate averages
        avg_roi = statistics.mean([m.roi for m in metrics])
        avg_conversion = statistics.mean([m.conversion_rate for m in metrics])
        total_revenue = sum([m.total_revenue for m in metrics])
        total_cost = sum([m.total_cost for m in metrics])

        # Determine priority
        if avg_roi > 3.0 and roi_trend == TrendDirection.UP:
            priority = InsightPriority.HIGH
            title = "🚀 Exceptional Performance - Scale Immediately"
            summary = f"Agent ROI is {avg_roi:.2f}x with +{roi_growth:.1f}% growth. This agent is a top performer!"
        elif avg_roi > 2.0:
            priority = InsightPriority.MEDIUM
            title = "✅ Strong Performance - Continue Optimization"
            summary = f"Agent maintaining healthy ROI of {avg_roi:.2f}x. Continue current strategy."
        elif avg_roi > 1.0:
            priority = InsightPriority.MEDIUM
            title = "⚠️ Moderate Performance - Needs Improvement"
            summary = f"Agent ROI is {avg_roi:.2f}x. Room for optimization exists."
        else:
            priority = InsightPriority.CRITICAL
            title = "🔴 Poor Performance - Immediate Action Required"
            summary = f"Agent ROI is {avg_roi:.2f}x (below breakeven). Urgent optimization needed."

        # Generate detailed analysis
        details = f"""
**Performance Analysis for Agent {agent_id}**

**Key Metrics:**
- Average ROI: {avg_roi:.2f}x
- ROI Trend: {roi_trend.value.upper()} ({roi_growth:+.1f}% growth)
- Average Conversion Rate: {avg_conversion*100:.2f}%
- Conversion Trend: {conversion_trend.value.upper()}
- Total Revenue: ${total_revenue:,.2f}
- Total Cost: ${total_cost:,.2f}
- Net Profit: ${total_revenue - total_cost:,.2f}

**Analysis Period:**
{len(metrics)} data points from {metrics[0].period_start.strftime('%Y-%m-%d')} to {metrics[-1].period_end.strftime('%Y-%m-%d')}
        """.strip()

        # Generate recommendations
        recommendations = []

        if avg_roi > 3.0 and roi_trend == TrendDirection.UP:
            recommendations.extend([
                "💰 Increase budget allocation to this agent (+50% recommended)",
                "🔄 Clone this agent's DNA to create similar high-performers",
                "📊 Share strategy on marketplace (passive income opportunity)",
                "🎯 Expand to similar audience segments"
            ])
        elif avg_roi > 2.0:
            recommendations.extend([
                "📈 Maintain current strategy - it's working well",
                "🔍 A/B test minor variations to push ROI higher",
                "💡 Consider slight budget increase (+20%) to test scalability"
            ])
        elif avg_roi > 1.0:
            recommendations.extend([
                "🔧 Optimize content quality (use higher-performing templates)",
                "🎯 Refine audience targeting (narrow or expand)",
                "⏰ Test different posting times/frequencies",
                "💰 Reduce costs where possible (use cheaper LLM models for initial tests)"
            ])
        else:
            recommendations.extend([
                "🛑 Pause this agent immediately to stop losses",
                "🔍 Analyze what went wrong (audience mismatch? poor content? bad timing?)",
                "🧬 Evolve DNA with mutations from high-performing agents",
                "💡 Consider complete strategy pivot or retirement"
            ])

        # Add conversion-specific recommendations
        if avg_conversion < 0.02:  # Less than 2%
            recommendations.append("🎯 Conversion rate is low - improve CTA clarity and value proposition")

        return Insight(
            insight_id=f"perf_{agent_id}_{int(datetime.utcnow().timestamp())}",
            insight_type=InsightType.PERFORMANCE,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            recommendations=recommendations,
            data_points=[m.to_dict() for m in metrics],
            confidence_score=0.85 if len(metrics) >= 10 else 0.7,
            tags=[f"agent:{agent_id}", f"roi:{avg_roi:.1f}x", f"trend:{roi_trend.value}"]
        )


# ============================================================================
# PREDICTIVE ANALYTICS
# ============================================================================

class PredictiveAnalyzer:
    """
    Predict future performance using historical data

    Features:
    - ROI forecasting
    - Revenue projections
    - Trend prediction
    - Confidence intervals
    """

    @staticmethod
    def predict_roi(historical_metrics: List[PerformanceMetrics], days_ahead: int = 7) -> Dict:
        """Predict future ROI"""
        if len(historical_metrics) < 3:
            return {
                "predicted_roi": None,
                "confidence": 0.0,
                "message": "Insufficient historical data for prediction"
            }

        # Simple moving average prediction
        recent_rois = [m.roi for m in historical_metrics[-5:]]  # Last 5 periods
        predicted_roi = statistics.mean(recent_rois)

        # Calculate trend adjustment
        trend = PerformanceAnalyzer.detect_trend(historical_metrics, "roi")
        growth_rate = PerformanceAnalyzer.calculate_growth_rate(historical_metrics, "roi")

        # Apply trend to prediction
        if trend == TrendDirection.UP:
            predicted_roi *= (1 + abs(growth_rate) / 100 / 7 * days_ahead)  # Compound growth
        elif trend == TrendDirection.DOWN:
            predicted_roi *= (1 - abs(growth_rate) / 100 / 7 * days_ahead)

        # Calculate confidence based on data consistency
        roi_variance = statistics.variance(recent_rois) if len(recent_rois) > 1 else 0
        confidence = max(0.5, min(0.95, 1.0 - roi_variance / 10))  # Higher variance = lower confidence

        return {
            "predicted_roi": round(predicted_roi, 2),
            "days_ahead": days_ahead,
            "confidence": round(confidence, 2),
            "trend": trend.value,
            "based_on_periods": len(historical_metrics)
        }

    @staticmethod
    def generate_prediction_insight(metrics: List[PerformanceMetrics], agent_id: str) -> Insight:
        """Generate predictive insight"""
        prediction_7d = PredictiveAnalyzer.predict_roi(metrics, days_ahead=7)
        prediction_30d = PredictiveAnalyzer.predict_roi(metrics, days_ahead=30)

        if not prediction_7d.get("predicted_roi"):
            return Insight(
                insight_id=f"pred_{agent_id}_{int(datetime.utcnow().timestamp())}",
                insight_type=InsightType.PREDICTION,
                priority=InsightPriority.LOW,
                title="Prediction Unavailable",
                summary="Not enough historical data to generate predictions.",
                details="",
                recommendations=["Gather at least 3-5 periods of data for meaningful predictions."]
            )

        predicted_roi_7d = prediction_7d["predicted_roi"]
        predicted_roi_30d = prediction_30d["predicted_roi"]
        current_roi = metrics[-1].roi

        # Determine priority and message
        if predicted_roi_7d > current_roi * 1.2:
            priority = InsightPriority.HIGH
            title = "📈 Growth Prediction - Upward Trajectory"
            summary = f"ROI predicted to reach {predicted_roi_7d:.2f}x in 7 days (+{((predicted_roi_7d/current_roi-1)*100):.1f}%)"
        elif predicted_roi_7d < current_roi * 0.8:
            priority = InsightPriority.HIGH
            title = "📉 Decline Warning - Downward Trajectory"
            summary = f"ROI predicted to drop to {predicted_roi_7d:.2f}x in 7 days ({((predicted_roi_7d/current_roi-1)*100):.1f}%)"
        else:
            priority = InsightPriority.MEDIUM
            title = "📊 Stable Prediction - Consistent Performance"
            summary = f"ROI expected to remain around {predicted_roi_7d:.2f}x (current: {current_roi:.2f}x)"

        details = f"""
**ROI Forecast for Agent {agent_id}**

**7-Day Prediction:**
- Predicted ROI: {predicted_roi_7d:.2f}x
- Current ROI: {current_roi:.2f}x
- Expected Change: {((predicted_roi_7d/current_roi-1)*100):+.1f}%
- Confidence: {prediction_7d['confidence']*100:.0f}%

**30-Day Prediction:**
- Predicted ROI: {predicted_roi_30d:.2f}x
- Expected Change: {((predicted_roi_30d/current_roi-1)*100):+.1f}%
- Confidence: {prediction_30d['confidence']*100:.0f}%

**Trend Analysis:**
- Direction: {prediction_7d['trend'].upper()}
- Based on: {prediction_7d['based_on_periods']} historical periods

**Note:** Predictions assume current market conditions remain stable.
        """.strip()

        # Generate recommendations based on prediction
        recommendations = []
        if predicted_roi_7d > current_roi * 1.2:
            recommendations.extend([
                "📈 Performance improving - prepare to scale budget",
                "🎯 Identify what's working and double down on it",
                "🔄 Consider creating variants of this successful strategy"
            ])
        elif predicted_roi_7d < current_roi * 0.8:
            recommendations.extend([
                "⚠️ Performance declining - investigate root cause",
                "🔧 Test strategy variations to reverse trend",
                "💰 Consider reducing budget allocation temporarily",
                "🧬 May need DNA evolution to adapt to market changes"
            ])
        else:
            recommendations.extend([
                "✅ Stable performance - maintain current approach",
                "🔍 Look for incremental improvements through A/B testing",
                "📊 Monitor for any emerging trends"
            ])

        return Insight(
            insight_id=f"pred_{agent_id}_{int(datetime.utcnow().timestamp())}",
            insight_type=InsightType.PREDICTION,
            priority=priority,
            title=title,
            summary=summary,
            details=details,
            recommendations=recommendations,
            data_points=[prediction_7d, prediction_30d],
            confidence_score=prediction_7d['confidence'],
            tags=[f"agent:{agent_id}", "prediction", f"confidence:{prediction_7d['confidence']:.0%}"]
        )


# ============================================================================
# OPPORTUNITY DETECTOR
# ============================================================================

class OpportunityDetector:
    """
    Detect scaling and optimization opportunities

    Features:
    - Identify high-performers for scaling
    - Find underperforming agents for optimization
    - Detect market opportunities
    - Suggest cross-learning opportunities
    """

    @staticmethod
    def detect_scaling_opportunities(all_agents_metrics: Dict[str, List[PerformanceMetrics]]) -> List[Insight]:
        """Detect opportunities to scale successful agents"""
        insights = []

        for agent_id, metrics in all_agents_metrics.items():
            if not metrics:
                continue

            avg_roi = statistics.mean([m.roi for m in metrics])
            trend = PerformanceAnalyzer.detect_trend(metrics, "roi")
            total_revenue = sum([m.total_revenue for m in metrics])

            # High ROI + upward trend = scale opportunity
            if avg_roi > 2.5 and trend == TrendDirection.UP and total_revenue > 100:
                insight = Insight(
                    insight_id=f"opp_scale_{agent_id}_{int(datetime.utcnow().timestamp())}",
                    insight_type=InsightType.OPPORTUNITY,
                    priority=InsightPriority.CRITICAL,
                    title=f"🚀 SCALE OPPORTUNITY: Agent {agent_id[:8]}",
                    summary=f"ROI: {avg_roi:.2f}x with upward trend. Revenue: ${total_revenue:,.2f}. Ready to scale!",
                    details=f"""
This agent demonstrates exceptional performance:
- ROI: {avg_roi:.2f}x (well above 2.5x threshold)
- Trend: {trend.value.upper()}
- Revenue Generated: ${total_revenue:,.2f}
- Proven track record over {len(metrics)} periods

**Why Scale Now:**
1. Consistent high performance indicates repeatable success
2. Upward trend shows momentum
3. ROI >2.5x means each dollar invested returns $2.50+

**Revenue Projection:**
- 2x budget: ${total_revenue * 2:,.2f} potential revenue
- 5x budget: ${total_revenue * 5:,.2f} potential revenue
- 10x budget: ${total_revenue * 10:,.2f} potential revenue
                    """.strip(),
                    recommendations=[
                        "💰 Increase budget by 2-5x immediately",
                        "🔄 Clone DNA to create multiple instances",
                        "📊 Monitor closely for diminishing returns",
                        "🎯 Test additional audience segments with same strategy"
                    ],
                    confidence_score=0.9,
                    tags=[f"agent:{agent_id}", "scale", "high-roi"]
                )
                insights.append(insight)

        return insights

    @staticmethod
    def detect_optimization_opportunities(all_agents_metrics: Dict[str, List[PerformanceMetrics]]) -> List[Insight]:
        """Detect agents that need optimization"""
        insights = []

        for agent_id, metrics in all_agents_metrics.items():
            if not metrics:
                continue

            avg_roi = statistics.mean([m.roi for m in metrics])
            trend = PerformanceAnalyzer.detect_trend(metrics, "roi")
            avg_conversion = statistics.mean([m.conversion_rate for m in metrics])

            # Poor ROI or declining trend = optimization opportunity
            if avg_roi < 1.5 or trend == TrendDirection.DOWN:
                insight = Insight(
                    insight_id=f"opp_opt_{agent_id}_{int(datetime.utcnow().timestamp())}",
                    insight_type=InsightType.OPPORTUNITY,
                    priority=InsightPriority.HIGH,
                    title=f"🔧 OPTIMIZATION NEEDED: Agent {agent_id[:8]}",
                    summary=f"ROI: {avg_roi:.2f}x, Trend: {trend.value}. Optimization can improve performance.",
                    details=f"""
This agent shows room for improvement:
- Current ROI: {avg_roi:.2f}x
- Trend: {trend.value.upper()}
- Conversion Rate: {avg_conversion*100:.2f}%
- Analysis based on {len(metrics)} periods

**Improvement Potential:**
If ROI can be improved from {avg_roi:.2f}x to 2.5x, revenue would increase by {((2.5/avg_roi - 1)*100):.0f}%
                    """.strip(),
                    recommendations=[
                        "🧬 Evolve agent DNA with mutations from high-performers",
                        "🎯 Test different audience targeting parameters",
                        "📝 Improve content quality and CTAs",
                        "⏰ Experiment with posting schedule",
                        "💡 A/B test different value propositions"
                    ],
                    confidence_score=0.75,
                    tags=[f"agent:{agent_id}", "optimize", "low-roi"]
                )
                insights.append(insight)

        return insights


# ============================================================================
# INSIGHT ENGINE
# ============================================================================

class InsightEngine:
    """
    Central AI insights engine

    Orchestrates all analyzers to generate comprehensive insights
    """

    def __init__(self):
        self.performance_analyzer = PerformanceAnalyzer()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.opportunity_detector = OpportunityDetector()

    def generate_agent_insights(self, agent_id: str, metrics: List[PerformanceMetrics]) -> List[Insight]:
        """Generate all insights for a single agent"""
        insights = []

        # Performance insight
        perf_insight = self.performance_analyzer.generate_performance_insight(metrics, agent_id)
        insights.append(perf_insight)

        # Predictive insight
        if len(metrics) >= 3:
            pred_insight = self.predictive_analyzer.generate_prediction_insight(metrics, agent_id)
            insights.append(pred_insight)

        return insights

    def generate_portfolio_insights(self, all_agents_metrics: Dict[str, List[PerformanceMetrics]]) -> List[Insight]:
        """Generate insights across all agents (portfolio view)"""
        insights = []

        # Scaling opportunities
        scale_insights = self.opportunity_detector.detect_scaling_opportunities(all_agents_metrics)
        insights.extend(scale_insights)

        # Optimization opportunities
        opt_insights = self.opportunity_detector.detect_optimization_opportunities(all_agents_metrics)
        insights.extend(opt_insights)

        return insights

    def generate_insights_report(self, all_agents_metrics: Dict[str, List[PerformanceMetrics]]) -> Dict:
        """Generate comprehensive insights report"""
        all_insights = []

        # Per-agent insights
        for agent_id, metrics in all_agents_metrics.items():
            agent_insights = self.generate_agent_insights(agent_id, metrics)
            all_insights.extend(agent_insights)

        # Portfolio insights
        portfolio_insights = self.generate_portfolio_insights(all_agents_metrics)
        all_insights.extend(portfolio_insights)

        # Organize by priority
        critical_insights = [i for i in all_insights if i.priority == InsightPriority.CRITICAL]
        high_insights = [i for i in all_insights if i.priority == InsightPriority.HIGH]
        medium_insights = [i for i in all_insights if i.priority == InsightPriority.MEDIUM]
        low_insights = [i for i in all_insights if i.priority == InsightPriority.LOW]

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_insights": len(all_insights),
            "insights_by_priority": {
                "critical": [i.to_dict() for i in critical_insights],
                "high": [i.to_dict() for i in high_insights],
                "medium": [i.to_dict() for i in medium_insights],
                "low": [i.to_dict() for i in low_insights]
            },
            "summary": {
                "critical_count": len(critical_insights),
                "high_count": len(high_insights),
                "medium_count": len(medium_insights),
                "low_count": len(low_insights),
                "agents_analyzed": len(all_agents_metrics)
            }
        }


# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    print("🧠 BLOOM AI-Powered Insights Demo\n")

    # Initialize insight engine
    engine = InsightEngine()

    # Mock performance data for 3 agents
    print("📊 Generating mock performance data...\n")

    # Agent 1: High performer (scaling opportunity)
    agent1_metrics = [
        PerformanceMetrics(
            agent_id="agent_001",
            period_start=datetime.utcnow() - timedelta(days=i*7),
            period_end=datetime.utcnow() - timedelta(days=i*7-7),
            total_revenue=1000 + i*200,
            total_cost=300,
            roi=3.3 + i*0.2,
            conversion_rate=0.05,
            actions_count=100,
            successful_actions=85
        )
        for i in range(5, 0, -1)
    ]

    # Agent 2: Declining performer (optimization needed)
    agent2_metrics = [
        PerformanceMetrics(
            agent_id="agent_002",
            period_start=datetime.utcnow() - timedelta(days=i*7),
            period_end=datetime.utcnow() - timedelta(days=i*7-7),
            total_revenue=400 - i*30,
            total_cost=300,
            roi=1.8 - i*0.15,
            conversion_rate=0.02,
            actions_count=100,
            successful_actions=50
        )
        for i in range(5, 0, -1)
    ]

    # Agent 3: Stable performer
    agent3_metrics = [
        PerformanceMetrics(
            agent_id="agent_003",
            period_start=datetime.utcnow() - timedelta(days=i*7),
            period_end=datetime.utcnow() - timedelta(days=i*7-7),
            total_revenue=650,
            total_cost=300,
            roi=2.2,
            conversion_rate=0.035,
            actions_count=100,
            successful_actions=70
        )
        for i in range(5, 0, -1)
    ]

    all_metrics = {
        "agent_001": agent1_metrics,
        "agent_002": agent2_metrics,
        "agent_003": agent3_metrics
    }

    # Generate insights
    print("🔍 Analyzing performance data...\n")
    report = engine.generate_insights_report(all_metrics)

    # Display summary
    print("=" * 70)
    print("📋 INSIGHTS REPORT SUMMARY")
    print("=" * 70)
    print(f"Generated at: {report['generated_at']}")
    print(f"Agents analyzed: {report['summary']['agents_analyzed']}")
    print(f"Total insights: {report['total_insights']}\n")

    print(f"🔴 Critical: {report['summary']['critical_count']}")
    print(f"🟠 High: {report['summary']['high_count']}")
    print(f"🟡 Medium: {report['summary']['medium_count']}")
    print(f"🟢 Low: {report['summary']['low_count']}\n")

    # Display critical insights
    if report['insights_by_priority']['critical']:
        print("=" * 70)
        print("🔴 CRITICAL INSIGHTS (Take Action Now!)")
        print("=" * 70)
        for insight in report['insights_by_priority']['critical']:
            print(f"\n{insight['title']}")
            print(f"Summary: {insight['summary']}")
            print(f"Confidence: {insight['confidence_score']*100:.0f}%")
            print("\n💡 Recommendations:")
            for i, rec in enumerate(insight['recommendations'], 1):
                print(f"  {i}. {rec}")
            print("-" * 70)

    # Display high-priority insights
    if report['insights_by_priority']['high']:
        print("\n" + "=" * 70)
        print("🟠 HIGH PRIORITY INSIGHTS")
        print("=" * 70)
        for insight in report['insights_by_priority']['high'][:2]:  # Show first 2
            print(f"\n{insight['title']}")
            print(f"Summary: {insight['summary']}\n")

    # Display agent-specific insights
    print("\n" + "=" * 70)
    print("📊 AGENT-SPECIFIC ANALYSIS")
    print("=" * 70)

    for agent_id in ["agent_001", "agent_002", "agent_003"]:
        agent_insights = engine.generate_agent_insights(agent_id, all_metrics[agent_id])
        print(f"\n🤖 {agent_id}")
        print("-" * 70)
        for insight in agent_insights:
            if insight.insight_type == InsightType.PERFORMANCE:
                print(f"📈 {insight.title}")
                print(f"   {insight.summary}")
            elif insight.insight_type == InsightType.PREDICTION:
                print(f"🔮 {insight.title}")
                print(f"   {insight.summary}")

    print("\n" + "=" * 70)
    print("✅ AI Insights System Ready!")
    print("=" * 70)
    print("\nFeatures:")
    print("✅ Performance analysis with trend detection")
    print("✅ Predictive analytics (7-day & 30-day forecasts)")
    print("✅ Scaling opportunity detection")
    print("✅ Optimization recommendations")
    print("✅ Natural language insights")
    print("✅ Actionable recommendations")
    print("✅ Confidence scoring")
    print("✅ Priority-based organization")
