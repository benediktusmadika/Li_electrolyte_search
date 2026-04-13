# Electrolyte PDF Extraction Agent

A modular, agentic LLM pipeline for extracting structured electrolyte, common-condition, formation, test, raw-result, and A2R-expanded data from many research-paper PDFs in a folder named `pdf_files`, using the API key in `gpt_api.txt`, and saving the results to CSV and Excel files.

## What it extracts

### Paper-level
- `file_name`
- `journal_name`
- `doi`
- `paper_title`
- `num_electrolytes`
- `tested_electrolytes_list`

### Electrolyte-level
- `Electrolyte_Name`
- `Is_Optimized`
- `Electrolyte_Formulation_Details`
- `esw_high`
- `esw_low`
- `ionic_conductivity`
- `viscosity`
- `density`

### Composition
- `Num_Salt`
- `Salt_Type_Abbr`
- `Salt_Type_Full`
- `Salt_Composition`
- `Salt_Composition_Type`
- `Num_Solvent`
- `Solvent_Type_Abbr`
- `Solvent_Type_Full`
- `Solvent_Ratio`
- `Solvent_Ratio_Type`
- `Num_Diluent`
- `Diluent_Type_Abbr`
- `Diluent_Type_Full`
- `Diluent_Composition`
- `Diluent_Composition_Type`
- `Num_Additive`
- `Additive_Type_Abbr`
- `Additive_Type_Full`
- `Additive_Ratio`
- `Additive_Ratio_Unit`

### Common conditions
- `Separator`
- `Anode_Active_Material_Type`
- `Anode_Active_Material_Details`
- `Anode_Si_Content_wt`
- `Cathode_Active_Material_Type`
- `Cathode_Active_Material_Details`
- `Cell_type`
- `Cell_type_details`
- `cell_mode`
- `electrolyte_loading`

### Formation
- `formation_wetting_voltage`
- `formation_wetting_time`
- `formation_wetting_temperature`
- `formation_cycle_protocol`
- `formation_initial_coulombic_efficiency`

### Test conditions and raw results
#### Cycling
- `cycle_operating_voltage_range`
- `cycle_T`
- `cycle_charge_C`
- `cycle_discharge_C`
- `cycle_life_retention_pair`
- `cycle_initial_discharge_capacity`
- `cycle_discharge_capacity`

#### Rate
- `rate_operating_voltage_range`
- `rate_T`
- `rate_retention_pair`

#### Storage
- `storage_T`
- `storage_SOC_initial`
- `storage_initial_voltage`
- `storage_voltage`
- `storage_gas_volume`
- `storage_swelling`
- `storage_DCIR_change`
- `storage_capacity`

#### RPT
- `rpt_operating_voltage_range`
- `rpt_T`
- `rpt_c_rate`
- `rpt_capacity`
- `rpt_resistance`
- `rpt_swelling`

### Shared test note
- `test_condition_distinctness`

## Workflow

For each PDF, the pipeline runs:

1. discovery
2. hierarchical extraction
3. validation
4. one repair pass if needed
5. deterministic export and A2R expansion

The model does **not** perform final A2R row explosion. It returns structured arrays, and Python expands them deterministically.

## Output files

The combined outputs are written to:

```text
outputs/combined_csv/