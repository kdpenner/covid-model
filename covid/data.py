import pandas as pd
import arviz as az
import numpy as np


def summarize_inference_data(inference_data: az.InferenceData):
    """
    Summarizes an inference_data object
    """
    posterior = inference_data.posterior
    hdi_mass = 95.
    hpdi = az.hdi(posterior.r_t, hdi_prob=hdi_mass/100.).r_t

    observed_positive = (
      inference_data.constant_data.observed_positive.to_series())

    def scale_to_positives(data):
        return observed_positive.mean()/np.mean(data)*data

    tests = inference_data.constant_data.tests.to_series()
    normalized_positive = observed_positive/tests.clip(0.1*tests.max())

    summary = pd.DataFrame(
        data={
            "mean": posterior.r_t.mean(["draw", "chain"]),
            "median": posterior.r_t.median(["chain", "draw"]),
            f"lower_{hdi_mass}": hpdi[:, 0],
            f"upper_{hdi_mass}": hpdi[:, 1],
            "infections": scale_to_positives(
              posterior.infections.mean(["draw", "chain"])),
            "test_adjusted_positive": scale_to_positives(
              posterior.test_adjusted_positive.mean(["draw", "chain"])),
            "test_adjusted_positive_raw": (scale_to_positives(
              normalized_positive)),
            "positive": observed_positive,
            "tests": tests,
        }, index=pd.Index(posterior.date.values, name="date"))
    return summary
