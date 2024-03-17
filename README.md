# FRHack2024 Hackathon Project README

## Description:
FRHack2024 project focuses on Challenge 3: Securing the route of the Olympic flame in terms of radio coverage.

## Team:
1. Chao Zhao
2. Luis Daniel
3. Rishika Gupta
4. Zineddine Tighidet

## Setup:
Ensure that you have Python and pip package installed on your device.

Next, install dependencies by running:
   ```bash
   pip install -r requirements.txt
  ```

## Input Files:
* Communes D1_D2_D3_pour info.xlsx
* Mesures sur D1 D2 D3.csv
* .cpg, .dbf, .prj, .shp, .shx files for:
  * Zones RURALES D1 D2 D3
  * Zones PERI URBAINES D1 D2 D3
  * Zones URBAINES D1 D2 D3
  * Shape Depts D1 D2 D3
  * Shape D1 D2 D3
 
## Instructions:
1. Run `format_directory.ipynb` to organize the files and execute the remaining code.
2. Explore and visualize the data using `visualise.ipynb`.
3. Refer to `test.ipynb` for detailed code and visualizations of the shortest path/route.
4. Start the interactive dashboard by running `python stilt.py`. The dashboard will be hosted locally on the Streamlit server.

## Note:
Ensure all input files are correctly placed in the project directory before running the scripts. For any issues or inquiries, please refer to the project documentation or contact the project team.
