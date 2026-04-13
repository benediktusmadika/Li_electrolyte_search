from __future__ import annotations

import copy
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


PAPER_BASE_COLUMNS = [
    "DOI",
    "Paper_Title",
    "Journal_Name",
    "File_Name",
    "Num_Electrolytes",
    "Tested_Electrolytes_List",
]

SUMMARY_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Is_Optimized",
    "Electrolyte_Formulation_Details",
    "esw_high",
    "esw_low",
    "ionic_conductivity",
    "viscosity",
    "density",
    "Separator",
    "Anode_Active_Material_Type",
    "Anode_Active_Material_Details",
    "Anode_Si_Content_wt",
    "Cathode_Active_Material_Type",
    "Cathode_Active_Material_Details",
    "Cell_type",
    "Cell_type_details",
    "cell_mode",
    "electrolyte_loading",
    "formation_wetting_voltage",
    "formation_wetting_time",
    "formation_wetting_temperature",
    "formation_cycle_protocol",
    "formation_initial_coulombic_efficiency",
    "Has_Cycling_Test",
    "Has_Rate_Test",
    "Has_Storage_Test",
    "Has_RPT_Test",
]

COMPOSITION_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Num_Salt",
    "Salt_Type_Abbr",
    "Salt_Type_Full",
    "Salt_Composition",
    "Salt_Composition_Type",
    "Num_Solvent",
    "Solvent_Type_Abbr",
    "Solvent_Type_Full",
    "Solvent_Ratio",
    "Solvent_Ratio_Type",
    "Num_Diluent",
    "Diluent_Type_Abbr",
    "Diluent_Type_Full",
    "Diluent_Composition",
    "Diluent_Composition_Type",
    "Num_Additive",
    "Additive_Type_Abbr",
    "Additive_Type_Full",
    "Additive_Ratio",
    "Additive_Ratio_Unit",
]

FORMATION_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "formation_wetting_voltage",
    "formation_wetting_time",
    "formation_wetting_temperature",
    "formation_cycle_protocol",
    "formation_initial_coulombic_efficiency",
]

CYCLING_RAW_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Test_ID",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "cycle_operating_voltage_range",
    "cycle_T",
    "cycle_charge_C",
    "cycle_discharge_C",
    "cycle_life_retention_pair",
    "cycle_initial_discharge_capacity",
    "cycle_discharge_capacity",
    "test_condition_distinctness",
]

RATE_RAW_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Test_ID",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "rate_operating_voltage_range",
    "rate_T",
    "rate_retention_pair",
    "test_condition_distinctness",
]

STORAGE_RAW_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Test_ID",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "storage_T",
    "storage_SOC_initial",
    "storage_initial_voltage",
    "storage_voltage",
    "storage_gas_volume",
    "storage_swelling",
    "storage_DCIR_change",
    "storage_capacity",
    "test_condition_distinctness",
]

RPT_RAW_COLUMNS = PAPER_BASE_COLUMNS + [
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Test_ID",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "rpt_operating_voltage_range",
    "rpt_T",
    "rpt_c_rate",
    "rpt_capacity",
    "rpt_resistance",
    "rpt_swelling",
    "test_condition_distinctness",
]

A2R_COMMON_COLUMNS = PAPER_BASE_COLUMNS + [
    "A2R_ID",
    "Electrolyte_ID",
    "Electrolyte_Name",
    "Test_ID",
    "Test_Type",
    "Cell_type",
    "cell_mode",
    "electrolyte_loading",
    "x_key",
    "x_value",
    "test_condition_distinctness",
    "alignment_note",
]

A2R_CYCLING_COLUMNS = A2R_COMMON_COLUMNS + [
    "cycle_operating_voltage_range",
    "cycle_T",
    "cycle_charge_C",
    "cycle_discharge_C",
    "cycle_retention",
    "cycle_initial_discharge_capacity",
    "cycle_discharge_capacity",
]

A2R_RATE_COLUMNS = A2R_COMMON_COLUMNS + [
    "rate_operating_voltage_range",
    "rate_T",
    "rate_charge_C",
    "rate_discharge_C",
    "rate_retention",
]

A2R_STORAGE_COLUMNS = A2R_COMMON_COLUMNS + [
    "storage_T",
    "storage_SOC_initial",
    "storage_initial_voltage",
    "storage_voltage",
    "storage_gas_volume",
    "storage_swelling",
    "storage_DCIR_change",
    "storage_capacity",
]

A2R_RPT_COLUMNS = A2R_COMMON_COLUMNS + [
    "rpt_operating_voltage_range",
    "rpt_T",
    "rpt_c_rate",
    "rpt_capacity",
    "rpt_resistance",
    "rpt_swelling",
]

A2R_ALL_COLUMNS = A2R_COMMON_COLUMNS + [
    "cycle_operating_voltage_range",
    "cycle_T",
    "cycle_charge_C",
    "cycle_discharge_C",
    "cycle_retention",
    "cycle_initial_discharge_capacity",
    "cycle_discharge_capacity",
    "rate_operating_voltage_range",
    "rate_T",
    "rate_charge_C",
    "rate_discharge_C",
    "rate_retention",
    "storage_T",
    "storage_SOC_initial",
    "storage_initial_voltage",
    "storage_voltage",
    "storage_gas_volume",
    "storage_swelling",
    "storage_DCIR_change",
    "storage_capacity",
    "rpt_operating_voltage_range",
    "rpt_T",
    "rpt_c_rate",
    "rpt_capacity",
    "rpt_resistance",
    "rpt_swelling",
]

EXPORT_TABLE_COLUMN_ORDER: Dict[str, List[str]] = {
    "extracted_data": SUMMARY_COLUMNS,
    "extracted_data_for_composition": COMPOSITION_COLUMNS,
    "extracted_data_for_formation": FORMATION_COLUMNS,
    "extracted_data_for_cycling_perf": CYCLING_RAW_COLUMNS,
    "extracted_data_for_rate_perform": RATE_RAW_COLUMNS,
    "extracted_data_for_storage_perf": STORAGE_RAW_COLUMNS,
    "extracted_data_for_rpt_performa": RPT_RAW_COLUMNS,
    "a2r_cycling": A2R_CYCLING_COLUMNS,
    "a2r_rate": A2R_RATE_COLUMNS,
    "a2r_storage": A2R_STORAGE_COLUMNS,
    "a2r_rpt": A2R_RPT_COLUMNS,
    "a2r_records_all": A2R_ALL_COLUMNS,
}

TEST_TYPES = ("cycling", "rate", "storage", "rpt")
COMMON_CONDITION_FIELDS = [
    "Separator",
    "Anode_Active_Material_Type",
    "Anode_Active_Material_Details",
    "Anode_Si_Content_wt",
    "Cathode_Active_Material_Type",
    "Cathode_Active_Material_Details",
    "Cell_type",
    "Cell_type_details",
    "cell_mode",
    "electrolyte_loading",
]
FORMATION_FIELDS = [
    "formation_wetting_voltage",
    "formation_wetting_time",
    "formation_wetting_temperature",
    "formation_cycle_protocol",
    "formation_initial_coulombic_efficiency",
]
TEST_CONDITION_FIELDS = [
    "cycle_operating_voltage_range",
    "cycle_T",
    "cycle_charge_C",
    "cycle_discharge_C",
    "rate_operating_voltage_range",
    "rate_T",
    "storage_T",
    "storage_SOC_initial",
    "storage_initial_voltage",
    "rpt_operating_voltage_range",
    "rpt_T",
    "rpt_c_rate",
]


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return str(value).strip() or None


def _int_or_none(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.isdigit():
            return int(cleaned)
    return None


def _yes_no_null(value: Any) -> Optional[str]:
    text = _text(value)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in {"yes", "y", "true", "1"}:
        return "yes"
    if lowered in {"no", "n", "false", "0"}:
        return "no"
    return None


def _ensure_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _ensure_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for value in values:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out


def _has_non_null_values(item: Dict[str, Optional[str]]) -> bool:
    return any(value is not None for value in item.values())


def _normalize_measurement_temperature(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {
        "value": _text(obj.get("value")),
        "unit": _text(obj.get("unit")),
        "temperature": _text(obj.get("temperature")),
    }


def _normalize_measurement_electrode(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {
        "value": _text(obj.get("value")),
        "unit": _text(obj.get("unit")),
        "electrode_type": _text(obj.get("electrode_type")),
    }


def _normalize_component(item: Any, keys: List[str]) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {key: _text(obj.get(key)) for key in keys}


def _normalize_cycle_retention_item(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {"cycle": _text(obj.get("cycle")), "retention": _text(obj.get("retention"))}


def _normalize_cycle_value_item(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {"cycle": _text(obj.get("cycle")), "value": _text(obj.get("value"))}


def _normalize_rate_item(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {
        "charge_c": _text(obj.get("charge_c")),
        "discharge_c": _text(obj.get("discharge_c")),
        "retention": _text(obj.get("retention")),
    }


def _normalize_time_value_item(item: Any) -> Dict[str, Optional[str]]:
    obj = _ensure_dict(item)
    return {"time": _text(obj.get("time")), "value": _text(obj.get("value"))}


def normalize_hierarchical_extraction(payload: Dict[str, Any], source_pdf: Path) -> Dict[str, Any]:
    data = copy.deepcopy(payload if isinstance(payload, dict) else {})

    paper = _ensure_dict(data.get("paper"))
    paper["file_name"] = _text(paper.get("file_name")) or source_pdf.name
    paper["journal_name"] = _text(paper.get("journal_name"))
    paper["doi"] = _text(paper.get("doi"))
    paper["paper_title"] = _text(paper.get("paper_title"))
    paper["num_electrolytes"] = _int_or_none(paper.get("num_electrolytes"))
    paper["tested_electrolytes_list"] = _dedupe_preserve_order(
        [_text(x) for x in _ensure_list(paper.get("tested_electrolytes_list")) if _text(x)]
    )
    paper["notes"] = _text(paper.get("notes"))
    paper["evidence"] = _dedupe_preserve_order(
        [_text(x) for x in _ensure_list(paper.get("evidence")) if _text(x)]
    )
    data["paper"] = paper

    electrolytes: List[Dict[str, Any]] = []
    for idx, raw_electrolyte in enumerate(_ensure_list(data.get("electrolytes")), start=1):
        electrolyte = _ensure_dict(raw_electrolyte)
        electrolyte["electrolyte_id"] = _text(electrolyte.get("electrolyte_id")) or f"E{idx}"
        electrolyte["Electrolyte_Name"] = _text(electrolyte.get("Electrolyte_Name"))
        electrolyte["Is_Optimized"] = _yes_no_null(electrolyte.get("Is_Optimized"))
        electrolyte["Electrolyte_Formulation_Details"] = _text(electrolyte.get("Electrolyte_Formulation_Details"))

        properties = _ensure_dict(electrolyte.get("properties"))
        properties["esw_high"] = _normalize_measurement_electrode(properties.get("esw_high"))
        properties["esw_low"] = _normalize_measurement_electrode(properties.get("esw_low"))
        properties["ionic_conductivity"] = [
            item
            for item in [
                _normalize_measurement_temperature(entry)
                for entry in _ensure_list(properties.get("ionic_conductivity"))
            ]
            if _has_non_null_values(item)
        ]
        properties["viscosity"] = [
            item
            for item in [
                _normalize_measurement_temperature(entry)
                for entry in _ensure_list(properties.get("viscosity"))
            ]
            if _has_non_null_values(item)
        ]
        properties["density"] = [
            item
            for item in [
                _normalize_measurement_temperature(entry)
                for entry in _ensure_list(properties.get("density"))
            ]
            if _has_non_null_values(item)
        ]
        electrolyte["properties"] = properties

        composition = _ensure_dict(electrolyte.get("composition"))
        composition["salts"] = [
            item
            for item in [
                _normalize_component(entry, ["abbr", "full", "composition", "composition_type"])
                for entry in _ensure_list(composition.get("salts"))
            ]
            if _has_non_null_values(item)
        ]
        composition["solvents"] = [
            item
            for item in [
                _normalize_component(entry, ["abbr", "full"])
                for entry in _ensure_list(composition.get("solvents"))
            ]
            if _has_non_null_values(item)
        ]
        composition["solvent_ratio"] = _text(composition.get("solvent_ratio"))
        composition["solvent_ratio_type"] = _text(composition.get("solvent_ratio_type"))
        composition["diluents"] = [
            item
            for item in [
                _normalize_component(entry, ["abbr", "full", "composition", "composition_type"])
                for entry in _ensure_list(composition.get("diluents"))
            ]
            if _has_non_null_values(item)
        ]
        composition["additives"] = [
            item
            for item in [
                _normalize_component(entry, ["abbr", "full", "ratio", "ratio_unit"])
                for entry in _ensure_list(composition.get("additives"))
            ]
            if _has_non_null_values(item)
        ]
        electrolyte["composition"] = composition

        common_conditions = _ensure_dict(electrolyte.get("common_conditions"))
        for field in COMMON_CONDITION_FIELDS:
            common_conditions[field] = _text(common_conditions.get(field))
        electrolyte["common_conditions"] = common_conditions

        formation = _ensure_dict(electrolyte.get("formation"))
        for field in FORMATION_FIELDS:
            formation[field] = _text(formation.get(field))
        electrolyte["formation"] = formation

        electrolyte["notes"] = _text(electrolyte.get("notes"))
        electrolyte["evidence"] = _dedupe_preserve_order(
            [_text(x) for x in _ensure_list(electrolyte.get("evidence")) if _text(x)]
        )
        electrolytes.append(electrolyte)

    data["electrolytes"] = electrolytes

    if paper["num_electrolytes"] is None and electrolytes:
        paper["num_electrolytes"] = len(electrolytes)
    if not paper["tested_electrolytes_list"]:
        paper["tested_electrolytes_list"] = _dedupe_preserve_order(
            [electrolyte["Electrolyte_Name"] for electrolyte in electrolytes if electrolyte.get("Electrolyte_Name")]
        )

    tests: List[Dict[str, Any]] = []
    per_electrolyte_counter: Dict[str, int] = defaultdict(int)
    sole_electrolyte_id = electrolytes[0]["electrolyte_id"] if len(electrolytes) == 1 else None

    for raw_test in _ensure_list(data.get("tests")):
        test = _ensure_dict(raw_test)
        electrolyte_id = _text(test.get("electrolyte_id")) or sole_electrolyte_id
        counter_key = electrolyte_id or "UNMAPPED"
        per_electrolyte_counter[counter_key] += 1
        test["electrolyte_id"] = electrolyte_id
        test["test_id"] = _text(test.get("test_id")) or f"{counter_key}_T{per_electrolyte_counter[counter_key]}"
        test_type = _text(test.get("test_type"))
        test["test_type"] = test_type.lower() if test_type else None

        test_conditions = _ensure_dict(test.get("test_conditions"))
        for field in TEST_CONDITION_FIELDS:
            test_conditions[field] = _text(test_conditions.get(field))
        test["test_conditions"] = test_conditions

        results = _ensure_dict(test.get("results"))
        results["cycle_life_retention_pair"] = [
            item
            for item in [
                _normalize_cycle_retention_item(entry)
                for entry in _ensure_list(results.get("cycle_life_retention_pair"))
            ]
            if _has_non_null_values(item)
        ]
        results["cycle_initial_discharge_capacity"] = _text(results.get("cycle_initial_discharge_capacity"))
        results["cycle_discharge_capacity"] = [
            item
            for item in [
                _normalize_cycle_value_item(entry)
                for entry in _ensure_list(results.get("cycle_discharge_capacity"))
            ]
            if _has_non_null_values(item)
        ]
        results["rate_retention_pair"] = [
            item
            for item in [
                _normalize_rate_item(entry)
                for entry in _ensure_list(results.get("rate_retention_pair"))
            ]
            if _has_non_null_values(item)
        ]
        results["storage_voltage"] = [
            item
            for item in [
                _normalize_time_value_item(entry)
                for entry in _ensure_list(results.get("storage_voltage"))
            ]
            if _has_non_null_values(item)
        ]
        results["storage_gas_volume"] = [
            item
            for item in [
                _normalize_time_value_item(entry)
                for entry in _ensure_list(results.get("storage_gas_volume"))
            ]
            if _has_non_null_values(item)
        ]
        results["storage_swelling"] = [
            item
            for item in [
                _normalize_time_value_item(entry)
                for entry in _ensure_list(results.get("storage_swelling"))
            ]
            if _has_non_null_values(item)
        ]
        results["storage_DCIR_change"] = [
            item
            for item in [
                _normalize_time_value_item(entry)
                for entry in _ensure_list(results.get("storage_DCIR_change"))
            ]
            if _has_non_null_values(item)
        ]
        results["storage_capacity"] = [
            item
            for item in [
                _normalize_time_value_item(entry)
                for entry in _ensure_list(results.get("storage_capacity"))
            ]
            if _has_non_null_values(item)
        ]
        results["rpt_capacity"] = [
            item
            for item in [
                _normalize_cycle_value_item(entry)
                for entry in _ensure_list(results.get("rpt_capacity"))
            ]
            if _has_non_null_values(item)
        ]
        results["rpt_resistance"] = [
            item
            for item in [
                _normalize_cycle_value_item(entry)
                for entry in _ensure_list(results.get("rpt_resistance"))
            ]
            if _has_non_null_values(item)
        ]
        results["rpt_swelling"] = [
            item
            for item in [
                _normalize_cycle_value_item(entry)
                for entry in _ensure_list(results.get("rpt_swelling"))
            ]
            if _has_non_null_values(item)
        ]
        test["results"] = results

        test["test_condition_distinctness"] = _text(test.get("test_condition_distinctness"))
        test["notes"] = _text(test.get("notes"))
        test["evidence"] = _dedupe_preserve_order(
            [_text(x) for x in _ensure_list(test.get("evidence")) if _text(x)]
        )
        tests.append(test)

    data["tests"] = tests
    data["document_notes"] = _text(data.get("document_notes"))
    return data


def _format_value_unit(value: Optional[str], unit: Optional[str]) -> Optional[str]:
    if value and unit:
        return f"{value} {unit}"
    if value:
        return value
    return None


def _format_esw(obj: Dict[str, Optional[str]]) -> Optional[str]:
    value = _format_value_unit(obj.get("value"), obj.get("unit"))
    if not value:
        return None
    electrode = obj.get("electrode_type") or "null"
    return f"{value} ({electrode})"


def _format_temperature_series(items: List[Dict[str, Optional[str]]]) -> Optional[str]:
    rendered: List[str] = []
    for item in items:
        value = _format_value_unit(item.get("value"), item.get("unit")) or "null"
        temperature = item.get("temperature") or "null"
        rendered.append(f"[{value}, {temperature}]")
    return ", ".join(rendered) if rendered else None


def _format_cycle_retention_pairs(items: List[Dict[str, Optional[str]]]) -> Optional[str]:
    rendered = []
    for item in items:
        cycle = item.get("cycle") or "null"
        retention = item.get("retention") or "null"
        rendered.append(f"[{cycle}, {retention}]")
    return ", ".join(rendered) if rendered else None


def _format_cycle_value_pairs(items: List[Dict[str, Optional[str]]]) -> Optional[str]:
    if not items:
        return None
    if any(item.get("cycle") for item in items):
        return ", ".join(
            f"[{item.get('cycle') or 'null'}, {item.get('value') or 'null'}]" for item in items
        )
    return ", ".join(item.get("value") or "null" for item in items)


def _format_rate_pairs(items: List[Dict[str, Optional[str]]]) -> Optional[str]:
    rendered = []
    for item in items:
        rendered.append(
            f"[{item.get('charge_c') or 'null'}, {item.get('discharge_c') or 'null'}, {item.get('retention') or 'null'}]"
        )
    return ", ".join(rendered) if rendered else None


def _format_time_value_pairs(items: List[Dict[str, Optional[str]]]) -> Optional[str]:
    rendered = []
    for item in items:
        rendered.append(f"[{item.get('time') or 'null'}, {item.get('value') or 'null'}]")
    return ", ".join(rendered) if rendered else None


def _component_list(items: List[Dict[str, Optional[str]]], key: str) -> Optional[List[Optional[str]]]:
    if not items:
        return None
    return [item.get(key) for item in items]


def _count_or_none(items: List[Any]) -> Optional[int]:
    return len(items) if items else None


def _paper_base(paper: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "DOI": paper.get("doi"),
        "Paper_Title": paper.get("paper_title"),
        "Journal_Name": paper.get("journal_name"),
        "File_Name": paper.get("file_name"),
        "Num_Electrolytes": paper.get("num_electrolytes"),
        "Tested_Electrolytes_List": paper.get("tested_electrolytes_list"),
    }


def _test_presence_flags(tests: List[Dict[str, Any]]) -> Dict[str, int]:
    present = {test_type: 0 for test_type in TEST_TYPES}
    for test in tests:
        test_type = test.get("test_type")
        if test_type in present:
            present[test_type] = 1
    return {
        "Has_Cycling_Test": present["cycling"],
        "Has_Rate_Test": present["rate"],
        "Has_Storage_Test": present["storage"],
        "Has_RPT_Test": present["rpt"],
    }


def _normalize_key(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = value.strip().lower()
    if not text or text in {"n/a", "na", "null", "none"}:
        return None
    text = text.replace("cycles", "cycle")
    if re.match(r"^\d+\s+days$", text):
        text = text.replace("days", "day")
    text = re.sub(r"\s+", " ", text)
    return text


def _make_summary_row(
    paper: Dict[str, Any],
    electrolyte: Dict[str, Any],
    tests_for_electrolyte: List[Dict[str, Any]],
) -> Dict[str, Any]:
    properties = electrolyte["properties"]
    common_conditions = electrolyte["common_conditions"]
    formation = electrolyte["formation"]
    row = _paper_base(paper)
    row.update(
        {
            "Electrolyte_ID": electrolyte.get("electrolyte_id"),
            "Electrolyte_Name": electrolyte.get("Electrolyte_Name"),
            "Is_Optimized": electrolyte.get("Is_Optimized"),
            "Electrolyte_Formulation_Details": electrolyte.get("Electrolyte_Formulation_Details"),
            "esw_high": _format_esw(properties.get("esw_high", {})),
            "esw_low": _format_esw(properties.get("esw_low", {})),
            "ionic_conductivity": _format_temperature_series(properties.get("ionic_conductivity", [])),
            "viscosity": _format_temperature_series(properties.get("viscosity", [])),
            "density": _format_temperature_series(properties.get("density", [])),
            **{field: common_conditions.get(field) for field in COMMON_CONDITION_FIELDS},
            **{field: formation.get(field) for field in FORMATION_FIELDS},
            **_test_presence_flags(tests_for_electrolyte),
        }
    )
    return row


def _make_composition_row(paper: Dict[str, Any], electrolyte: Dict[str, Any]) -> Dict[str, Any]:
    composition = electrolyte["composition"]
    salts = composition.get("salts", [])
    solvents = composition.get("solvents", [])
    diluents = composition.get("diluents", [])
    additives = composition.get("additives", [])
    row = _paper_base(paper)
    row.update(
        {
            "Electrolyte_ID": electrolyte.get("electrolyte_id"),
            "Electrolyte_Name": electrolyte.get("Electrolyte_Name"),
            "Num_Salt": _count_or_none(salts),
            "Salt_Type_Abbr": _component_list(salts, "abbr"),
            "Salt_Type_Full": _component_list(salts, "full"),
            "Salt_Composition": _component_list(salts, "composition"),
            "Salt_Composition_Type": _component_list(salts, "composition_type"),
            "Num_Solvent": _count_or_none(solvents),
            "Solvent_Type_Abbr": _component_list(solvents, "abbr"),
            "Solvent_Type_Full": _component_list(solvents, "full"),
            "Solvent_Ratio": composition.get("solvent_ratio"),
            "Solvent_Ratio_Type": composition.get("solvent_ratio_type"),
            "Num_Diluent": _count_or_none(diluents),
            "Diluent_Type_Abbr": _component_list(diluents, "abbr"),
            "Diluent_Type_Full": _component_list(diluents, "full"),
            "Diluent_Composition": _component_list(diluents, "composition"),
            "Diluent_Composition_Type": _component_list(diluents, "composition_type"),
            "Num_Additive": _count_or_none(additives),
            "Additive_Type_Abbr": _component_list(additives, "abbr"),
            "Additive_Type_Full": _component_list(additives, "full"),
            "Additive_Ratio": _component_list(additives, "ratio"),
            "Additive_Ratio_Unit": _component_list(additives, "ratio_unit"),
        }
    )
    return row


def _make_formation_row(paper: Dict[str, Any], electrolyte: Dict[str, Any]) -> Dict[str, Any]:
    common_conditions = electrolyte["common_conditions"]
    formation = electrolyte["formation"]
    row = _paper_base(paper)
    row.update(
        {
            "Electrolyte_ID": electrolyte.get("electrolyte_id"),
            "Electrolyte_Name": electrolyte.get("Electrolyte_Name"),
            "Cell_type": common_conditions.get("Cell_type"),
            "cell_mode": common_conditions.get("cell_mode"),
            "electrolyte_loading": common_conditions.get("electrolyte_loading"),
            **{field: formation.get(field) for field in FORMATION_FIELDS},
        }
    )
    return row


def _common_test_context(
    paper: Dict[str, Any],
    electrolyte: Dict[str, Any],
    test: Dict[str, Any],
) -> Dict[str, Any]:
    common_conditions = electrolyte["common_conditions"]
    return {
        **_paper_base(paper),
        "Electrolyte_ID": electrolyte.get("electrolyte_id"),
        "Electrolyte_Name": electrolyte.get("Electrolyte_Name"),
        "Test_ID": test.get("test_id"),
        "Cell_type": common_conditions.get("Cell_type"),
        "cell_mode": common_conditions.get("cell_mode"),
        "electrolyte_loading": common_conditions.get("electrolyte_loading"),
        "test_condition_distinctness": test.get("test_condition_distinctness"),
    }


def _make_cycling_raw_row(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, Any]:
    conditions = test["test_conditions"]
    results = test["results"]
    row = _common_test_context(paper, electrolyte, test)
    row.update(
        {
            "cycle_operating_voltage_range": conditions.get("cycle_operating_voltage_range"),
            "cycle_T": conditions.get("cycle_T"),
            "cycle_charge_C": conditions.get("cycle_charge_C"),
            "cycle_discharge_C": conditions.get("cycle_discharge_C"),
            "cycle_life_retention_pair": _format_cycle_retention_pairs(results.get("cycle_life_retention_pair", [])),
            "cycle_initial_discharge_capacity": results.get("cycle_initial_discharge_capacity"),
            "cycle_discharge_capacity": _format_cycle_value_pairs(results.get("cycle_discharge_capacity", [])),
        }
    )
    return row


def _make_rate_raw_row(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, Any]:
    conditions = test["test_conditions"]
    results = test["results"]
    row = _common_test_context(paper, electrolyte, test)
    row.update(
        {
            "rate_operating_voltage_range": conditions.get("rate_operating_voltage_range"),
            "rate_T": conditions.get("rate_T"),
            "rate_retention_pair": _format_rate_pairs(results.get("rate_retention_pair", [])),
        }
    )
    return row


def _make_storage_raw_row(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, Any]:
    conditions = test["test_conditions"]
    results = test["results"]
    row = _common_test_context(paper, electrolyte, test)
    row.update(
        {
            "storage_T": conditions.get("storage_T"),
            "storage_SOC_initial": conditions.get("storage_SOC_initial"),
            "storage_initial_voltage": conditions.get("storage_initial_voltage"),
            "storage_voltage": _format_time_value_pairs(results.get("storage_voltage", [])),
            "storage_gas_volume": _format_time_value_pairs(results.get("storage_gas_volume", [])),
            "storage_swelling": _format_time_value_pairs(results.get("storage_swelling", [])),
            "storage_DCIR_change": _format_time_value_pairs(results.get("storage_DCIR_change", [])),
            "storage_capacity": _format_time_value_pairs(results.get("storage_capacity", [])),
        }
    )
    return row


def _make_rpt_raw_row(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, Any]:
    conditions = test["test_conditions"]
    results = test["results"]
    row = _common_test_context(paper, electrolyte, test)
    row.update(
        {
            "rpt_operating_voltage_range": conditions.get("rpt_operating_voltage_range"),
            "rpt_T": conditions.get("rpt_T"),
            "rpt_c_rate": conditions.get("rpt_c_rate"),
            "rpt_capacity": _format_cycle_value_pairs(results.get("rpt_capacity", [])),
            "rpt_resistance": _format_cycle_value_pairs(results.get("rpt_resistance", [])),
            "rpt_swelling": _format_cycle_value_pairs(results.get("rpt_swelling", [])),
        }
    )
    return row


def _merge_series_by_key(
    series_map: Dict[str, List[Dict[str, Optional[str]]]],
    key_field: str,
    fallback_prefix: str,
) -> List[Dict[str, Any]]:
    explicit_order: List[str] = []
    display_by_key: Dict[str, str] = {}
    for items in series_map.values():
        for item in items:
            key = _normalize_key(item.get(key_field))
            if key and key not in display_by_key:
                display_by_key[key] = item.get(key_field) or key
                explicit_order.append(key)

    merged_rows: List[Dict[str, Any]] = []
    if explicit_order:
        for key in explicit_order:
            row: Dict[str, Any] = {key_field: display_by_key[key], "alignment_note": None}
            for field_name, items in series_map.items():
                match = next((item for item in items if _normalize_key(item.get(key_field)) == key), None)
                row[field_name] = match.get("value") if match else None
            merged_rows.append(row)
        return merged_rows

    max_len = max([len(items) for items in series_map.values()] or [0])
    for idx in range(max_len):
        row = {key_field: f"{fallback_prefix}_{idx + 1}", "alignment_note": f"{key_field} missing; aligned by position"}
        for field_name, items in series_map.items():
            row[field_name] = items[idx].get("value") if idx < len(items) else None
        merged_rows.append(row)
    return merged_rows


def _a2r_common(
    paper: Dict[str, Any],
    electrolyte: Dict[str, Any],
    test: Dict[str, Any],
    a2r_id: str,
    x_key: str,
    x_value: Optional[str],
    alignment_note: Optional[str],
) -> Dict[str, Any]:
    common_conditions = electrolyte["common_conditions"]
    return {
        **_paper_base(paper),
        "A2R_ID": a2r_id,
        "Electrolyte_ID": electrolyte.get("electrolyte_id"),
        "Electrolyte_Name": electrolyte.get("Electrolyte_Name"),
        "Test_ID": test.get("test_id"),
        "Test_Type": test.get("test_type"),
        "Cell_type": common_conditions.get("Cell_type"),
        "cell_mode": common_conditions.get("cell_mode"),
        "electrolyte_loading": common_conditions.get("electrolyte_loading"),
        "x_key": x_key,
        "x_value": x_value,
        "test_condition_distinctness": test.get("test_condition_distinctness"),
        "alignment_note": alignment_note,
    }


def _a2r_cycling_rows(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> List[Dict[str, Any]]:
    conditions = test["test_conditions"]
    results = test["results"]
    pairs = results.get("cycle_life_retention_pair", [])
    discharge_items = results.get("cycle_discharge_capacity", [])

    discharge_by_key = {
        _normalize_key(item.get("cycle")): item
        for item in discharge_items
        if _normalize_key(item.get("cycle")) is not None
    }
    discharge_position_fallback = not discharge_by_key and len(discharge_items) == len(pairs) and len(pairs) > 0

    rows: List[Dict[str, Any]] = []
    if pairs:
        for idx, pair in enumerate(pairs, start=1):
            cycle_label = pair.get("cycle")
            matched_discharge = None
            alignment_note = None
            if _normalize_key(cycle_label) in discharge_by_key:
                matched_discharge = discharge_by_key[_normalize_key(cycle_label)]
            elif discharge_position_fallback and idx - 1 < len(discharge_items):
                matched_discharge = discharge_items[idx - 1]
                alignment_note = "cycle_discharge_capacity aligned by position"
            row = _a2r_common(
                paper=paper,
                electrolyte=electrolyte,
                test=test,
                a2r_id=f"{test.get('test_id')}_CYC_{idx}",
                x_key="cycle",
                x_value=cycle_label,
                alignment_note=alignment_note,
            )
            row.update(
                {
                    "cycle_operating_voltage_range": conditions.get("cycle_operating_voltage_range"),
                    "cycle_T": conditions.get("cycle_T"),
                    "cycle_charge_C": conditions.get("cycle_charge_C"),
                    "cycle_discharge_C": conditions.get("cycle_discharge_C"),
                    "cycle_retention": pair.get("retention"),
                    "cycle_initial_discharge_capacity": results.get("cycle_initial_discharge_capacity"),
                    "cycle_discharge_capacity": matched_discharge.get("value") if matched_discharge else None,
                }
            )
            rows.append(row)
        return rows

    for idx, item in enumerate(discharge_items, start=1):
        row = _a2r_common(
            paper=paper,
            electrolyte=electrolyte,
            test=test,
            a2r_id=f"{test.get('test_id')}_CYC_{idx}",
            x_key="cycle",
            x_value=item.get("cycle"),
            alignment_note="cycle_life_retention_pair missing; created from cycle_discharge_capacity only",
        )
        row.update(
            {
                "cycle_operating_voltage_range": conditions.get("cycle_operating_voltage_range"),
                "cycle_T": conditions.get("cycle_T"),
                "cycle_charge_C": conditions.get("cycle_charge_C"),
                "cycle_discharge_C": conditions.get("cycle_discharge_C"),
                "cycle_retention": None,
                "cycle_initial_discharge_capacity": results.get("cycle_initial_discharge_capacity"),
                "cycle_discharge_capacity": item.get("value"),
            }
        )
        rows.append(row)
    return rows


def _a2r_rate_rows(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> List[Dict[str, Any]]:
    conditions = test["test_conditions"]
    results = test["results"]
    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(results.get("rate_retention_pair", []), start=1):
        row = _a2r_common(
            paper=paper,
            electrolyte=electrolyte,
            test=test,
            a2r_id=f"{test.get('test_id')}_RATE_{idx}",
            x_key="rate_pair",
            x_value=f"{item.get('charge_c') or 'null'} / {item.get('discharge_c') or 'null'}",
            alignment_note=None,
        )
        row.update(
            {
                "rate_operating_voltage_range": conditions.get("rate_operating_voltage_range"),
                "rate_T": conditions.get("rate_T"),
                "rate_charge_C": item.get("charge_c"),
                "rate_discharge_C": item.get("discharge_c"),
                "rate_retention": item.get("retention"),
            }
        )
        rows.append(row)
    return rows


def _a2r_storage_rows(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> List[Dict[str, Any]]:
    conditions = test["test_conditions"]
    results = test["results"]
    merged = _merge_series_by_key(
        {
            "storage_voltage": results.get("storage_voltage", []),
            "storage_gas_volume": results.get("storage_gas_volume", []),
            "storage_swelling": results.get("storage_swelling", []),
            "storage_DCIR_change": results.get("storage_DCIR_change", []),
            "storage_capacity": results.get("storage_capacity", []),
        },
        key_field="time",
        fallback_prefix="time_index",
    )
    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(merged, start=1):
        row = _a2r_common(
            paper=paper,
            electrolyte=electrolyte,
            test=test,
            a2r_id=f"{test.get('test_id')}_STO_{idx}",
            x_key="time",
            x_value=item.get("time"),
            alignment_note=item.get("alignment_note"),
        )
        row.update(
            {
                "storage_T": conditions.get("storage_T"),
                "storage_SOC_initial": conditions.get("storage_SOC_initial"),
                "storage_initial_voltage": conditions.get("storage_initial_voltage"),
                "storage_voltage": item.get("storage_voltage"),
                "storage_gas_volume": item.get("storage_gas_volume"),
                "storage_swelling": item.get("storage_swelling"),
                "storage_DCIR_change": item.get("storage_DCIR_change"),
                "storage_capacity": item.get("storage_capacity"),
            }
        )
        rows.append(row)
    return rows


def _a2r_rpt_rows(paper: Dict[str, Any], electrolyte: Dict[str, Any], test: Dict[str, Any]) -> List[Dict[str, Any]]:
    conditions = test["test_conditions"]
    results = test["results"]
    merged = _merge_series_by_key(
        {
            "rpt_capacity": results.get("rpt_capacity", []),
            "rpt_resistance": results.get("rpt_resistance", []),
            "rpt_swelling": results.get("rpt_swelling", []),
        },
        key_field="cycle",
        fallback_prefix="cycle_index",
    )
    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(merged, start=1):
        row = _a2r_common(
            paper=paper,
            electrolyte=electrolyte,
            test=test,
            a2r_id=f"{test.get('test_id')}_RPT_{idx}",
            x_key="cycle",
            x_value=item.get("cycle"),
            alignment_note=item.get("alignment_note"),
        )
        row.update(
            {
                "rpt_operating_voltage_range": conditions.get("rpt_operating_voltage_range"),
                "rpt_T": conditions.get("rpt_T"),
                "rpt_c_rate": conditions.get("rpt_c_rate"),
                "rpt_capacity": item.get("rpt_capacity"),
                "rpt_resistance": item.get("rpt_resistance"),
                "rpt_swelling": item.get("rpt_swelling"),
            }
        )
        rows.append(row)
    return rows


def build_export_tables(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    export_tables: Dict[str, List[Dict[str, Any]]] = {
        table_name: [] for table_name in EXPORT_TABLE_COLUMN_ORDER.keys()
    }
    paper = data.get("paper", {})
    electrolytes = data.get("electrolytes", [])
    tests = data.get("tests", [])

    electrolytes_by_id = {electrolyte.get("electrolyte_id"): electrolyte for electrolyte in electrolytes}
    tests_by_electrolyte: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for test in tests:
        tests_by_electrolyte[test.get("electrolyte_id")].append(test)

    for electrolyte in electrolytes:
        related_tests = tests_by_electrolyte.get(electrolyte.get("electrolyte_id"), [])
        export_tables["extracted_data"].append(_make_summary_row(paper, electrolyte, related_tests))
        export_tables["extracted_data_for_composition"].append(_make_composition_row(paper, electrolyte))
        export_tables["extracted_data_for_formation"].append(_make_formation_row(paper, electrolyte))

    for test in tests:
        electrolyte = electrolytes_by_id.get(test.get("electrolyte_id"))
        if not electrolyte:
            continue
        test_type = test.get("test_type")
        if test_type == "cycling":
            export_tables["extracted_data_for_cycling_perf"].append(_make_cycling_raw_row(paper, electrolyte, test))
            export_tables["a2r_cycling"].extend(_a2r_cycling_rows(paper, electrolyte, test))
        elif test_type == "rate":
            export_tables["extracted_data_for_rate_perform"].append(_make_rate_raw_row(paper, electrolyte, test))
            export_tables["a2r_rate"].extend(_a2r_rate_rows(paper, electrolyte, test))
        elif test_type == "storage":
            export_tables["extracted_data_for_storage_perf"].append(_make_storage_raw_row(paper, electrolyte, test))
            export_tables["a2r_storage"].extend(_a2r_storage_rows(paper, electrolyte, test))
        elif test_type == "rpt":
            export_tables["extracted_data_for_rpt_performa"].append(_make_rpt_raw_row(paper, electrolyte, test))
            export_tables["a2r_rpt"].extend(_a2r_rpt_rows(paper, electrolyte, test))

    export_tables["a2r_records_all"] = (
        export_tables["a2r_cycling"]
        + export_tables["a2r_rate"]
        + export_tables["a2r_storage"]
        + export_tables["a2r_rpt"]
    )
    return export_tables