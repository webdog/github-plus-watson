# Purpose

This serves as the repository for all the source code to generate all the example data for the Collaboration Data lightning talk at World of Watson.  

# Gathering the data:  

API scripts are written in `python 3.5.x`, specifically using the anaconda distribution.  
Third party dependencies are defined in the requirements.txt file in root directory.  

The script (gh-reports.py) is run with command line arguments. The arguments are as follows:  

-r - Specify the repository name (**Required**)  
-o - Specify the organization name (If not specified, will use the user's repositories)  
-u - User account (**Required**)  
-t [1-8] - Which report you want to run (**Required**)  
  - 1 : "Languages committed per User",  
  - 2 : "Ratio of Merged/Unmerged Pull Requests (Status=All)",  
  - 3 : "Ratio of Merged/Unmerged Pull Requests (Status=Closed)",  
  - 4 : "Contribution Count of last 100 Pull Requests",
  - 5 : "Repository Maintenance (Documentation submission vs Code Submission",  
  - 6 : "Issues open by Assignee",  
  - 7 : "Number of Comments on Closed Issues",  
  - 8 : "Analyze sentiment of conversations in last 100 Pull Requests"  
-e [True|False] - Specify GitHub Enterprise instance. False by default  

-p - Public repo vs org repo. Not currently used.  
-s - `Search` Unused arg for later reports forthcoming  

Example usage:  

`./gh-reports.py -r hubot -o github -u webdog -t 1`  

You will then be prompted for a `personal access token` which you can generate in your GitHub Profile.  

Reports are then dropped in the ./reports/ directory as pipe-delimited csvs. Note: CSVs are not generated in any specific column order. So you may experience different column positions after each run.  

Example usage is then shown in ipython notebooks under the `reports` directory.  
Note: This software is in a very alpha state. Happy hacking!  
