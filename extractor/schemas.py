from __future__ import annotations

from typing import Any, Dict


JsonSchema = Dict[str, Any]


def nullable_string() -> JsonSchema:
    return {"type": ["string", "null"]}


def nullable_integer() -> JsonSchema:
    return {"type": ["integer", "null"]}


def string_array() -> JsonSchema:
    return {"type": "array", "items": {"type": "string"}}


def evidence_array() -> JsonSchema:
    return {"type": "array", "items": {"type": "string"}}


def measurement_with_temperature_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "value": nullable_string(),
            "unit": nullable_string(),
            "temperature": nullable_string(),
        },
        "required": ["value", "unit", "temperature"],
    }


def measurement_with_electrode_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "value": nullable_string(),
            "unit": nullable_string(),
            "electrode_type": nullable_string(),
        },
        "required": ["value", "unit", "electrode_type"],
    }


def salt_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "abbr": nullable_string(),
            "full": nullable_string(),
            "composition": nullable_string(),
            "composition_type": nullable_string(),
        },
        "required": ["abbr", "full", "composition", "composition_type"],
    }


def solvent_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "abbr": nullable_string(),
            "full": nullable_string(),
        },
        "required": ["abbr", "full"],
    }


def diluent_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "abbr": nullable_string(),
            "full": nullable_string(),
            "composition": nullable_string(),
            "composition_type": nullable_string(),
        },
        "required": ["abbr", "full", "composition", "composition_type"],
    }


def additive_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "abbr": nullable_string(),
            "full": nullable_string(),
            "ratio": nullable_string(),
            "ratio_unit": nullable_string(),
        },
        "required": ["abbr", "full", "ratio", "ratio_unit"],
    }


def cycle_retention_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "cycle": nullable_string(),
            "retention": nullable_string(),
        },
        "required": ["cycle", "retention"],
    }


def cycle_value_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "cycle": nullable_string(),
            "value": nullable_string(),
        },
        "required": ["cycle", "value"],
    }


def rate_retention_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "charge_c": nullable_string(),
            "discharge_c": nullable_string(),
            "retention": nullable_string(),
        },
        "required": ["charge_c", "discharge_c", "retention"],
    }


def time_value_item_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "time": nullable_string(),
            "value": nullable_string(),
        },
        "required": ["time", "value"],
    }


def paper_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "file_name": nullable_string(),
            "journal_name": nullable_string(),
            "doi": nullable_string(),
            "paper_title": nullable_string(),
            "num_electrolytes": nullable_integer(),
            "tested_electrolytes_list": string_array(),
            "notes": nullable_string(),
            "evidence": evidence_array(),
        },
        "required": [
            "file_name",
            "journal_name",
            "doi",
            "paper_title",
            "num_electrolytes",
            "tested_electrolytes_list",
            "notes",
            "evidence",
        ],
    }


def electrolyte_schema() -> JsonSchema:
    common_condition_properties = {
        "Separator": nullable_string(),
        "Anode_Active_Material_Type": nullable_string(),
        "Anode_Active_Material_Details": nullable_string(),
        "Anode_Si_Content_wt": nullable_string(),
        "Cathode_Active_Material_Type": nullable_string(),
        "Cathode_Active_Material_Details": nullable_string(),
        "Cell_type": nullable_string(),
        "Cell_type_details": nullable_string(),
        "cell_mode": nullable_string(),
        "electrolyte_loading": nullable_string(),
    }
    formation_properties = {
        "formation_wetting_voltage": nullable_string(),
        "formation_wetting_time": nullable_string(),
        "formation_wetting_temperature": nullable_string(),
        "formation_cycle_protocol": nullable_string(),
        "formation_initial_coulombic_efficiency": nullable_string(),
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "electrolyte_id": nullable_string(),
            "Electrolyte_Name": nullable_string(),
            "Is_Optimized": nullable_string(),
            "Electrolyte_Formulation_Details": nullable_string(),
            "properties": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "esw_high": measurement_with_electrode_schema(),
                    "esw_low": measurement_with_electrode_schema(),
                    "ionic_conductivity": {"type": "array", "items": measurement_with_temperature_schema()},
                    "viscosity": {"type": "array", "items": measurement_with_temperature_schema()},
                    "density": {"type": "array", "items": measurement_with_temperature_schema()},
                },
                "required": ["esw_high", "esw_low", "ionic_conductivity", "viscosity", "density"],
            },
            "composition": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "salts": {"type": "array", "items": salt_item_schema()},
                    "solvents": {"type": "array", "items": solvent_item_schema()},
                    "solvent_ratio": nullable_string(),
                    "solvent_ratio_type": nullable_string(),
                    "diluents": {"type": "array", "items": diluent_item_schema()},
                    "additives": {"type": "array", "items": additive_item_schema()},
                },
                "required": [
                    "salts",
                    "solvents",
                    "solvent_ratio",
                    "solvent_ratio_type",
                    "diluents",
                    "additives",
                ],
            },
            "common_conditions": {
                "type": "object",
                "additionalProperties": False,
                "properties": common_condition_properties,
                "required": list(common_condition_properties.keys()),
            },
            "formation": {
                "type": "object",
                "additionalProperties": False,
                "properties": formation_properties,
                "required": list(formation_properties.keys()),
            },
            "notes": nullable_string(),
            "evidence": evidence_array(),
        },
        "required": [
            "electrolyte_id",
            "Electrolyte_Name",
            "Is_Optimized",
            "Electrolyte_Formulation_Details",
            "properties",
            "composition",
            "common_conditions",
            "formation",
            "notes",
            "evidence",
        ],
    }


def test_schema() -> JsonSchema:
    test_condition_properties = {
        "cycle_operating_voltage_range": nullable_string(),
        "cycle_T": nullable_string(),
        "cycle_charge_C": nullable_string(),
        "cycle_discharge_C": nullable_string(),
        "rate_operating_voltage_range": nullable_string(),
        "rate_T": nullable_string(),
        "storage_T": nullable_string(),
        "storage_SOC_initial": nullable_string(),
        "storage_initial_voltage": nullable_string(),
        "rpt_operating_voltage_range": nullable_string(),
        "rpt_T": nullable_string(),
        "rpt_c_rate": nullable_string(),
    }
    results_properties = {
        "cycle_life_retention_pair": {"type": "array", "items": cycle_retention_item_schema()},
        "cycle_initial_discharge_capacity": nullable_string(),
        "cycle_discharge_capacity": {"type": "array", "items": cycle_value_item_schema()},
        "rate_retention_pair": {"type": "array", "items": rate_retention_item_schema()},
        "storage_voltage": {"type": "array", "items": time_value_item_schema()},
        "storage_gas_volume": {"type": "array", "items": time_value_item_schema()},
        "storage_swelling": {"type": "array", "items": time_value_item_schema()},
        "storage_DCIR_change": {"type": "array", "items": time_value_item_schema()},
        "storage_capacity": {"type": "array", "items": time_value_item_schema()},
        "rpt_capacity": {"type": "array", "items": cycle_value_item_schema()},
        "rpt_resistance": {"type": "array", "items": cycle_value_item_schema()},
        "rpt_swelling": {"type": "array", "items": cycle_value_item_schema()},
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "test_id": nullable_string(),
            "electrolyte_id": nullable_string(),
            "test_type": nullable_string(),
            "test_conditions": {
                "type": "object",
                "additionalProperties": False,
                "properties": test_condition_properties,
                "required": list(test_condition_properties.keys()),
            },
            "results": {
                "type": "object",
                "additionalProperties": False,
                "properties": results_properties,
                "required": list(results_properties.keys()),
            },
            "test_condition_distinctness": nullable_string(),
            "notes": nullable_string(),
            "evidence": evidence_array(),
        },
        "required": [
            "test_id",
            "electrolyte_id",
            "test_type",
            "test_conditions",
            "results",
            "test_condition_distinctness",
            "notes",
            "evidence",
        ],
    }


def discovery_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "electrolytes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "electrolyte_name": nullable_string(),
                        "aliases": string_array(),
                        "mentioned_test_types": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "is_candidate_optimized": nullable_string(),
                        "evidence": evidence_array(),
                    },
                    "required": [
                        "electrolyte_name",
                        "aliases",
                        "mentioned_test_types",
                        "is_candidate_optimized",
                        "evidence",
                    ],
                },
            },
            "document_notes": nullable_string(),
        },
        "required": ["electrolytes", "document_notes"],
    }


def hierarchical_extraction_schema() -> JsonSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "paper": paper_schema(),
            "electrolytes": {"type": "array", "items": electrolyte_schema()},
            "tests": {"type": "array", "items": test_schema()},
            "document_notes": nullable_string(),
        },
        "required": ["paper", "electrolytes", "tests", "document_notes"],
    }


def validation_schema() -> JsonSchema:
    issue_array = {"type": "array", "items": {"type": "string"}}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "is_valid_overall": {"type": "boolean"},
            "coverage_issues": issue_array,
            "paper_issues": issue_array,
            "electrolyte_issues": issue_array,
            "test_issues": issue_array,
            "composition_issues": issue_array,
            "a2r_preparation_issues": issue_array,
            "suggested_fixes": issue_array,
        },
        "required": [
            "is_valid_overall",
            "coverage_issues",
            "paper_issues",
            "electrolyte_issues",
            "test_issues",
            "composition_issues",
            "a2r_preparation_issues",
            "suggested_fixes",
        ],
    }