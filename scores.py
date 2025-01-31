def dynamic_score(value, min_val, max_val, higher_is_better=True):
    """
    Dynamically calculate a score between 0 and 1 based on value position in the range.
    Args:
        value (float): Metric value.
        min_val (float): Minimum value of the range.
        max_val (float): Maximum value of the range.
        higher_is_better (bool): True if higher values are better, False if lower values are better.
    Returns:
        float: Score between 0 and 1.
    """
    if higher_is_better:
        if value <= min_val:
            return 0  # Lowest score
        elif value >= max_val:
            return 1  # Highest score
        else:
            return (value - min_val) / (max_val - min_val)  # Linear scaling
    else:
        if value <= min_val:
            return 1  # Best score for lower values
        elif value >= max_val:
            return 0  # Worst score for higher values
        else:
            return (max_val - value) / (max_val - min_val)  # Linear scaling
        
def score_using_criteria(give_metrics, scoring_criteria, calculate_weight=False):
    """Score calculation with weights and criteria
    Args:
        give_metrics (dict): give feature values
        scoring_criteria (dict): scoring criteria
        calculate_weight (bool): with weight or without weight
    Return:
        score
    """
    scores = []
    for metric, value in give_metrics.items():
        if metric in scoring_criteria:
            if calculate_weight:
                min_val, max_val, higher_is_better, weight = scoring_criteria[metric]
            else:
                min_val, max_val, higher_is_better = scoring_criteria[metric]

            base_score = dynamic_score(value, min_val, max_val, higher_is_better)
            if calculate_weight:
                score = base_score * weight  # Apply weight multiplier
            else:
                score = base_score
            scores.append(score)
    
    return sum(scores) / len(scores) if scores else 0  # Average score

def calculate_stock_score(metrics):
    """
    Calculate the overall stock score based on dynamic ranges for each metric.
    Args:
        metrics (dict): Metric name as key, value as value.
    Returns:
        float: Weighted overall score.
    """
    scoring_criteria = {
        # Metric: (min_val, max_val, higher_is_better)
        "P/E Ratio": (0, 25, False, 1.2),            # Lower is better
        "P/B Ratio": (0, 3, False, 1.2),             # Lower is better
        "D/E Ratio": (0, 1, False, 1.2),             # Lower is better
        "ROE (%)": (0, 20, True, 1.2),               # Higher is better
        "EPS Growth (%)": (0, 30, True, 1.2),        # Higher is better
        "Current Ratio": (1, 3, True, 1.2),          # Optimal range, higher is better up to 3
        "Dividend Yield (%)": (0, 5, True, 1),     # Higher is better
        "FCF Growth (%)": (0, 20, True, 1.2),        # Higher is better
        "Revenue Growth (%)": (0, 20, True, 1.2),    # Higher is better
        "Net Profit Margin (%)": (0, 30, True, 1), # Higher is better
        "Operating Margin (%)": (0, 30, True, 1),  # Higher is better
        "Cash Conversion Cycle (Days)": (60, 0, False, 1), # Lower is better (reversed range)
        "Interest Coverage Ratio": (0, 10, True, 1),       # Higher is better
        "Gross Margin (%)": (0, 60, True, 1),      # Higher is better
        "PEG Ratio": (0, 2, False, 1),             # Lower is better
        # technical
        "RSI": (30, 70, True, 0.8),                # Fast-moving, lower weight
        "MACD Signal Line Cross": (-1, 1, True, 1.2),  # Slow-moving, higher weight
        "Bollinger Bands %B": (0, 1, True, 1.0),   # Medium-moving
        "Volume Change (%)": (0, 100, True, 1.0),  # Medium-moving
        "SMA-50 vs SMA-200": (-5, 5, True, 1.2),   # Slow-moving
        "Price Above SMA-200 (%)": (0, 10, True, 1.2), # Slow-moving
        "Stochastic Oscillator": (20, 80, True, 0.8),  # Fast-moving
        "Volatility (ATR %)": (0, 5, False, 0.8),    # Fast-moving
        "Price Change (%)": (0, 10, True, 1.0),     # Medium-moving
        # Metric: (min_val, max_val, higher_is_better, weight)
        "Price Moved from 52-Week High (%)": (0, 20, True, 1.0),
        # "Promoter Holding Change (%)": (-5, 0, False, 2.0),  # Avoid promoter selling
        "Market Cap (₹Cr)": (1000, 10000, True, 1.0),
        "QoQ Sales Growth (%)": (0, 10, True, 1.2),
        "QoQ Profit Growth (%)": (0, 10, True, 1.2),
        "YoY Sales Growth (%)": (0, 15, True, 1.3),
        "YoY Profit Growth (%)": (0, 15, True, 1.3),
        "Beta": (0, 2, True, 1),
    }
    return score_using_criteria(give_metrics=metrics, scoring_criteria=scoring_criteria, calculate_weight=True)