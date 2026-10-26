from math import exp

import pytest

from random_examples.compound_interest import (
    ContinuousCompoundInterestParams,
    DailyCompoundInterestParams,
    MonthlyCompoundInterestParams,
    YearlyCompoundInterestParams,
    calculate_final_amount,
)


def test_calculate_final_amount_dispatches_for_each_parameter_type():
    years = 2
    principle = 100.0
    monthly_investment = 10.0
    interest = 0.1
    annual_amount = (
        (principle + monthly_investment * 12) * (1 + interest) + monthly_investment * 12
    ) * (1 + interest)

    daily_growth = 1 + interest / 365
    daily_deposit = monthly_investment * 12 / 365
    daily_amount = principle * daily_growth**730 + daily_deposit * daily_growth * (
        daily_growth**730 - 1
    ) / (daily_growth - 1)
    continuous_amount = principle * exp(
        interest * years
    ) + monthly_investment * years * 12 * exp(interest * (years - 1) / 12)

    cases = [
        (MonthlyCompoundInterestParams, annual_amount),
        (YearlyCompoundInterestParams, annual_amount),
        (DailyCompoundInterestParams, daily_amount),
        (ContinuousCompoundInterestParams, continuous_amount),
    ]

    for params_type, expected in cases:
        params = params_type(
            years=years,
            principle=principle,
            monthly_investment=monthly_investment,
            interest=interest,
        )

        assert calculate_final_amount(params) == pytest.approx(expected)


def test_calculate_final_amount_rejects_unsupported_input_type():
    with pytest.raises(TypeError, match="Unsupported type"):
        calculate_final_amount(object())
