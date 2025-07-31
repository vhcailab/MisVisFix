def get_core_pitfalls():
    return {
        "misrepresentation": {
            "label": "Misrepresentation",
            "description": "A visualization must draw data proportionally, using consistent scale, direction, and visual encoding.",
            "rule": "Distorts data relationships by manipulating proportions, flipping scale direction, or reversing intuitive meanings (e.g., inverted y-axis)."
        },
        "truncated_axis": {
            "label": "Truncated Axis",
            "description": "Bar and column charts must start the y-axis at zero unless clearly justified.",
            "rule": "Exaggerates trends or differences by starting the axis at a non-zero point or visually manipulating scale direction."
        },
        "inappropriate_axis_range": {
            "label": "Inappropriate Axis Range",
            "description": "Charts must use axis ranges that preserve accurate comparison of values.",
            "rule": "Magnifies or minimizes differences, altering the viewer's perception of the data."
        },
        "selective_data": {
            "label": "Selective Data",
            "description": "Charts must not omit relevant values, time ranges, or categories to influence interpretation.",
            "rule": "Creates a biased narrative by cherry-picking data or omitting important context."
        },
        "confusing_chart_type": {
            "label": "Confusing Chart Type",
            "description": "A chart must use a visual representation that clearly reflects the structure of the data.",
            "rule": "Leads to misinterpretation by using the wrong visual form for the dataset."
        },
        "hidden_distribution": {
            "label": "Hidden Distribution",
            "description": "A visualization should expose variation or outliers when relevant to understanding the data.",
            "rule": "Oversimplifies the data by hiding its underlying structure or variability."
        },
        "misleading_title": {
            "label": "Misleading Title",
            "description": "Titles must describe what the chart actually shows without implying unsupported conclusions.",
            "rule": "Frames interpretation in a way that is biased or inaccurate."
        },
        "misleading_annotation": {
            "label": "Misleading Annotation",
            "description": "Annotations must avoid emotional, visual, or narrative cues that suggest unsupported conclusions.",
            "rule": "Biases the viewer with text, visual emphasis, or timing that implies causality or value judgments."
        },
        "color_blind_unfriendly": {
            "label": "Color-Blind Unfriendly",
            "description": "Charts must use color schemes distinguishable by individuals with color vision deficiencies.",
            "rule": "Limits accessibility and comprehension for color-blind viewers."
        },
        "overplotting": {
            "label": "Overplotting",
            "description": "Charts should avoid overlapping data points or clutter that obscures trends.",
            "rule": "Excessive visual overlap prevents clear pattern recognition."
        },
        "dual_axis": {
            "label": "Dual Axis",
            "description": "Dual axes must be used with clear labels and explanation.",
            "rule": "Improper alignment or scaling creates false correlations or exaggerations."
        },
        "violating_color_convention": {
            "label": "Violating Color Convention",
            "description": "Colors must follow intuitive or standard meanings unless explicitly explained.",
            "rule": "Can mislead by reversing common interpretations (e.g., red = bad, green = good)."
        },
        "inappropriate_use_of_pie_chart": {
            "label": "Inappropriate Use of Pie Chart",
            "description": "Pie charts must be reserved for part-to-whole relationships with few categories.",
            "rule": "Hard to interpret when used for unrelated quantities or with too many slices."
        },
        "pattern_seeking": {
            "label": "Pattern Seeking",
            "description": "Visuals must not imply trends or predictions based only on visual continuity.",
            "rule": "Creates false narratives by suggesting trends where none are supported."
        },
        "correlation_not_causation": {
            "label": "Correlation, Not Causation",
            "description": "Charts must not imply that one variable causes another unless supported by evidence.",
            "rule": "Misleads viewers by placing related trends side-by-side or sequencing them suggestively."
        },
        "hidden_uncertainty": {
            "label": "Hidden Uncertainty",
            "description": "Charts should include error bars or confidence ranges when data includes uncertainty.",
            "rule": "Hides variability and confidence intervals, misleading viewers about precision."
        },
        "questionable_prediction": {
            "label": "Questionable Prediction",
            "description": "Extrapolations must be backed by statistically valid models.",
            "rule": "Visual forecasts without explanation mislead viewers about future trends."
        },
        "changing_scale": {
            "label": "Changing Scale",
            "description": "Related charts must maintain consistent scale unless clearly justified.",
            "rule": "Inconsistent scaling across views confuses viewers and invalidates comparisons."
        },
        "misleading_aggregation": {
            "label": "Misleading Aggregation",
            "description": "Aggregation must reflect appropriate summary level without hiding key details.",
            "rule": "Can hide important variation or falsely flatten peaks in trends."
        },
        "missing_context_or_comparison_metric": {
            "label": "Missing Context or Comparison Metric",
            "description": "Charts should include baseline, reference points, or comparison to provide meaning.",
            "rule": "Without context, viewers cannot assess significance or interpret values properly."
        }
    }
