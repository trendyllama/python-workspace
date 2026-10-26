import logging
from dataclasses import dataclass
from enum import IntEnum, unique
from functools import singledispatch
from math import e
from typing import Protocol, runtime_checkable


@unique
class YearInterval(IntEnum):
    MONTHS = 12
    DAYS = 365


@runtime_checkable
class CompoundInterestCalculator(Protocol):
    years: int
    principle: float
    monthly_investment: float
    interest: float
    final_amount: float | None

    def calculate_final_amount(self) -> float: ...


class MonthlyCompoundInterestCalculator(CompoundInterestCalculator):
    def __init__(
        self, years: int, principle: float, monthly_investment: float, interest: float
    ) -> None:
        self.years = years
        self.principle = principle
        self.monthly_investment = monthly_investment
        self.interest = interest
        self.final_amount = None

    def calculate_final_amount(self) -> float:
        monthly_invest = self.monthly_investment * YearInterval.MONTHS.value
        final_ammount = 0.0

        for _ in range(self.years):
            if final_ammount == 0:
                final_ammount = self.principle

            final_ammount = (final_ammount + monthly_invest) * (1 + self.interest)

        self.final_amount = final_ammount
        return self.final_amount


class YearlyCompoundInterestCalculator(CompoundInterestCalculator):
    def __init__(
        self, years: int, principle: float, monthly_investment: float, interest: float
    ) -> None:
        self.years = years
        self.principle = principle
        self.monthly_investment = monthly_investment
        self.interest = interest
        self.final_amount = None

    def calculate_final_amount(self) -> float:
        yearly_invest = self.monthly_investment * YearInterval.MONTHS.value
        final_ammount = 0.0

        for _ in range(self.years):
            if final_ammount == 0:
                final_ammount = self.principle

            final_ammount = (final_ammount + yearly_invest) * (1 + self.interest)

        self.final_amount = final_ammount
        return self.final_amount


class DailyCompoundInterestCalculator(CompoundInterestCalculator):
    def __init__(
        self, years: int, principle: float, monthly_investment: float, interest: float
    ) -> None:
        self.years = years
        self.principle = principle
        self.monthly_investment = monthly_investment
        self.interest = interest
        self.final_amount = None

    def calculate_final_amount(self) -> float:
        daily_invest = (
            self.monthly_investment
            * YearInterval.MONTHS.value
            / YearInterval.DAYS.value
        )
        final_ammount = 0.0

        for _ in range(self.years * YearInterval.DAYS.value):
            if final_ammount == 0:
                final_ammount = self.principle

            final_ammount = (final_ammount + daily_invest) * (
                1 + self.interest / YearInterval.DAYS.value
            )
        self.final_amount = final_ammount
        return self.final_amount


class ContinuousCompoundInterestCalculator(CompoundInterestCalculator):
    """

    A class that calculates the final amount of an investment with continuous compounding interest.

    Examples:

    """

    def __init__(
        self, years: int, principle: float, monthly_investment: float, interest: float
    ) -> None:
        self.years = years
        self.principle = principle
        self.monthly_investment = monthly_investment
        self.interest = interest
        self.final_amount = None

    def calculate_final_amount(self) -> float:
        total_months = self.years * YearInterval.MONTHS.value
        monthly_invest = self.monthly_investment
        final_ammount = self.principle * e ** (self.interest * self.years)

        for _ in range(total_months):
            final_ammount += monthly_invest * e ** (
                self.interest * ((self.years - 1) / YearInterval.MONTHS.value)
            )

        self.final_amount = final_ammount

        if self.final_amount is None:
            raise ValueError

        return self.final_amount


@dataclass
class MonthlyCompoundInterestParams:
    years: int
    principle: float
    monthly_investment: float
    interest: float


@dataclass
class YearlyCompoundInterestParams:
    years: int
    principle: float
    monthly_investment: float
    interest: float

@dataclass
class DailyCompoundInterestParams:
    years: int
    principle: float
    monthly_investment: float
    interest: float

@dataclass
class ContinuousCompoundInterestParams:
    years: int
    principle: float
    monthly_investment: float
    interest: float


@singledispatch
def calculate_final_amount(params) -> float:
    msg = f"Unsupported type: {type(params)}"
    raise TypeError(msg)


@calculate_final_amount.register(MonthlyCompoundInterestParams)
def _(params: MonthlyCompoundInterestParams) -> float:

    monthly_invest = params.monthly_investment * YearInterval.MONTHS.value
    final_ammount = 0.0

    for _ in range(params.years):
        if final_ammount == 0:
            final_ammount = params.principle

        final_ammount = (final_ammount + monthly_invest) * (1 + params.interest)

    return final_ammount


@calculate_final_amount.register(YearlyCompoundInterestParams)
def _(params: YearlyCompoundInterestParams) -> float:
    yearly_invest = params.monthly_investment * YearInterval.MONTHS.value
    final_ammount = 0.0

    for _ in range(params.years):
        if final_ammount == 0:
            final_ammount = params.principle

        final_ammount = (final_ammount + yearly_invest) * (1 + params.interest)

    return final_ammount

@calculate_final_amount.register(DailyCompoundInterestParams)
def _(params: DailyCompoundInterestParams) -> float:
    daily_invest = (
        params.monthly_investment
        * YearInterval.MONTHS.value
        / YearInterval.DAYS.value
    )
    final_ammount = 0.0

    for _ in range(params.years * YearInterval.DAYS.value):
        if final_ammount == 0:
            final_ammount = params.principle

        final_ammount = (final_ammount + daily_invest) * (
            1 + params.interest / YearInterval.DAYS.value
        )

    return final_ammount

@calculate_final_amount.register(ContinuousCompoundInterestParams)
def _(params: ContinuousCompoundInterestParams) -> float:
    total_months = params.years * YearInterval.MONTHS.value
    monthly_invest = params.monthly_investment
    final_ammount = params.principle * e ** (params.interest * params.years)

    for _ in range(total_months):
        final_ammount += monthly_invest * e ** (
            params.interest * ((params.years - 1) / YearInterval.MONTHS.value)
        )

    return final_ammount




def main() -> None:
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        filename="compound_interest_log.log",
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
    )

    logger.info("New User!")
    logger.info("How many years will you be saving?")
    years = int(input("Enter years: "))
    log_msg1 = f"The user is investing for {years} years"
    logger.info(log_msg1)

    logger.info("How much money do you currently have?")
    principle = float(input("Enter how much money you currently have: "))
    log_msg2 = f"The user currently has ${principle:,.2f}"
    logger.info(log_msg2)

    logger.info("How much money do you plan on investing monthly?")
    monthly_investment = float(input("Enter ammount: "))
    log_msg3 = f"The user is investing ${monthly_investment:,.2f} monthly"
    logger.info(log_msg3)

    logger.info("What yearly intrest rate are you expecting?")
    interest = float(input("Enter the expected intrest rate in decimals (10% = 0.1): "))
    log_msg4 = f"The user's intrest rate is {interest}"
    logger.info(log_msg4)
    logger.info(" ")

    monthly_invest = monthly_investment * YearInterval.MONTHS.value
    final_ammount = 0

    for _ in range(years):
        if final_ammount == 0:
            final_ammount = principle

        final_ammount = (final_ammount + monthly_invest) * (1 + interest)

    final = f"This is how much money you will have after {years} years: ${final_ammount:,.2f}"
    logger.info(final)

    logger.info(
        "This is the user's final balance at the end of the period: %s", final_ammount
    )

    logger.info("Session over...")
    logger.info("Thank you for using our calculator")


if __name__ == "__main__":
    main()
