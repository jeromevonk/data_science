@echo off

set "dataset=full"
REM set "dataset=sample"

REM Step 1: Audit
cd "2. Auditing"
python 1_count_tags.py %dataset%
python 2_tag_potential_problems.py %dataset%
python 3_count_unique_users.py %dataset%
python 4_improve_street_types.py %dataset%
cd ..

REM Step 2: Prepare the database
cd "3. Preparing_database"
python preparing_database.py %dataset%
cd ..

REM Step 3: Create the database
cd "4. Database"
python create_database.py
cd ..

REM Step 4: Perform some queries
cd "4. Database"
python perform_queries.py
cd ..