# Week 1: Docker & Terraform (Azure Edition)
This repository contains my solution for Week 1 of the Data Engineering Zoomcamp. While the course uses GCP, I locally ran on Fedora 43 and used resources of Ms Azure.

## Table of Contents
* [Terraform Setup](#terraform-part)
* [Docker & Python Ingestion](#docker--python)
* [SQL Homework Solutions](#sql-commands-for-homework-questions)
* [How to Run](#how-to-run)

## Terraform part![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?logo=terraform&logoColor=white)

Instead of the standard Google Cloud setup, i used azure ones.<br>

google provider	-> azurerm provider<br>
Project	-> Resource Group (azurerm_resource_group)<br>
GCS Bucket -> Data Lake Storage Gen2 (azurerm_storage_account with HNS)<br>
BigQuery -> Azure Synapse Analytics (azurerm_synapse_workspace)<br>

The Terraform configuration is split into two files to follow best practices:<br>
    1. main.tf: Defines the resource logic.<br>
    2. variables.tf: Stores parameters and ensures sensitive data (like SQL passwords) aren't hardcoded.<br>

Deployment process/steps

I managed the deployment through the Azure CLI and Terraform on Fedora.<br>
1. Azure Authentication<br>

I authenticated via the Service Principal method to allow Terraform to interact with my subscription securely:<br>
    az login<br>
    az ad sp create-for-rbac --name "zoomcamp-sp" --role="Contributor" --scopes="/subscriptions/<my-subscription-id>"<br>

2. Environment Configuration<br>

I exported my credentials as environment variables and also a json to keep them out of the source code:<br>

export ARM_CLIENT_ID="<APPID>"<br>
export ARM_CLIENT_SECRET="<Pwd>"<br>
export ARM_SUBSCRIPTION_ID="<Subscription_id>"<br>
export ARM_TENANT_ID="<TenantID>"<br>

3. Execution Sequence<br>

terraform init       # Initialize Azure providers
terraform fmt        # Format for readability
terraform validate   # Check for syntax errors
terraform plan       # Preview the 4 resources to be created
terraform apply      # Deploy to Azure

4. Results

The deployment was successful: <br>
Plan: 4 to add, 0 to change, 0 to destroy.<br>

## Docker & python![Python](https://img.shields.io/badge/python-3.13-blue.svg)<br>

This section documents my journey of automating the ingestion of NYC taxi data into a local PostgreSQL database using a ingestion script.<br>
The Tech Stack<br>
 Language: Python 3.13 (Managed with uv)<br>
 Libraries: Pandas (Data manipulation),<br>
            SQLAlchemy (Database engine),<br>
            psycopg2-binary (Postgres driver),<br>
            Click (CLI arguments).<br>
 Environment: Dockerized PostgreSQL and pgAdmin.<br>

My steps:<br>
    1.make project folder

    2.uv init --python=3.13

    3. made a network
        docker network create homework-network<br>
    
    4. ran pastgress
            docker run -it \
            -e POSTGRES_USER="root" \
            -e POSTGRES_PASSWORD="root" \
            -e POSTGRES_DB="ny_taxi" \
            -v ny_taxi_postgres_data:/var/lib/postgresql \
            -p 5432:5432 \
            --network=homework-network \
            --name pgdatabase \
            postgres:18

    5. ran pgadmin on another terminal
            docker run -it \
            -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
            -e PGADMIN_DEFAULT_PASSWORD="root" \
            -v pgadmin_data:/var/lib/pgadmin \
            -p 8085:80 \
            --network=homework-network \
            --name pgadmin \
            dpage/pgadmin4

    6. Then wrote the script in jupyter
            uv run jupyter notebook

    7. then typed
        docker run -it \
        --network=homework_default \
        homework_ingest:v001 \
        --pg-user=root \
        --pg-pass=root \
        --pg-host=172.18.0.3 \
        --pg-port=5432 \
        --pg-db=ny_taxi \
        --target-table=green_taxi_trips

    8. Then I red pandas manual to find out how to work on parquet file as only csv was taught

    9. convert into python script
            uv run jupyter nbconvert --to=script notebook.ipynb
            mv notebook.py ingest_data.py

    10. now made dockerfile to containarize the script and build it via:
            docker build -t homework_ingest:v001 .
            
    11. Then i wrote docker-compose.yaml

a note: <br>
    A key problem solved was Service Discovery. Since the ingestion script runs in a separate container, localhost refers to the script container itself. I performed a docker network inspect to identify the database's internal IP (172.18.0.3) and used it to establish a direct connection.<br>
    The Execution Command<br>

## SQL commands for homework questions
Question 3. 

    SELECT COUNT(*) 
    FROM 
        green_taxi_trips 
    WHERE
        trip_distance <= 1 
        AND lpep_pickup_datetime >= '2025-11-01' 
        AND lpep_pickup_datetime < '2025-12-01';

Question 4.

    SELECT 
        CAST(lpep_pickup_datetime AS DATE) AS pickup_day,
        SUM(trip_distance) AS total_daily_distance
    FROM 
        green_taxi_trips 
    WHERE 
        trip_distance <= 100
    GROUP BY 
        pickup_day
    ORDER BY 
        pickup_day DESC
    LIMIT 1;

Question 5.

    SELECT 
        T."Zone",
    FROM 
        green_taxi_trips G
    JOIN taxi_zone_data T
        ON T."LocationID" = G."PULocationID"
    WHERE 
        trip_distance <= 100
    GROUP BY 
        T."Zone"
    ORDER BY 
        sum_total_amount DESC
    LIMIT 1;

Question 6.

    SELECT 
        zdo."Zone" AS dropoff_zone,
        t.tip_amount
    FROM 
        green_taxi_trips t
    JOIN 
        taxi_zone_data zpu ON t."PULocationID" = zpu."LocationID"
    JOIN 
        taxi_zone_data zdo ON t."DOLocationID" = zdo."LocationID"
    WHERE 
        zpu."Zone" = 'East Harlem North'
        AND t.lpep_pickup_datetime >= '2025-11-01'
        AND t.lpep_pickup_datetime < '2025-12-01'
    ORDER BY 
        t.tip_amount DESC
    LIMIT 1;

## How to run

1. I used Docker Compose to run multiple containers on same network

    To start the services:
        docker compose up -d

2. run ingestion script | Dockerfile
 made dockerfile sp it can run in any environment without local python dependency problem.

    docker run -it \
    --network=homework_default \
    homework_ingest:v001 \
        --pg-user=root \
        --pg-pass=root \
        --pg-host=pgdatabase \
        --pg-port=5432 \
        --pg-db=ny_taxi \
        --target-table=green_taxi_trips
3. to work with pgcli
    uv run pgcli -h localhost -p 5432 -u root -d ny_taxi

4. Shutdown & Cleanup
To stop the database and remove the containers, run:
    docker compose down