def calculate_risk_score(
    severity: float,
    asset_criticality: float,
    exposure: float,
    exploitability: float,
    compensating_control: float,
    weights: dict[str, float],
) -> float:
    return (
        weights['a'] * severity
        + weights['b'] * asset_criticality
        + weights['c'] * exposure
        + weights['d'] * exploitability
        - weights['e'] * compensating_control
    )
