import nbformat as nbf

def refactor_notebook_vars(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbf.read(f, as_version=4)

    # We want to replace df_optimized with df_final in all cells AFTER our new section
    # Our new section title is "## 5. Week 2: Data Preprocessing & Feature Engineering"
    
    start_replacing = False
    for cell in nb.cells:
        if cell.cell_type == 'markdown' and '## 5. Week 2: Data Preprocessing & Feature Engineering' in cell.source:
            start_replacing = True
            continue
        
        if start_replacing and cell.cell_type == 'code':
            # Be careful not to replace df_optimized where it's being used to CREATE df_clean
            if 'df_clean = preprocess_data(df_optimized)' in cell.source:
                continue
            
            cell.source = cell.source.replace('df_optimized', 'df_final')
            # Also replace df_sample if it's used in visualizations later
            cell.source = cell.source.replace('df_sample', 'df_final')

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print(f"Successfully refactored variables in {notebook_path}")

if __name__ == "__main__":
    refactor_notebook_vars('notebooks/01_data_exploration.ipynb')
