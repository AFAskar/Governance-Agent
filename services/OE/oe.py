from typing import Literal
import math

SCALE = Literal["Unacceptable", "Low", "Fair", "Good", "Excellent", "Leader"]
WEIGHTS = [0.20, 0.05, 0.05, 0.1, 0.05, 0.1, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
SCALE_TO_INT_MAP = {
    "Unacceptable": 0,
    "Low": 1,
    "Fair": 2,
    "Good": 3,
    "Excellent": 4,
    "Leader": 5,
}


def get_high_good_percentage_scale(result: float) -> SCALE:
    if result <= 70:
        return "Unacceptable"
    elif 70 < result <= 75:
        return "Low"
    elif 75 < result <= 80:
        return "Fair"
    elif 80 < result <= 85:
        return "Good"
    elif 85 < result <= 90:
        return "Excellent"
    elif result > 95:
        return "Leader"
    else:
        raise ValueError("Invalid result value")


def get_day_low_good_scale(day_num: int | float) -> SCALE:
    if day_num <= 7:
        return "Leader"
    elif 7 < day_num <= 14:
        return "Excellent"
    elif 14 < day_num <= 21:
        return "Good"
    elif 21 < day_num <= 28:
        return "Fair"
    elif 28 < day_num <= 35:
        return "Low"
    else:
        return "Unacceptable"


def calculate_Adherence_to_the_Data_Sharing_Policy(
    Certified_attribs, total_attribs, is_classified
) -> SCALE:
    """
    Returns:
        Percentage
    """
    API_WEIGHTS = [0.8, 0.2]

    c = 1 if is_classified else 0
    num_Certified_attribs = len(Certified_attribs)
    num_total_attribs = len(total_attribs)
    result = (
        API_WEIGHTS[0] * num_Certified_attribs / num_total_attribs + API_WEIGHTS[1] * c
    ) * 100
    return get_high_good_percentage_scale(result)


def calculate_Systems_integrated_with_NDL(
    num_integrated: int, total_systems: int
) -> SCALE:
    result = num_integrated / total_systems * 100
    return get_high_good_percentage_scale(result)


def Data_sharing_agreement_processing(
    days_taken_for_approve_deny: int, total_agreements: int
) -> SCALE:
    result = days_taken_for_approve_deny / total_agreements

    return get_day_low_good_scale(result)


def final_OE_metric(
    days_taken_for_approve_deny,
    total_agreements,
    num_integrated,
    total_systems,
    total_attribs,
    Certified_attribs,
):
    scores = []
    Data_sharing_agreement_val = Data_sharing_agreement_processing(
        days_taken_for_approve_deny, total_agreements
    )
    scores.append(Data_sharing_agreement_val)
    Systems_integrated_with_NDL = calculate_Systems_integrated_with_NDL(
        num_integrated, total_systems
    )
    scores.append(Systems_integrated_with_NDL)
    Adherence_to_the_Data_Sharing_Policy = (
        calculate_Adherence_to_the_Data_Sharing_Policy(
            Certified_attribs=Certified_attribs,
            total_attribs=total_attribs,
            is_classified=False,
        )
    )
    scores.append(Adherence_to_the_Data_Sharing_Policy)
    oe = 0
    for score, weight in zip(scores, WEIGHTS):
        oe += score * weight
    return oe
