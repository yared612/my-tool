import numpy as np
import pulp


def define_employees():
    employees = {
        # day shift
        "A": {"level": "senior", "shift": "day", "off_days": [2, 3], "preferred_off_days": [2, 3]},
        "B": {"level": "senior", "shift": "day", "off_days": [], "preferred_off_days": []},
        "C": {"level": "senior", "shift": "day", "off_days": [], "preferred_off_days": []},
        "D": {
            "level": "mid",
            "shift": "day",
            "off_days": [10, 11, 12, 13],
            "preferred_off_days": [10, 11, 12, 13],
        },
        "E": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "F": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "G": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "H": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "I": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "J": {"level": "mid", "shift": "day", "off_days": [], "preferred_off_days": []},
        "K": {
            "level": "junior",
            "shift": "day",
            "off_days": [13, 14, 15],
            "preferred_off_days": [13, 14, 15],
        },
        "L": {"level": "junior", "shift": "day", "off_days": [], "preferred_off_days": []},
        # swing shift
        "M": {
            "level": "senior",
            "shift": "swing",
            "off_days": [5, 6, 7, 8],
            "preferred_off_days": [5, 6, 7, 8],
        },
        "N": {"level": "senior", "shift": "swing", "off_days": [], "preferred_off_days": []},
        "O": {
            "level": "mid",
            "shift": "swing",
            "off_days": [12, 13, 14],
            "preferred_off_days": [12, 13, 14],
        },
        "P": {"level": "mid", "shift": "swing", "off_days": [], "preferred_off_days": []},
        "Q": {"level": "mid", "shift": "swing", "off_days": [], "preferred_off_days": []},
        "R": {
            "level": "junior",
            "shift": "swing",
            "off_days": [20, 21, 22],
            "preferred_off_days": [20, 21, 22],
        },
        # night shift
        "S": {
            "level": "senior",
            "shift": "night",
            "off_days": [5, 6, 7],
            "preferred_off_days": [5, 6, 7],
        },
        "T": {"level": "senior", "shift": "night", "off_days": [], "preferred_off_days": []},
        "U": {
            "level": "mid",
            "shift": "night",
            "off_days": [19, 20, 21],
            "preferred_off_days": [19, 20, 21],
        },
        "V": {"level": "mid", "shift": "night", "off_days": [], "preferred_off_days": []},
        "W": {
            "level": "junior",
            "shift": "night",
            "off_days": [25, 26, 27],
            "preferred_off_days": [25, 26, 27],
        },
    }
    return employees


def define_shift_requirements():
    shift_requirements = {
        "day": [
            7,
            7,
            7,
            7,
            6,
            6,
            7,
            7,
            7,
            7,
            7,
            6,
            6,
            7,
            7,
            7,
            7,
            7,
            6,
            6,
            7,
            7,
            7,
            7,
            7,
            6,
            6,
            7,
            7,
            7,
            7,
        ],
        "swing": [4] * 31,
        "night": [3] * 31,
    }
    return shift_requirements


def create_problem():
    prob = pulp.LpProblem("Shift Scheduling", pulp.LpMinimize)
    return prob


def define_variables(employees, shift_requirements):
    schedule = pulp.LpVariable.dicts(
        "schedule",
        [
            (emp, day, shift)
            for emp in employees
            for day in range(len(shift_requirements["day"]))
            for shift in shift_requirements
        ],
        cat="Binary",
    )
    return schedule


def add_constraints(prob, schedule, employees, shift_requirements, max_consecutive_days):
    num_days = len(shift_requirements["day"])
    shifts = list(shift_requirements.keys())

    # condition1：check all shifts are correct
    for day in range(num_days):
        for shift in shifts:
            prob += (
                pulp.lpSum(
                    [
                        schedule[(emp, day, shift)]
                        for emp in employees
                        if employees[emp]["shift"] == shift
                    ]
                )
                == shift_requirements[shift][day],
                f"ShiftRequirement_{shift}_Day{day}",
            )

    # condition2：check all employees work day are correct
    for emp in employees:
        shift = employees[emp]["shift"]
        for day in range(num_days - max_consecutive_days):
            prob += (
                pulp.lpSum(
                    [schedule[(emp, day + d, shift)] for d in range(max_consecutive_days + 1)]
                )
                <= max_consecutive_days,
                f"MaxConsecutive_{emp}_Day{day}",
            )

    # condition3：employees off days
    for emp in employees:
        for off_day in employees[emp]["off_days"]:
            if off_day - 1 in range(num_days):
                shift = employees[emp]["shift"]
                prob += schedule[(emp, off_day - 1, shift)] == 0, f"OffDay_{emp}_Day{off_day}"

    # condition4：Must have one senior employee in each shift
    for day in range(num_days):
        for shift in shifts:
            prob += (
                pulp.lpSum(
                    [
                        schedule[(emp, day, shift)]
                        for emp in employees
                        if employees[emp]["level"] == "senior" and employees[emp]["shift"] == shift
                    ]
                )
                >= 1,
                f"Senior_{shift}_Day{day}",
            )

    # add var
    is_five_day_streak = pulp.LpVariable.dicts(
        "is_five_day_streak",
        [(emp, day) for emp in employees for day in range(num_days - 4)],
        cat="Binary",
    )

    is_one_day_streak = pulp.LpVariable.dicts(
        "is_one_day_streak",
        [(emp, day) for emp in employees for day in range(num_days)],
        cat="Binary",
    )

    # condition5：Define five day streak and one day streak
    for emp in employees:
        shift = employees[emp]["shift"]
        for day in range(num_days - 4):
            # If an employee work 5 consecutive days, is_five_day_streak = 1
            prob += is_five_day_streak[(emp, day)] <= schedule[(emp, day, shift)]
            prob += is_five_day_streak[(emp, day)] <= schedule[(emp, day + 1, shift)]
            prob += is_five_day_streak[(emp, day)] <= schedule[(emp, day + 2, shift)]
            prob += is_five_day_streak[(emp, day)] <= schedule[(emp, day + 3, shift)]
            prob += is_five_day_streak[(emp, day)] <= schedule[(emp, day + 4, shift)]
            prob += (
                is_five_day_streak[(emp, day)]
                >= schedule[(emp, day, shift)]
                + schedule[(emp, day + 1, shift)]
                + schedule[(emp, day + 2, shift)]
                + schedule[(emp, day + 3, shift)]
                + schedule[(emp, day + 4, shift)]
                - 4,
                f"FiveDayStreak_{emp}_Day{day}",
            )

    # condition6：Define only work 1 day streak
    for emp in employees:
        shift = employees[emp]["shift"]
        for day in range(num_days):
            if day == 0:
                prev_day_off = 1
            else:
                prev_day_off = 1 - schedule[(emp, day - 1, shift)]
            if day == num_days - 1:
                next_day_off = 1
            else:
                next_day_off = 1 - schedule[(emp, day + 1, shift)]
            prob += (
                is_one_day_streak[(emp, day)]
                >= schedule[(emp, day, shift)] - (1 - prev_day_off) - (1 - next_day_off),
                f"OneDayStreakDef1_{emp}_Day{day}",
            )
            prob += (
                is_one_day_streak[(emp, day)] <= schedule[(emp, day, shift)],
                f"OneDayStreakDef2_{emp}_Day{day}",
            )
            prob += (
                is_one_day_streak[(emp, day)] <= prev_day_off,
                f"OneDayStreakDef3_{emp}_Day{day}",
            )
            prob += (
                is_one_day_streak[(emp, day)] <= next_day_off,
                f"OneDayStreakDef4_{emp}_Day{day}",
            )

    return is_five_day_streak, is_one_day_streak


def add_objective_function(
    prob, schedule, employees, shift_requirements, is_five_day_streak, is_one_day_streak
):
    # Original objective function： Maximize the employees' expected off days
    prob += (
        pulp.lpSum(
            [
                (1 - schedule[(emp, day - 1, employees[emp]["shift"])])
                for emp in employees
                for day in employees[emp]["preferred_off_days"]
                if day - 1 in range(len(shift_requirements["day"]))
            ]
        )
        # Add Minimize the employees' expected off days
        + pulp.lpSum(
            [
                is_five_day_streak[(emp, day)] * 10
                for emp in employees
                for day in range(len(shift_requirements["day"]) - 4)
            ]
        )
        + pulp.lpSum(
            [
                is_one_day_streak[(emp, day)] * 5
                for emp in employees
                for day in range(len(shift_requirements["day"]))
            ]
        )
    )


def solve_problem(prob):
    prob.solve()


def get_schedule_result(schedule, employees, shift_requirements):
    num_days = len(shift_requirements["day"])
    shifts = list(shift_requirements.keys())

    schedule_result = {}
    for day in range(num_days):
        day_str = f"Day {day + 1}"
        schedule_result[day_str] = {}
        for shift in shifts:
            shift_employees = []
            for emp in employees:
                if pulp.value(schedule[(emp, day, shift)]) == 1:
                    shift_employees.append(emp)
            schedule_result[day_str][shift] = shift_employees
    return schedule_result
