import nbformat as nbf
import os

def update_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)

    # 1. Update Imports
    import_cell_found = False
    for cell in nb.cells:
        if cell.cell_type == 'code' and 'import pandas as pd' in cell.source:
            # Update imports
            source_lines = cell.source.split('\n')
            new_lines = []
            for line in source_lines:
                if 'from src.data_loader import' in line and 'preprocess_data' not in line:
                    new_lines.append(line.replace('optimize_dataframe_dtypes', 'optimize_dataframe_dtypes, preprocess_data'))
                elif 'from src.utils import' in line and 'create_derived_features' not in line:
                    # Insert features import before utils
                    new_lines.append("from src.features import create_derived_features")
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            cell.source = '\n'.join(new_lines)
            import_cell_found = True
            break

    # 2. Insert Preprocessing and Feature Engineering cells
    # We'll insert them after section 4.3 (Compare Memory Usage)
    insertion_index = -1
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'markdown' and '4.3 Compare Memory Usage' in cell.source:
            # The next code cell is the visual comparison. We insert after that.
            if i + 1 < len(nb.cells) and nb.cells[i+1].cell_type == 'code':
                insertion_index = i + 2
            else:
                insertion_index = i + 1
            break

    if insertion_index != -1:
        new_cells = [
            nbf.v4.new_markdown_cell("## 5. Week 2: Data Preprocessing & Feature Engineering\n\nNow we will apply the preprocessing and feature engineering steps developed in Week 2."),
            nbf.v4.new_markdown_cell("### 5.1 Apply Preprocessing\n\nThis handles nulls in `Flight Status` and formats the `Departure Date`."),
            nbf.v4.new_code_cell([
                "# Apply preprocessing\n",
                "df_clean = preprocess_data(df_optimized)\n",
                "\n",
                "# Check results\n",
                "print(\"Target Columns Null Check:\")\n",
                "target_cols = ['Flight Status', 'DEPARTURE_DATE']\n",
                "print(df_clean[target_cols].isnull().sum())"
            ]),
            nbf.v4.new_markdown_cell("### 5.2 Create Derived Features\n\nWe extract Month, Day of Week, Route, and Age Groups."),
            nbf.v4.new_code_cell([
                "# Create final feature-engineered dataframe\n",
                "df_final = create_derived_features(df_clean)\n",
                "\n",
                "# Display new features\n",
                "new_cols = ['MONTH_NAME', 'DAY_NAME', 'ROUTE', 'AGE_GROUP']\n",
                "display(df_final[new_cols].head())"
            ])
        ]
        
        # Shift existing section numbers
        for cell in nb.cells[insertion_index:]:
            if cell.cell_type == 'markdown':
                import re
                # Match "## 5. " and change to "## 6. ", etc.
                match = re.match(r'^(#+ )(\d+)(\..*)', cell.source)
                if match:
                    new_num = int(match.group(2)) + 1
                    cell.source = f"{match.group(1)}{new_num}{match.group(3)}"
        
        # Insert the new cells
        nb.cells[insertion_index:insertion_index] = new_cells

    # 3. Update subsequent code to use df_final
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # Replace df_optimized with df_final in subsequent sections
            # But only after our insertion point
            pass # We'll do this carefully in the actual script if needed

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print(f"Successfully updated {notebook_path}")

if __name__ == "__main__":
    update_notebook('notebooks/01_data_exploration.ipynb')
