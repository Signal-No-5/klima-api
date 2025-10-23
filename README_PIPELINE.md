# 🌦️ KLIMA Data Pipeline

**Author:** Philip Ma, Data Engineer of Team Signal #5

**Last updated:** October 23, 2025

---

## 🧭 Overview

KLIMA is a disaster intelligence platform designed to **predict, assess, and communicate risk** across the Philippines.

This document provides an overview of the **data pipeline** located in `klima-api/pipeline/`. In the future, this pipeline may evolve into a standalone backend service and separate repository.

It describes the pipeline’s **architecture**, **design rationale**, and **data flow**, highlighting how modular engineering principles support KLIMA’s broader goal of disaster resilience through data.

---

## ⚙️ Architecture

The KLIMA pipeline follows a **modular, asset-oriented philosophy** inspired by **Databricks**, **Dagster**, **Airflow**, and **dbt**.

It implements the **Medallion Architecture**, which organizes data transformations into three distinct stages:

* **🟫 Bronze Stage – Raw ingestion**
  - Collects unmodified data from APIs and other external sources.
  - Serves as a single source of truth for raw observations.

* **⬜ Silver Stage – Cleaned and standardized assets**
  - Transforms and normalizes bronze data into structured tables.
  - Ensures data consistency through standardized schemas and validation.

* **🟨 Gold Stage – Aggregated and analytical outputs**
  - Merges silver assets into higher-level insights such as risk levels, alert triggers, and reports for LGUs and citizens.

### 🧩 Asset-Oriented Design

Every data entity is treated as an **asset**, similar to Dagster’s paradigm.
A **custom `@asset` decorator** is implemented to handle the common functions shared by all assets, such as the following:

* **Table creation** – Materializes a new table in the appropriate Medallion stage
* **Deduplication** – Ensures uniqueness if a key is provided
* **Retries with backoff** – Prevents transient network or API errors from halting runs
* **Lineage metadata** – Records which upstream assets contributed to a dataset
* **Logging** – Captures execution traces, errors, and timestamps for every run

This design keeps the pipeline **extensible**, allowing new assets to be added with minimal coupling between modules.

In this project, **each asset corresponds to a Python script** that materializes a specific dataset (i.e., creates a table). Assets are named after the tables they produce.

### 🗂️ Project Structure

An outline of the pipeline’s organization:

```
pipeline/
│
├── asset.py                        # Custom asset decorator
│
├── config/                         # Configuration files
│   ├── api/                        # API endpoints (e.g., PAGASA ActiveWarning)
│   │   ├── pagasa.py
│   │   ├── ...	   
│   │   └── __init__.py                
│   ├── db.py                       # Database connection settings and file paths
│   └── __init__.py
│
├── logs/                           # Temporary logs and pipeline execution traces
│
├── orchestration/                  # Scheduling, execution, and dependency management
│   ├── jobs/ (to-do)               # Individual pipeline runs or scheduled workflows
│   │   ├── hazard_tables.py
│   │   ├── ...
│   │   └── __init__.py
│   ├── scheduler.py (to-do)
│   └── __init__.py
│
├── refinery/                       # Core data refinement stages
│   ├── bronze/                     # Raw data ingestion
│   │   ├── pagasa_warnings.py      # Materializes the pagasa_warnings table
│   │   ├── noah_flood_100yr.py (to-do)
│   │   ├── ...
│   │   └── __init__.py
│   ├── silver/                     # Data cleaning and validation
│   │   ├── tropical_cyclones.py
│   │   ├── flood_advisories.py
│   │   ├── ...
│   │   └── __init__.py
│   ├── gold/                       # Data aggregation and enrichment
│   │   ├── user_risks.py (to-do)
│   │   ├── ...
│   │   └── __init__.py
│   └── __init__.py
│
├── utils/                          # Helper modules
│   ├── timestamp.py                # Timezone-aware timestamps
│   ├── extract_http.py             # Unified HTTP extractor with retry + validation logic
│   └── __init__.py 
│
└── __init__.py

```

This modular structure allows assets to be orchestrated manually or through an industry-grade orchestrator like Dagster in future versions.

---

## 🌧️ Data Sources

### 🧮 Risk Calculation Model

KLIMA’s data sources are organized around its core **risk model**, defined as:

$R = f(H, E, V)$

Where:

* **R (Risk)** — likelihood and severity of safety compromise
* **H (Hazard)** — real-time or forecasted environmental threats
* **E (Exposure)** — user behavior and proximity to hazards
* **V (Vulnerability)** — long-term socioeconomic and geographic sensitivity

Each component is **normalized between 0 and 1** and combined through **weighted averages**, enabling dynamic recalculation as new data arrives.

In future iterations, the model may be further **optimized using machine learning**, and refined in collaboration with **subject-matter experts** to improve accuracy and interpretability. It will also be **validated against historical data** to ensure its reliability in real-world scenarios.

---

### 🌊 Hazard Layer (scheduled ingestion)

Represents **real-time and forecasted hazards**.
KLIMA automatically extracts and standardizes data from government APIs and public data sources.

**Current Source:**

* PAGASA Active Warnings API

**Potential Additions:**

* DIWATA satellite imagery
* NDRRMC situation reports
* PAGASA Cyclone Track API
* PAGASA Lightning Warnings API

**Purpose:** Identify when and where hazards are likely to occur, forming the first layer of the risk model.

---

### 🚶 Exposure Layer (user-generated)

Captures **crowdsourced impact and movement** of citizens during hazard events.

**Upcoming Sources:**

* Anonymous location pings (privacy-safe, optional)
* User reports (“REPORT”, “HELP”, or “SAFE”) through KLIMA or Messenger
* Behavioral patterns (e.g., evacuation trends)

**Purpose:** Quantify real-time exposure to hazards and strengthen the feedback loop between users and local governments.

---

### 🏘️ Vulnerability Layer (pre-loaded spatial data)

Encodes long-term geographic and socioeconomic vulnerability.

**Current Source:**

* UP NOAH – 100-year Flood Hazard Maps

**Potential Additions:**

* Project CCHAIN and Open Hazards PH datasets
* PSA socioeconomic indicators (population, income, infrastructure)
* OpenStreetMap and Geofabric elevation/topography

**Purpose:** Provide contextual understanding of which communities are inherently more vulnerable even before hazards occur.

---

## 🧬 Lineage Graph

(to-do)

---

## 📈 Future Directions

* Integration with the KLIMA mobile app, replacing the current dummy data with live pipeline outputs
* Finalization of version 1.0 of the Risk formula, establishing a consistent basis for user risk scoring
* Migration of production storage to a PostgreSQL + DuckDB hybrid, improving scalability and query efficiency
* Expansion of data coverage through the addition of new and diverse data sources
* Implementation of an event-driven alerting system using asynchronous webhooks and user risk segmentation
* Scheduled orchestration powered by Dagster for automated, reliable data updates

---

## 🧑‍💻 Closing Note

This pipeline demonstrates how **data engineering principles** can be applied to **disaster resilience**.
Even in its prototype stage, KLIMA’s modular, medallion-based design provides a strong foundation for scalable risk intelligence in the Philippines.

> “Data saves lives — but only if we can move it fast enough.”