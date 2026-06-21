# Semantic Service Invocation with Large Language Models and Ontology Validation

## Overview

This repository presents a comparative study on **semantic service invocation from natural language**. The project investigates how user requests expressed in natural language can be transformed into correct API service calls and evaluates the impact of **ontology-guided semantic validation** on improving the reliability of Large Language Model (LLM) predictions.

The proposed framework combines **LLMs** with an **OWL-based ontology validation layer** to detect semantic inconsistencies, normalize parameter names, validate required and optional parameters, and safely correct structured service invocations.

---

# Research Question

> **Can ontology-based semantic validation improve the reliability and correctness of LLM-generated API service invocations?**

---

# Main Contributions

* Design of an OpenAPI-based multi-domain semantic service benchmark.
* Construction of a 300-query natural language dataset.
* Development of an OWL ontology describing domains, operations, endpoints, and parameters.
* Implementation and comparison of four semantic service invocation approaches:

  * Rule-Based Intent Mapping
  * Embedding-Based Semantic Matching
  * Direct LLM Service Selection
  * LLM + Ontology Validation and Safe Semantic Correction
* Comprehensive experimental evaluation and error analysis.

---

# Project Structure

```text
Semantic-Service-Invocation/

├── dataset/
│   └── service_dataset.csv
│
├── ontology/
│   └── service_ontology.owl
│
├── openapi/
│   ├── weather_api.yaml
│   ├── travel_api.yaml
│   ├── product_api.yaml
│   ├── order_api.yaml
│   └── calendar_api.yaml
│
├── src/
│   ├── rule_based/
│   ├── embedding/
│   ├── llm/
│   ├── ontology_validation/
│   └── evaluation/
│
├── results/
│
├── figures/
│
└── paper/
```

---

# Service Domains

The benchmark contains five independent service domains:

* Weather
* Travel
* Product
* Order
* Calendar

Each domain is described using OpenAPI specifications and represented in the ontology.

---

# Dataset

The benchmark dataset contains:

* **300 natural language queries**
* **5 service domains**
* **25 operations**
* Ground-truth annotations for:

  * Domain
  * Intent
  * Endpoint
  * Parameters
  * Ontology concept

The dataset includes simple requests, paraphrases, and semantically diverse formulations to provide a realistic evaluation scenario.

---

# Ontology

The project includes an OWL ontology modeling:

* Service Domains
* Operations
* Endpoints
* Parameters

The ontology additionally supports:

* Required parameter validation
* Optional parameter validation
* Semantic parameter normalization through alias mapping

The ontology is loaded at runtime using **Owlready2** and acts as the semantic validation layer of the proposed system.

---

# Compared Approaches

## 1. Rule-Based Intent Mapping

Uses manually defined keyword rules and regular expressions to identify intents and extract parameters.

---

## 2. Embedding-Based Semantic Matching

Uses Sentence-Transformer embeddings (`all-MiniLM-L6-v2`) with cosine similarity retrieval to identify the closest semantic operation.

---

## 3. Direct LLM Service Selection

Uses OpenAI `gpt-4o-mini` to predict:

* Domain
* Intent
* Endpoint
* Parameters
* Ontology concept

directly from natural language queries.

---

## 4. LLM + Ontology Validation (Proposed Method)

The proposed framework augments LLM predictions with ontology-guided validation and safe semantic correction.

The ontology:

* validates domains,
* validates endpoints,
* validates ontology concepts,
* checks required parameters,
* tolerates optional parameters,
* normalizes parameter aliases,
* detects hallucinated parameter names.

Importantly, the ontology **never changes the predicted intent**, ensuring safe and deterministic correction.

---

# Evaluation Metrics

The following metrics are computed:

* Domain Accuracy
* Intent Accuracy
* Endpoint Accuracy
* Parameter Accuracy
* End-to-End Task Success

Ontology-specific diagnostics include:

* Hallucination Rate
* Missing Parameter Rate
* Ontology Inconsistency Rate

---

# Final Experimental Results

| Method             | Domain     | Intent     | Endpoint   | Parameter  | End-to-End |
| ------------------ | ---------- | ---------- | ---------- | ---------- | ---------- |
| Rule-Based         | 50.00%     | 43.00%     | 43.00%     | 12.33%     | 10.33%     |
| Embedding-Based    | 93.67%     | 62.33%     | 62.33%     | 16.67%     | 11.00%     |
| Direct LLM         | 99.00%     | 95.33%     | 95.33%     | 40.67%     | 39.33%     |
| **LLM + Ontology** | **99.33%** | **95.33%** | **95.33%** | **65.67%** | **62.33%** |

The ontology-enhanced approach achieves the highest overall reliability, particularly in parameter correctness and end-to-end task success.

---

# Technologies

* Python 3.11
* OpenAI GPT-4o-mini
* Owlready2
* Sentence Transformers
* OpenAPI 3.0.3
* OWL Ontology
* Matplotlib
* Pandas

---

# Research Paper

The complete research paper describing the methodology, experiments, and results is available in the `paper/` directory.

---

# Reproducibility

All experiments can be reproduced using the provided:

* OpenAPI specifications
* Dataset
* Ontology
* Source code
* Evaluation scripts
* Result files
* Generated figures

---

# Author

**ANAS ALSHOURAFA**

Department of Computer Engineering

Çanakkale Onsekiz Mart University

Çanakkale, Türkiye
