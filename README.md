# H1B-Data-Importer

- Currently, imports data from https://h1bdata.info/index.php for further analysis. 
- Provides minimal filtering options for cities, years, job titles, and salary cutoffs.
- Can potentially use the data files provided directly at the source (https://www.foreignlaborcert.doleta.gov/performancedata.cfm#dis) for better data with extra columns.

If using Anaconda,
- Run "conda env create -f environment.yml" on a terminal.
- This creates an environment "h1bdata" with the requisite dependencies.
- Activate the environment and run "python data_fetcher.py -h" to view the expected/optional arguments.
