from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfWriter

from extractor.agent import ElectrolyteExtractionAgent
from extractor.config import ApiConfig


class FakeClient:
    def upload_file(self, pdf_path: Path):
        return type("UploadedFile", (), {"file_id": "file_fake_123", "filename": pdf_path.name})()

    def delete_file(self, file_id: str) -> None:
        return None

    def create_structured_response(
        self,
        *,
        file_id,
        system_prompt,
        user_prompt,
        schema_name,
        schema,
        model=None,
        reasoning_effort=None,
    ):
        if schema_name == "electrolyte_discovery":
            return {
                "electrolytes": [
                    {
                        "electrolyte_name": "LiFSI-1.2DME-3TTE",
                        "aliases": ["optimized electrolyte"],
                        "mentioned_test_types": ["cycling"],
                        "is_candidate_optimized": "yes",
                        "evidence": ["Table 1"],
                    }
                ],
                "document_notes": None,
            }

        if schema_name in {"electrolyte_hierarchical_extraction", "electrolyte_hierarchical_repair"}:
            return {
                "paper": {
                    "file_name": None,
                    "journal_name": "Journal of Power Sources",
                    "doi": "10.1016/j.jpowsour.2024.234567",
                    "paper_title": "Example Paper",
                    "num_electrolytes": 1,
                    "tested_electrolytes_list": ["LiFSI-1.2DME-3TTE"],
                    "notes": None,
                    "evidence": ["Title page"],
                },
                "electrolytes": [
                    {
                        "electrolyte_id": "E1",
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
                        "test_id": "E1_T1",
                        "electrolyte_id": "E1",
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

        if schema_name == "electrolyte_hierarchical_validation":
            return {
                "is_valid_overall": True,
                "coverage_issues": [],
                "paper_issues": [],
                "electrolyte_issues": [],
                "test_issues": [],
                "composition_issues": [],
                "a2r_preparation_issues": [],
                "suggested_fixes": [],
            }

        raise AssertionError(f"Unexpected schema_name: {schema_name}")


def test_agent_process_folder_smoke(tmp_path: Path, monkeypatch) -> None:
    pdf_dir = tmp_path / "pdf_files"
    pdf_dir.mkdir()
    pdf_path = pdf_dir / "paper1.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with pdf_path.open("wb") as handle:
        writer.write(handle)

    out_dir = tmp_path / "outputs"
    monkeypatch.setattr("extractor.agent.build_llm_client", lambda config: FakeClient())

    agent = ElectrolyteExtractionAgent(ApiConfig(api_key="sk-test", delete_remote_file_after_run=False))
    paths = agent.process_folder(pdf_dir, out_dir)

    assert (paths.combined_csv / "extracted_data.csv").exists()
    assert (paths.combined_csv / "extracted_data_for_composition.csv").exists()
    assert (paths.combined_csv / "a2r_cycling.csv").exists()
    assert (paths.final_json / "paper1.json").exists()

    payload = json.loads((paths.final_json / "paper1.json").read_text(encoding="utf-8"))
    assert payload["paper"]["file_name"] == "paper1.pdf"
    assert payload["electrolytes"][0]["Electrolyte_Name"] == "LiFSI-1.2DME-3TTE"