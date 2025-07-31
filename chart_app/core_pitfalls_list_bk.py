def get_core_pitfalls():
    return {
        "misrepresentation": {
            "label": "Misrepresentation",
            "description": "A visualization should draw data proportionally and to scale.",
            "reason": "Distorts data relationships by manipulating proportions or visual elements."
        },
        "truncated_axis": {
            "label": "Truncated Axis",
            "description": "A visualization should show the full range of values on its axes.",
            "reason": "Exaggerates trends or differences by starting the axis at a non-zero point."
        },
        "inappropriate_axis_range": {
            "label": "Inappropriate Axis Range",
            "description": "The chart uses an axis range that distorts comparisons between data points.",
            "reason": "Magnifies or minimizes differences, altering the viewer's perception of the data."
        },
        "selective_data": {
            "label": "Selective Data",
            "description": "A visualization should not cherry-pick data to support a predetermined conclusion.",
            "reason": "Creates a biased narrative by omitting relevant data points or ranges."
        },
        "confusing_chart_type": {
            "label": "Confusing Chart Type",
            "description": "A visualization should not use inappropriate chart types that fail to represent the data accurately.",
            "reason": "Leads to misinterpretation by using the wrong type of chart for the dataset."
        },
        "hidden_distribution": {
            "label": "Hidden Distribution",
            "description": "A visualization should show underlying data distribution when relevant.",
            "reason": "Fails to represent important variations or outliers, oversimplifying the data."
        },
        "misleading_title": {
            "label": "Misleading Title",
            "description": "A visualization should have an accurate title that reflects the true nature of the data.",
            "reason": "Influences interpretation by implying conclusions unsupported by the data."
        },
        "misleading_annotation": {
            "label": "Misleading Annotation",
            "description": "A visualization should use accurate and unbiased annotations.",
            "reason": "Biases the viewer by adding annotations that misrepresent or distort the data."
        },
        "color_blind_unfriendly": {
            "label": "Color-Blind Unfriendly",
            "description": "A visualization should use color schemes that are distinguishable by individuals with color vision deficiencies.",
            "reason": "Limits accessibility by making it difficult for color-blind viewers to interpret the graph."
        },
        "overplotting": {
            "label": "Overplotting",
            "description": "A visualization should use techniques to prevent overlapping data points from obscuring patterns.",
            "reason": "Obscures patterns and trends due to excessive data overlap or clutter."
        },
        "dual_axis": {
            "label": "Dual Axis",
            "description": "A visualization should use dual axes carefully, ensuring clear labeling and explanation to prevent misinterpretation.",
            "reason": "Creates false correlations or exaggerates trends by improperly aligning axes."
        },
        "violating_color_convention": {
            "label": "Violating Color Convention",
            "description": "A visualization should use colors that match conventional meanings unless clearly explained otherwise.",
            "reason": "Confuses viewers by using unconventional colors without adequate explanation."
        },
        "inappropriate_use_of_pie_chart": {
            "label": "Inappropriate Use of Pie Chart",
            "description": "A visualization should use pie charts only for part-to-whole relationships with a small number of categories.",
            "reason": "Leads to misinterpretation when used for unrelated data or with too many slices."
        },
        "pattern_seeking": {
            "label": "Pattern Seeking",
            "description": "A visualization should not use historical correlation to predict future trends without justification.",
            "reason": "Creates false narratives by implying causation from correlation."
        },
        "correlation_not_causation": {
            "label": "Correlation, Not Causation",
            "description": "A visualization should not imply causation from correlation.",
            "reason": "Misleads viewers by implying a causal relationship that does not exist."
        },
        "hidden_uncertainty": {
            "label": "Hidden Uncertainty",
            "description": "A visualization should include appropriate representations of data uncertainty.",
            "reason": "Misrepresents confidence in the data by omitting uncertainty or error margins."
        },
        "questionable_prediction": {
            "label": "Questionable Prediction",
            "description": "A visualization should not extrapolate trends without a justified statistical method.",
            "reason": "Misleads viewers by presenting unsupported future projections."
        },
        "changing_scale": {
            "label": "Changing Scale",
            "description": "A visualization should maintain consistent scales within the same chart and between related charts.",
            "reason": "Confuses viewers by using inconsistent scales, making comparisons invalid."
        },
        "overplotting": {
            "label": "Overplotting",
            "description": "A visualization should avoid excessive visual elements that make trends or comparisons unclear.",
            "reason": "Too many overlapping or clustered elements obscure patterns and make interpretation difficult."
        },
        "misleading_aggregation": {
            "label": "Misleading Aggregation",
            "description": "A visualization should not aggregate data in a way that hides meaningful trends or variability.",
            "reason": "Daily totals without explanations or averages can misrepresent underlying trends."
        },
        "missing_context_or_comparison_metric": {
            "label": "Missing Context or Comparison Metric",
            "description": "A visualization should provide relevant context (e.g., testing rates, positivity rates) to interpret the data.",
            "reason": "Lack of context prevents accurate understanding of trends or severity."
        }

    }



