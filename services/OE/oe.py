from typing import Literal
import math

SCALE = Literal["Unacceptable", "Low", "Fair", "Good", "Excellent", "Leader"]
WEIGHTS = {
    "DSI.OE.01": 0.05,
    "DSI.OE.02": 0.20,
    "DSI.OE.05": 0.05,
    "OD.OE.01": 0.15,
    "OD.OE.05": 0.05,
    "MCM.OE.01": 0.05,
    "MCM.OE.02": 0.05,
    "MCM.OE.03": 0.05,
    "RMD.OE.01": 0.1,
    "DQ.OE.02": 0.05,
    "DQ.OE.03": 0.05,
    "DO.OE.02": 0.1,
    "DO.OE.03": 0.05,
}
SCALE_TO_INT_MAP = {
    "Unacceptable": 0,
    "Low": 1,
    "Fair": 2,
    "Good": 3,
    "Excellent": 4,
    "Leader": 5,
}


def get_med_good_percentage_scale(result: float) -> SCALE:
    if result <= 90:
        return "Unacceptable"
    elif 90 < result <= 92:
        return "Low"
    elif 92 < result <= 94:
        return "Fair"
    elif 94 < result <= 96:
        return "Good"
    elif 96 < result <= 98:
        return "Excellent"
    elif result > 98:
        return "Leader"
    else:
        raise ValueError("Invalid result value")


def get_5_day_scale(days: int | float) -> SCALE:
    if days <= 1:
        return "Leader"
    elif 1 < days <= 2:
        return "Excellent"
    elif 2 < days <= 3:
        return "Good"
    elif 3 < days <= 4:
        return "Fair"
    elif 4 < days <= 5:
        return "Low"
    else:
        return "Unacceptable"


def get_really_high_good_percentage_scale(result: float) -> SCALE:
    if result <= 94:
        return "Unacceptable"
    elif 94 < result <= 95:
        return "Low"
    elif 95 < result <= 96:
        return "Fair"
    elif 96 < result <= 97:
        return "Good"
    elif 97 < result <= 98:
        return "Excellent"
    elif result > 98:
        return "Leader"
    else:
        raise ValueError("Invalid result value")


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
    elif result > 90:
        return "Leader"
    else:
        raise ValueError("Invalid result value")


def get_low_good_percentage_scale(result: float) -> SCALE:
    if result > 10:
        return "Unacceptable"
    elif 8 < result <= 10:
        return "Low"
    elif 6 < result <= 8:
        return "Fair"
    elif 4 < result <= 6:
        return "Good"
    elif 2 < result <= 4:
        return "Excellent"
    elif result <= 2:
        return "Leader"
    else:
        raise ValueError("Invalid result value")


def get_low_good_int_scale(result: float) -> SCALE:
    if result > 5:
        return "Unacceptable"
    elif 4 < result <= 5:
        return "Low"
    elif 3 < result <= 4:
        return "Fair"
    elif 2 < result <= 3:
        return "Good"
    elif 1 < result <= 2:
        return "Excellent"
    elif result <= 1:
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


def get_day_med_good_scale(day_num: int | float) -> SCALE:
    if day_num <= 10:
        return "Leader"
    elif 10 < day_num <= 15:
        return "Excellent"
    elif 15 < day_num <= 20:
        return "Good"
    elif 20 < day_num <= 25:
        return "Fair"
    elif 25 < day_num <= 30:
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


def calculate_Systems_integrated_with_NDL(num_integrated, total_systems) -> int:
    result = num_integrated / total_systems * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Data_sharing_agreement_processing(
    days_taken_for_approve_deny, total_agreements
) -> int:
    result = days_taken_for_approve_deny / total_agreements

    output = get_low_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Published_APIs_on_GSB(total_published_apis, total_required_apis) -> int:
    result = total_published_apis / total_required_apis * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Attributes_published_in_Tawakkalna(
    total_published_attributes, total_required_attributes
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


def Datasets_published_in_ODP(num_published_datasets, total_required_datasets) -> int:
    """OD.OE.01"""
    result = num_published_datasets / total_required_datasets * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Delay_Lag_in_refreshing_open_dataset(
    delay_in_refreshing, num_refreshes, expected_refresh_time
) -> int:
    """OD.OE.02"""
    result = delay_in_refreshing / (num_refreshes * expected_refresh_time) * 100
    output = get_low_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Reported_issues_for_the_published_datasets(
    Number_of_issues_reported_on_the_entitys_published_datasets_in_ODP, total_published
) -> int:
    """OD.OE.03"""
    result = (
        Number_of_issues_reported_on_the_entitys_published_datasets_in_ODP
        / total_published
    )

    output = get_low_good_int_scale(result)
    return SCALE_TO_INT_MAP[output]


def Delay_in_resolving_reported_issues_on_published_datasets(
    time_taken_to_resolve, expected_resolution_time
) -> int:
    """OD.OE.04"""
    result = (
        (time_taken_to_resolve - expected_resolution_time)
        / expected_resolution_time
        * 100
    )
    output = get_low_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Response_effectiveness_to_new_open_dataset_requests(
    time_taken_to_process, expected_processing_time
) -> int:
    """OD.OE.05"""
    result = (
        1
        - (time_taken_to_process - expected_processing_time) / expected_processing_time
    ) * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_domain_two_OD(*args, **kwargs) -> dict[str, int]:
    return {
        "OD.OE.01": Datasets_published_in_ODP(
            num_published_datasets=kwargs.get("num_published_datasets"),
            total_required_datasets=kwargs.get("total_required_datasets"),
        ),
        "OD.OE.02": Delay_Lag_in_refreshing_open_dataset(
            delay_in_refreshing=kwargs.get("delay_in_refreshing"),
            num_refreshes=kwargs.get("num_refreshes"),
            expected_refresh_time=kwargs.get("expected_refresh_time"),
        ),
        "OD.OE.03": Reported_issues_for_the_published_datasets(
            Number_of_issues_reported_on_the_entitys_published_datasets_in_ODP=kwargs.get(
                "Number_of_issues_reported_on_the_entitys_published_datasets_in_ODP"
            ),
            total_published=kwargs.get("total_published"),
        ),
        "OD.OE.04": Delay_in_resolving_reported_issues_on_published_datasets(
            time_taken_to_resolve=kwargs.get("time_taken_to_resolve"),
            expected_resolution_time=kwargs.get("expected_resolution_time"),
        ),
        "OD.OE.05": Response_effectiveness_to_new_open_dataset_requests(
            time_taken_to_process=kwargs.get("time_taken_to_process"),
            expected_processing_time=kwargs.get("expected_processing_time"),
        ),
    }


def Systems_cataloged_in_NDC(num_cat, total) -> int:
    """MCM.OE.01"""
    result = num_cat / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Business_attributes_defined_and_linked_in_NDC(num_defined, total) -> int:
    """MCM.OE.02"""
    result = num_defined / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Reporting_assets_defined_in_NDC(num_reporting, total) -> int:
    """MCM.OE.03"""
    result = num_reporting / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Business_attributes_linked_to_attribute_class_standards_in_NDC(
    num_linked, total
) -> int:
    """MCM.OE.04"""
    result = num_linked / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Accuracy_of_business_attribute_relationships_in_NDC(
    num_incorrect, total_defined
) -> int:
    """MCM.OE.05"""
    result = num_incorrect / total_defined * 100
    output = get_low_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_domain_three_MCM(*args, **kwargs) -> dict[str, int]:
    return {
        "MCM.OE.01": Systems_cataloged_in_NDC(
            kwargs.get("num_cat"), kwargs.get("total")
        ),
        "MCM.OE.02": Business_attributes_defined_and_linked_in_NDC(
            kwargs.get("num_defined"), kwargs.get("total")
        ),
        "MCM.OE.03": Reporting_assets_defined_in_NDC(
            kwargs.get("num_reporting"), kwargs.get("total")
        ),
        "MCM.OE.04": Business_attributes_linked_to_attribute_class_standards_in_NDC(
            kwargs.get("num_linked"), kwargs.get("total")
        ),
        "MCM.OE.05": Accuracy_of_business_attribute_relationships_in_NDC(
            kwargs.get("num_incorrect"), kwargs.get("total_defined")
        ),
    }


def Publishing_reference_entities(num_published, total_expected) -> int:
    """RMD.OE.01"""
    result = num_published / total_expected * 100
    output = get_med_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Time_taken_to_publish_new_reference_entities(time_taken, num_entities) -> int:
    """RMD.OE.02"""
    result = time_taken / num_entities
    output = get_day_med_good_scale(result)
    return SCALE_TO_INT_MAP[output]


def Time_taken_to_fix_reported_issues_in_reference_entities(
    time_taken_to_fix, total_reported_issues
) -> int:
    """RMD.OE.03"""
    result = time_taken_to_fix / total_reported_issues
    output = get_5_day_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_domain_four_RMD(*args, **kwargs) -> dict[str, int]:
    return {
        "RMD.OE.01": Publishing_reference_entities(
            num_published=kwargs.get("num_published"),
            total_expected=kwargs.get("total_expected"),
        ),
        "RMD.OE.02": Time_taken_to_publish_new_reference_entities(
            time_taken=kwargs.get("time_taken"),
            num_entities=kwargs.get("num_entities"),
        ),
        "RMD.OE.03": Time_taken_to_fix_reported_issues_in_reference_entities(
            time_taken_to_fix=kwargs.get("time_taken_to_fix"),
            total_reported_issues=kwargs.get("total_reported_issues"),
        ),
    }


def Data_Quality_index_in_GSB(num_clean, total) -> int:
    """DQ.OE.01"""
    result = num_clean / total * 100
    output = get_med_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Conformance_to_data_standards_in_NDL(num_clean, total) -> int:
    """DQ.OE.02"""
    result = num_clean / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Attributes_Availability_for_Correction_in_Tawakkalna(num_available, total) -> int:
    """DQ.OE.03"""
    result = num_available / total * 100
    output = get_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def calculate_domain_five_DQ(*args, **kwargs) -> dict[str, int]:
    return {
        "DQ.OE.01": Data_Quality_index_in_GSB(
            num_clean=kwargs.get("num_clean"), total=kwargs.get("total")
        ),
        "DQ.OE.02": Conformance_to_data_standards_in_NDL(
            num_clean=kwargs.get("num_clean"), total=kwargs.get("total")
        ),
        "DQ.OE.03": Attributes_Availability_for_Correction_in_Tawakkalna(
            num_available=kwargs.get("num_available"), total=kwargs.get("total")
        ),
    }


def Delay_in_response_time_of_GSBAPIs(
    response_time, expected_response_time, num_calls
) -> int:
    """DO.OE.01"""
    result = response_time / (expected_response_time * num_calls) * 100
    output = get_low_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Responsiveness_of_GSB_API_calls(num_failed, num_calls) -> int:
    """DO.OE.02"""
    result = (num_calls - num_failed) / num_calls * 100
    output = get_really_high_good_percentage_scale(result)
    return SCALE_TO_INT_MAP[output]


def Responsiveness_of_the_integration_solution_with_NDL(
    num_pipeline_failed, num_pipeline_calls
) -> int:
    """DO.OE.03"""
    result = (num_pipeline_calls - num_pipeline_failed) / num_pipeline_calls * 100
    output = get_really_high_good_percentage_scale(result)

    return SCALE_TO_INT_MAP[output]


def calculate_domain_six_DO(*args, **kwargs) -> dict[str, int]:
    return {
        "DO.OE.01": Delay_in_response_time_of_GSBAPIs(
            response_time=kwargs.get("response_time"),
            expected_response_time=kwargs.get("expected_response_time"),
            num_calls=kwargs.get("num_calls"),
        ),
        "DO.OE.02": Responsiveness_of_GSB_API_calls(
            num_failed=kwargs.get("num_failed"), num_calls=kwargs.get("num_calls")
        ),
        "DO.OE.03": Responsiveness_of_the_integration_solution_with_NDL(
            num_pipeline_failed=kwargs.get("num_pipeline_failed"),
            num_pipeline_calls=kwargs.get("num_pipeline_calls"),
        ),
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
    domain_2 = calculate_domain_two_OD(
        num_published_datasets=args[6],
        total_required_datasets=args[7],
        delay_in_refreshing=args[8],
        num_refreshes=args[9],
        expected_refresh_time=args[10],
        Number_of_issues_reported_on_the_entitys_published_datasets_in_ODP=args[11],
        total_published=args[12],
        time_taken_to_resolve=args[13],
        expected_resolution_time=args[14],
        time_taken_to_process=args[15],
        expected_processing_time=args[16],
    )
    domain_3 = calculate_domain_three_MCM(
        num_cat=args[17],
        total=args[18],
        num_defined=args[19],
        num_reporting=args[20],
        num_linked=args[21],
        num_incorrect=args[22],
        total_defined=args[23],
    )
    domain_4 = calculate_domain_four_RMD(
        num_published=args[24],
        total_expected=args[25],
        time_taken=args[26],
        num_entities=args[27],
        time_taken_to_fix=args[28],
        total_reported_issues=args[29],
    )
    domain_5 = calculate_domain_five_DQ(
        num_clean=args[30],
        total=args[31],
        num_available=args[32],
    )
    domain_6 = calculate_domain_six_DO(
        response_time=args[33],
        expected_response_time=args[34],
        num_calls=args[35],
        num_failed=args[36],
        num_pipeline_failed=args[37],
        num_pipeline_calls=args[38],
    )
    scores = list(domain_1.values())
    oe = 0
    for score, weight in zip(scores, WEIGHTS):
        oe += score * weight
    return oe
