# 📊 Data Directory

This directory contains data files for the ERP system.

## 📁 Structure

```
data/
├── geography/           # Geographic data files
│   ├── indian_states.xlsx
│   ├── indian_cities.xlsx
│   └── indian_pincodes.xlsx
├── templates/           # Data templates
│   └── geography_template.xlsx
└── processed/          # Processed data files
    └── processed_geography.json
```

## 🚀 Usage

1. **Add Excel Files**: Place your Excel files in the `geography/` folder
2. **Run Processing**: Use the data processing scripts to import data
3. **Update Database**: The processed data will be loaded into the database

## 📋 Excel File Format

### States File (indian_states.xlsx)
| Column | Description |
|--------|-------------|
| state_code | 2-digit state code (e.g., "27") |
| state_name | Full state name (e.g., "Maharashtra") |
| state_type | "state" or "union_territory" |
| region | "North", "South", "East", "West", "Central", "Northeast" |
| capital | State capital city |

### Cities File (indian_cities.xlsx)
| Column | Description |
|--------|-------------|
| city_name | City name |
| state_code | 2-digit state code |
| city_type | "metro", "city", "town" |
| is_major_city | TRUE/FALSE |
| latitude | Geographic latitude (optional) |
| longitude | Geographic longitude (optional) |

### Pincodes File (indian_pincodes.xlsx)
| Column | Description |
|--------|-------------|
| pincode | 6-digit pincode |
| area_name | Area/locality name |
| city_name | City name |
| state_code | 2-digit state code |
| area_type | "Post Office", "Area", "Locality" |

## 🔧 Processing Scripts

- `process_geography_data.py` - Main processing script
- `validate_data.py` - Data validation script
- `import_to_database.py` - Database import script

## 📝 Notes

- All Excel files are tracked in Git
- Data processing is automated
- Original files are preserved
- Processed data is optimized for database