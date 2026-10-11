from math import isclose, isfinite
from numbers import Real


def compare_numeric(expected: Real, observed: Real, tolerance: float = 1e-9) -> dict:
    """Compare an observed metric against a trusted reference value."""
    if isinstance(expected, bool) or isinstance(observed, bool):
        return {
            "status": "INCONCLUSIVE",
            "expected": expected,
            "observed": observed,
            "reason": "Boolean values are not valid numeric metrics.",
        }

    if not isinstance(expected, Real) or not isinstance(observed, Real):
        return {
            "status": "INCONCLUSIVE",
            "expected": str(expected),
            "observed": str(observed),
            "reason": "Both values must be numeric.",
        }

    if not isfinite(float(expected)) or not isfinite(float(observed)):
        return {
            "status": "INCONCLUSIVE",
            "expected": str(expected),
            "observed": str(observed),
            "reason": "Non-finite numeric values cannot be verified.",
        }

    passed = isclose(
        float(expected),
        float(observed),
        rel_tol=tolerance,
        abs_tol=tolerance,
    )

    return {
        "status": "VERIFIED" if passed else "FAILED",
        "expected": float(expected),
        "observed": float(observed),
        "reason": (
            "Observed value matches the reference within tolerance."
            if passed
            else "Observed value differs from the reference."
        ),
    }
