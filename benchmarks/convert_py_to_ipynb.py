"""Utility to convert Python benchmark script to a Jupyter Notebook."""

import nbformat as nbf
from pathlib import Path


def convert():
  input_file = Path("benchmark_run.py")
  if not input_file.exists():
    # Using logging here would be better but keeping it simple for now.
    return

  nb = nbf.v4.new_notebook()
  nb.cells = []

  with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

  current_cell_source = []

  for line in lines:
    if line.strip().startswith("# %%"):
      if current_cell_source:
        nb.cells.append(
            nbf.v4.new_code_cell("".join(current_cell_source).strip())
        )
        current_cell_source = []
    else:
      current_cell_source.append(line)

  if current_cell_source:
    nb.cells.append(nbf.v4.new_code_cell("".join(current_cell_source).strip()))

  # Post-processing: Replace asyncio.run(main()) with await main()
  # We iterate through all cells to find the one with the execution block
  for cell in nb.cells:
    if "asyncio.run(main())" in cell.source:
      cell.source = cell.source.replace("asyncio.run(main())", "await main()")

  output_file = input_file.with_suffix(".ipynb")
  with open(output_file, "w", encoding="utf-8") as f:
    nbf.write(nb, f)


if __name__ == "__main__":
  convert()
