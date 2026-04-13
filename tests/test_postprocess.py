from __future__ import annotations

from pathlib import Path

from extractor.postprocess import build_export_tables, normalize_hierarchical_extraction


def test_normalize_and_build_a2r_tables(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%fake\n")

    payload = {
        "paper": {
            "file_name": None,
            "journal_name": "Journal of Power Sources",
            "doi": "10.1016/j.jpowsour.2024.234567",
            "paper_title": "Example Paper",
            "num_electrolytes": None,
            "tested_electrolytes_list": [],
            "notes": None,
            "evidence": [],
        },
        "electrolytes": [
            {
                "electrolyte_id": None,
                "Electrolyte_Name": "LiFSI-1.2DME-3TTE",
                "Is_Optimized": "yes",
                "Electrolyte_Formulation_Details": "LiFSI in DME with TTE.",
                "properties": {
                    "esw_high": {"value": "5.0", "unit": "V", "electrode_type": "Pt"},
                    "esw_low": {"value": "2.25", "unit": "V", "electrode_type": "Glassy Carbon"},
                    "ionic_conductivity": [{"value": "4.1", "unit": "mS/cm", "temperature": "25 °C"}],
                    "viscosity": [{"value": "3.3", "unit": "mPa·s", "temperature": "25 °C"}],
                    "density": [{"value": "1.09", "unit": "g/cm³", "temperature": "25 °C"}],
                },
                "composition": {
                    "salts": [
                        {
                            "abbr": "LiFSI",
                            "full": "Lithium bis(fluorosulfonyl)imide",
                            "composition": "1",
                            "composition_type": "molar ratio coefficient",
                        }
                    ],
                    "solvents": [{"abbr": "DME", "full": "1,2-Dimethoxyethane"}],
                    "solvent_ratio": "1.2",
                    "solvent_ratio_type": "molar ratio coefficient",
                    "diluents": [
                        {
                            "abbr": "TTE",
                            "full": "TTE full",
                            "composition": "3",
                            "composition_type": "molar ratio coefficient",
                        }
                    ],
                    "additives": [],
                },
                "common_conditions": {
                    "Separator": "PP (Celgard 2400)",
                    "Anode_Active_Material_Type": "Graphite (Gr)",
                    "Anode_Active_Material_Details": "Artificial graphite",
                    "Anode_Si_Content_wt": "0 wt%",
                    "Cathode_Active_Material_Type": "NMC",
                    "Cathode_Active_Material_Details": "LiNi0.8Mn0.1Co0.1O2 (NMC811)",
                    "Cell_type": "coin cell",
                    "Cell_type_details": '{"coin_cell_model":"2032"}',
                    "cell_mode": "Graphite || Li (half-cell)",
                    "electrolyte_loading": "3.0 g/Ah",
                },
                "formation": {
                    "formation_wetting_voltage": "1.5 V",
                    "formation_wetting_time": "16 h",
                    "formation_wetting_temperature": "25 °C",
                    "formation_cycle_protocol": "[Formation: 1 cycle at 0.1 C between 2.0–4.65 V at 25°C] (Electrochemical Measurements)",
                    "formation_initial_coulombic_efficiency": "91.5 %",
                },
                "notes": None,
                "evidence": ["Table 1"],
            }
        ],
        "tests": [
            {
                "test_id": None,
                "electrolyte_id": None,
                "test_type": "cycling",
                "test_conditions": {
                    "cycle_operating_voltage_range": "2.7 – 4.6 V",
                    "cycle_T": "25 °C",
                    "cycle_charge_C": "0.5 C",
                    "cycle_discharge_C": "0.2 C",
                    "rate_operating_voltage_range": None,
                    "rate_T": None,
                    "storage_T": None,
                    "storage_SOC_initial": None,
                    "storage_initial_voltage": None,
                    "rpt_operating_voltage_range": None,
                    "rpt_T": None,
                    "rpt_c_rate": None,
                },
                "results": {
                    "cycle_life_retention_pair": [
                        {"cycle": "300 cycle", "retention": "81.2 %"},
                        {"cycle": "400 cycle", "retention": "80.0 %"},
                    ],
                    "cycle_initial_discharge_capacity": "154.2 mAh/g",
                    "cycle_discharge_capacity": [
                        {"cycle": "300 cycle", "value": "125.5 mAh/g"},
                        {"cycle": "400 cycle", "value": "115.5 mAh/g"},
                    ],
                    "rate_retention_pair": [],
                    "storage_voltage": [],
                    "storage_gas_volume": [],
                    "storage_swelling": [],
                    "storage_DCIR_change": [],
                    "storage_capacity": [],
                    "rpt_capacity": [],
                    "rpt_resistance": [],
                    "rpt_swelling": [],
                },
                "test_condition_distinctness": None,
                "notes": None,
                "evidence": ["Figure 3"],
            }
        ],
        "document_notes": None,
    }

    normalized = normalize_hierarchical_extraction(payload, pdf_path)
    tables = build_export_tables(normalized)

    assert normalized["paper"]["file_name"] == "paper.pdf"
    assert normalized["paper"]["num_electrolytes"] == 1
    assert normalized["electrolytes"][0]["electrolyte_id"] == "E1"
    assert normalized["tests"][0]["electrolyte_id"] == "E1"
    assert normalized["tests"][0]["test_id"].startswith("E1_T")
    assert tables["extracted_data"][0]["Has_Cycling_Test"] == 1
    assert len(tables["a2r_cycling"]) == 2
    assert tables["a2r_cycling"][0]["cycle_retention"] == "81.2 %"
    assert tables["a2r_cycling"][0]["cycle_discharge_capacity"] == "125.5 mAh/g"


def test_storage_merge_by_time(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%fake\n")

    payload = {
        "paper": {
            "file_name": None,
            "journal_name": None,
            "doi": "10.1/example",
            "paper_title": None,
            "num_electrolytes": None,
            "tested_electrolytes_list": [],
            "notes": None,
            "evidence": [],
        },
        "electrolytes": [
            {
                "electrolyte_id": "E1",
                "Electrolyte_Name": "E1",
                "Is_Optimized": None,
                "Electrolyte_Formulation_Details": None,
                "properties": {
                    "esw_high": {"value": None, "unit": None, "electrode_type": None},
                    "esw_low": {"value": None, "unit": None, "electrode_type": None},
                    "ionic_conductivity": [],
                    "viscosity": [],
                    "density": [],
                },
                "composition": {
                    "salts": [],
                    "solvents": [],
                    "solvent_ratio": None,
                    "solvent_ratio_type": None,
                    "diluents": [],
                    "additives": [],
                },
                "common_conditions": {
                    "Separator": None,
                    "Anode_Active_Material_Type": None,
                    "Anode_Active_Material_Details": None,
                    "Anode_Si_Content_wt": None,
                    "Cathode_Active_Material_Type": None,
                    "Cathode_Active_Material_Details": None,
                    "Cell_type": None,
                    "Cell_type_details": None,
                    "cell_mode": None,
                    "electrolyte_loading": None,
                },
                "formation": {
                    "formation_wetting_voltage": None,
                    "formation_wetting_time": None,
                    "formation_wetting_temperature": None,
                    "formation_cycle_protocol": None,
                    "formation_initial_coulombic_efficiency": None,
                },
                "notes": None,
                "evidence": [],
            }
        ],
        "tests": [
            {
                "test_id": "E1_T1",
                "electrolyte_id": "E1",
                "test_type": "storage",
                "test_conditions": {
                    "cycle_operating_voltage_range": None,
                    "cycle_T": None,
                    "cycle_charge_C": None,
                    "cycle_discharge_C": None,
                    "rate_operating_voltage_range": None,
                    "rate_T": None,
                    "storage_T": "55 °C",
                    "storage_SOC_initial": "100%",
                    "storage_initial_voltage": "4.6 V",
                    "rpt_operating_voltage_range": None,
                    "rpt_T": None,
                    "rpt_c_rate": None,
                },
                "results": {
                    "cycle_life_retention_pair": [],
                    "cycle_initial_discharge_capacity": None,
                    "cycle_discharge_capacity": [],
                    "rate_retention_pair": [],
                    "storage_voltage": [
                        {"time": "7 days", "value": "3.2 V"},
                        {"time": "14 days", "value": "3.15 V"},
                    ],
                    "storage_gas_volume": [{"time": "7 days", "value": "15 mL"}],
                    "storage_swelling": [{"time": "14 days", "value": "5 %"}],
                    "storage_DCIR_change": [],
                    "storage_capacity": [
                        {"time": "7 days", "value": "99 %"},
                        {"time": "14 days", "value": "98.5 %"},
                    ],
                    "rpt_capacity": [],
                    "rpt_resistance": [],
                    "rpt_swelling": [],
                },
                "test_condition_distinctness": None,
                "notes": None,
                "evidence": [],
            }
        ],
        "document_notes": None,
    }

    normalized = normalize_hierarchical_extraction(payload, pdf_path)
    tables = build_export_tables(normalized)

    assert len(tables["a2r_storage"]) == 2
    assert tables["a2r_storage"][0]["x_value"] == "7 days"
    assert tables["a2r_storage"][0]["storage_voltage"] == "3.2 V"