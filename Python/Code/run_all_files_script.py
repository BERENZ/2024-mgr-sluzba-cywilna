import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

# List of notebook filenames to execute sequentially.
notebooks_to_run = [
    'Initial_data_cleansing.ipynb',
    'Further_data_cleansing.ipynb',
    'kprm_data_merge_1.ipynb',
    'teryt.ipynb',
    'main_and_kprm_data_merge_2.ipynb',
    'maps.ipynb',
    'bdl_merge.ipynb',
    'feature_engineering.ipynb'
]

def run_notebooks(notebooks, path='.'):
    for notebook_name in notebooks:
        notebook_path = os.path.join(path, notebook_name)
        print(f"Running {notebook_path}...")

        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

        try:
            ep.preprocess(nb, {'metadata': {'path': path}})
            print(f"Successfully ran {notebook_name}")
        except Exception as e:
            print(f"Error running {notebook_name}: {e}")

if __name__ == '__main__':
    run_notebooks(notebooks_to_run)
