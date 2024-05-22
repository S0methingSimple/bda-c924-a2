# COMP90024 Assignment 2 - Decoding Melbourne's Housing Market

This project implements a big data architecture for analyzing housing prices and social media sentiment on the Melbourne Research Cloud (MRC).

## Key Functionalities

1. Bulk ingest housing price data from a source (specified in data)
2. Daily extraction of relevant toots (social media messages) containing housing price keywords using serverless functions (`backend/harvester`)
3. Processing and storing harvested toots in Elasticsearch
4. Providing access to both static housing data and processed toots through RESTful APIs (`backend/api`)
5. Enabling data exploration and analysis using Jupyter Notebooks (`frontend`)

## Project Structure

- frontend: Contains Jupyter notebooks for data analysis and visualization.
- backend: Houses the application's backend code:
  - Harvester functions for extracting toots (serverless functions).
  - API code for accessing and managing data.
- data: Stores any static data required for analysis (e.g., initial housing price dataset).
- docs: Includes documentation like API reference and reports related to the project.

## Getting Started

### Frontend

The frontend are structured with ipynb file. Just simply run it to start analysis of data.

### Backend

The backend of the project is deployed entirely with Fission specification, the default specifications are already generated, modify as required.

1. Install the required helm charts, refer to installation guide [here](https://gitlab.unimelb.edu.au/feit-comp90024/comp90024/-/blob/master/installation/README.md).
2. Batch ingest the data of the project

   1. List all index in Elasticsearch
        ``` bash
      (
          cd ./backend/batch
          python3 ShowIndexList.py
      )
      ```
   2. Update Mastodon data to Elasticsearch manually
      1. Need manually change the start and end date (line 48&49)as you want
           ``` bash 
         start_date = datetime(2010, 1, 1, tzinfo=timezone.utc)
         end_date = datetime(2024, 5, 1, tzinfo=timezone.utc)
           ```
      2. Run UpdateMastodonData.py
         ``` bash 
         (
             cd ./backend/batch
             python3 UpdateMastodonData.py
         )
           ```
   3. Upload Twitter data
      ``` bash
      (
          cd ./backend/batch
          python3 pushTwitter.py
      )
      ```

3. Update specific Elasticsearch configuration and apply them (`backend/manifest`).

    ``` bash
    kubectl apply -f ./backend/manifests/es_confmap.yaml
    ```

4. Deploy harvester to fission.

    ``` bash
    (
        cd ./backend/harvester
        fission spec apply --specdir ./specs --wait
    )
    ```

5. Deploy API to fission.

    ``` bash
    (
        cd ./backend/api
        fission spec apply --specdir ./specs --wait
    )
    ```

6. Test API. Refer to the API [documentation](https://docs.google.com/document/d/1xTyMfZxW4E-Otca22jtNjIg3nUjKx1a2u48fiU56yGs/edit#heading=h.i099w3d8471b) for usage.

    ``` bash
    kubectl port-forward service/router -n fission 9090:80
    curl "http://127.0.0.1:9090/toot/housing_price?start_date=2023-01-01&end_date=2023-12-01&type=raw"  | jq '.'  
    ```
   
7. Test harvester and show time trigger.

    ``` bash
   fission fn test --name harvester 
   fisson timetrigger list
    ```