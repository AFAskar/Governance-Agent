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
) -> int:
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
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_Systems_integrated_with_NDL(
    num_integrated: int, total_systems: int
) -> int:
    result = num_integrated / total_systems * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Data_sharing_agreement_processing(
    days_taken_for_approve_deny: int, total_agreements: int
) -> int:
    result = days_taken_for_approve_deny / total_agreements

    output = get_day_low_good_scale(result)
    return SCALE_TO_INT_MAP[output]


def Published_APIs_on_GSB(total_published_apis: int, total_required_apis: int) -> int:
    result = total_published_apis / total_required_apis * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Attributes_published_in_Tawakkalna(
    total_published_attributes: int, total_required_attributes: int
) -> int:
    result = total_published_attributes / total_required_attributes * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_domain_one(*args, **kwargs) -> dict[str, int]:
    return {
        "DSI.OE.01": calculate_Adherence_to_the_Data_Sharing_Policy(
            Certified_attribs=kwargs.get("Certified_attribs"),
            total_attribs=kwargs.get("total_attribs"),
            is_classified=kwargs.get("is_classified"),
        ),
        "DSI.OE.02": calculate_Systems_integrated_with_NDL(
            num_integrated=kwargs.get("num_integrated"),
            total_systems=kwargs.get("total_systems"),
        ),
        "DSI.OE.03": Data_sharing_agreement_processing(
            days_taken_for_approve_deny=kwargs.get("days_taken_for_approve_deny"),
            total_agreements=kwargs.get("total_agreements"),
        ),
        "DSI.OE.04": Published_APIs_on_GSB(
            total_published_apis=kwargs.get("total_published_apis"),
            total_required_apis=kwargs.get("total_required_apis"),
        ),
        "DSI.OE.05": Attributes_published_in_Tawakkalna(
            total_published_attributes=kwargs.get("total_published_attributes"),
            total_required_attributes=kwargs.get("total_required_attributes"),
        ),
    }


def calculate_domain_two() -> dict[str, int]:
    return {
        "OD.OE.01": 0,
        "OD.OE.02": 0,
        "OD.OE.03": 0,
        "OD.OE.04": 0,
        "OD.OE.05": 0,
    }


def calculate_domain_three() -> dict[str, int]:
    return {
        "MCM.OE.01": 0,
        "MCM.OE.02": 0,
        "MCM.OE.03": 0,
        "MCM.OE.04": 0,
        "MCM.OE.05": 0,
    }


def calculate_domain_four() -> dict[str, int]:
    return {
        "RMD.OE.01": 0,
        "RMD.OE.02": 0,
        "RMD.OE.03": 0,
    }


def calculate_domain_five() -> dict[str, int]:
    return {
        "DQ.OE.01": 0,
        "DQ.OE.02": 0,
        "DQ.OE.03": 0,
    }


def calculate_domain_six() -> dict[str, int]:
    return {
        "DO.OE.01": 0,
        "DO.OE.02": 0,
        "DO.OE.03": 0,
    }


def final_OE_metric(*args):
    domain_1 = calculate_domain_one(
        Certified_attribs=args[0],
        total_attribs=args[1],
        num_integrated=args[2],
        total_systems=args[3],
        days_taken_for_approve_deny=args[4],
        total_agreements=args[5],
    )
    scores = list(domain_1.values())
    oe = 0
    for score, weight in zip(scores, WEIGHTS):
        oe += score * weight
    return oe
