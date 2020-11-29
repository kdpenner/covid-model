import os
from scipy import stats as sps
import numpy as np
import pandas as pd
import requests
import io


def get_patient_data(max_delay=60):
    """ Finds every valid delay between symptom onset and report confirmation
        from the patient line list and returns all the delay samples. """
    url = "https://github.com/beoutbreakprepared/nCoV2019/raw/master/latest_data/latestdata.tar.gz"
    r = requests.get(url)

    patients = pd.read_csv(
        io.BytesIO(r.content), compression="gzip",
        parse_dates=False,
        usecols=["country", "date_onset_symptoms", "date_confirmation"],
        low_memory=False, skiprows=1,
    )

    patients.columns = ["Country", "Onset", "Confirmed"]
    patients.Country = patients.Country.astype("category")

    # There's an errant reversed date
    patients = patients.replace("01.31.2020", "31.01.2020")
    patients = patients.replace("31.04.2020", "01.05.2020")

    # Only keep if both values are present
    patients = patients.dropna()

    # Must have strings that look like individual dates
    # "2020.03.09" is 10 chars long
    is_ten_char = lambda x: x.str.len().eq(10)
    patients = patients[is_ten_char(patients.Confirmed) & is_ten_char(patients.Onset)]

    # Convert both to datetimes
    patients.Confirmed = pd.to_datetime(
        patients.Confirmed, format="%d.%m.%Y", errors="coerce"
    )
    patients.Onset = pd.to_datetime(patients.Onset, format="%d.%m.%Y", errors="coerce")

    # Only keep records where confirmed > onset
    patients = patients[patients.Confirmed > patients.Onset]

    # Mexico has many cases that are all confirmed on the same day regardless
    # of onset date, so we filter it out.
    patients = patients[patients.Country.ne("Mexico")]

    # Remove any onset dates from the last two weeks to account for all the
    # people who haven't been confirmed yet.
    patients = patients[patients.Onset < patients.Onset.max() - pd.Timedelta(days=14)]

    return patients


def get_delays_from_patient_data(max_delay=60):
    patients = get_patient_data(max_delay=max_delay)
    delays = (patients.Confirmed - patients.Onset).dt.days
    delays = delays.reset_index(drop=True)
    delays = delays[delays.le(max_delay)]
    return delays


def get_emp_delay_distribution():
    """ Returns the empirical delay distribution between symptom onset and
        confirmed positive case. """

    # The literature suggests roughly 5 days of incubation before becoming
    # having symptoms. See:
    # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7081172/
    INCUBATION_DAYS = 5

    try:
        p_delay_path = os.path.expanduser("~/.local/share/rtlive/p_delay.csv")
        p_delay = pd.read_csv(p_delay_path, squeeze=True)
    except FileNotFoundError:
        delays = get_delays_from_patient_data()
        p_delay = delays.value_counts().sort_index()
        new_range = np.arange(0, p_delay.index.max() + 1)
        p_delay = p_delay.reindex(new_range, fill_value=0)
        p_delay /= p_delay.sum()
        p_delay = (
            pd.Series(np.zeros(INCUBATION_DAYS))
            .append(p_delay, ignore_index=True)
            .rename("p_delay")
        )
        p_delay.to_csv(os.path.expanduser("~/.local/share/rtlive/p_delay.csv"), index=False)

    return p_delay

def get_fitted_delay_distribution():
    """ Infection to positive test """
    meanlog = 1.68
    sdlog = 0.92
    ps1 = sps.lognorm.cdf(np.arange(0, 70), s=sdlog, scale=np.exp(meanlog))
    ps = np.zeros(len(ps1))
    ps[1:] = np.diff(ps1)
    ps /= ps.sum()
    return ps
