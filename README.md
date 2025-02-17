# WMDA API Integration Scripts

This repository contains a set of Python scripts designed for interacting with the WMDA (World Marrow Donor Association) API, managing patient data, and performing various related tasks.

# WMDA API Integration Scripts

# **INSTALLATION**

### 1. Clone the Repository
```bash
git clone https://github.com/limia12/WMDA_Project.git
```
### 2. Install and Activate Environment
```bash
conda env create -f environment.yml
conda activate WMDA_project
```
### 3. Install required files
```bash
pip install -r requirements.txt
```
### 3. Navigate to correct directory
```bash
cd WMDA_Project/wmda_match/modules
```
# **RUNNING SCRIPTS**

## Overview

These scripts allow users to:
- Fetch, update, and manage patient and donor data from the WMDA API.
- Integrate data from an SQLite database with the API.
- Perform searches, update IDs, and retrieve patient summaries.

## Scripts

### 1. `create_patient.py`
- **Purpose**: Retrieves a Bearer token for authentication, fetches donor data from the SQLite database, and creates a new patient on the WMDA API using the retrieved data. **MUST RUN update_WMDA_ID.py AFTER CREATING PATIENT**
- **How to Run**:
  ```bash
  python3 create_patient.py

### 2. `update_WMDA_ID.py`
- **Purpose**: This script retrieves patient data and updates the wmdaId field in a local database. It checks for existing wmdaId values and only updates records where the field is empty or NULL.
- **How to Run**:
  ```bash
  python3 update_WMDA_ID.py

### 3. `update_patient.py`
- **Purpose**: This script is designed to update existing patient data on the WMDA (World Marrow Donor Association) API using information stored in an local database. 
- **How to Run**:
  ```bash
  python3 update_patient.py

### 4. `patient_list.py`
- **Purpose**: This script fetches and displays patient data from the WMDA API, including patient IDs, WMDA IDs, status, ethnicity, and request summaries.
- **How to Run**:
  ```bash
  python3 patient_list.py

### 5. `create_patient_search.py`
- **Purpose**: This script retrieves wmdaId from the local database and starts or updates a patient search on the WMDA API, updating the corresponding SearchID in the database.
- **How to Run**:
  ```bash
  python3 create_patient_search.py

### 6. `patient_search_list.py`
- **Purpose**: This script fetches the wmdaId for a given donor from the local database, and uses it to retrieve and display patient search results from the API.
- **How to Run**:
  ```bash
  python3 patient_search_list.py

### 7. `patientsummary.py`
- **Purpose**: This script fetches the SearchID for a given patient from the local database, and uses it to retrieve and display the search summary from an API.
- **How to Run**:
  ```bash
  python3 patientsummary.py

### 8. `create_table.py`
- **Purpose**: This script creates a dummy table to test these features. 
- **How to Run**:
  ```bash
  python3 patientsummary.py