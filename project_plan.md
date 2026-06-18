# LLM-Based Semantic Service Invocation

## 1. Project Goal

This project investigates how successfully natural language user requests can be transformed into correct semantic API service calls.

Given a natural language query, the system predicts:

* Service domain
* Service intent (operation)
* API endpoint
* Required parameters
* Ontology concept

The project compares multiple service invocation approaches and evaluates their performance.

---

# 2. Research Problem

**How successful is automatic semantic service invocation generation from natural language user requests?**

---

# 3. Project Components

The project consists of:

1. OpenAPI service specifications
2. Natural language dataset
3. Ontology-based semantic model
4. Rule-Based baseline
5. Embedding-Based similarity matching
6. Direct LLM service selection
7. LLM + Ontology validation
8. Accuracy and error analysis

---

# 4. API Domains

The project contains five independent API domains:

* Weather
* Travel
* Product
* Order
* Calendar

---

# 5. Current Project Structure

```
Semantic-Service-Invocation/

├── dataset/
│   └── service_dataset.csv
│
├── figures/
│   └── rule_based/
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
├── paper/
│
├── results/
│   └── rule_based/
│
├── src/
│   └── rule_based/
│       ├── rule_based_mapper.py
│       ├── evaluate_rule_based.py
│       └── generate_rule_based_figures.py
│
└── PROJECT_PLAN.md
```

---

# 6. Completed Work

## 6.1 OpenAPI Specifications

Status: ✅ Completed

Created:

* weather_api.yaml
* travel_api.yaml
* product_api.yaml
* order_api.yaml
* calendar_api.yaml

Each API contains multiple operations with endpoints and parameters.

---

## 6.2 Natural Language Dataset

Status: ✅ Completed

Created:

```
dataset/service_dataset.csv
```

Dataset size:

* 300 queries

Five domains:

* Weather
* Travel
* Product
* Order
* Calendar

Each record contains:

* query
* domain
* intent
* endpoint
* parameters
* ontology_concept

The dataset includes:

* Easy queries
* Medium paraphrased queries
* Hard semantic queries

to enable a fair comparison between methods.

---

## 6.3 Ontology

Status: ✅ Completed

Created:

```
ontology/service_ontology.owl
```

Verified successfully in Protégé.

Ontology contains:

* ServiceDomain classes
* Operation classes
* Endpoint classes
* Parameter classes

Including semantic relationships between them.

---

## 6.4 Rule-Based Intent Mapping

Status: ✅ Completed

Implemented:

```
src/rule_based/rule_based_mapper.py
```

Features:

* Dynamic service catalog loading
* Keyword-based intent prediction
* Endpoint prediction
* Ontology concept prediction
* Basic parameter extraction

---

## 6.5 Rule-Based Evaluation

Status: ✅ Completed

Implemented:

```
src/rule_based/evaluate_rule_based.py
```

Evaluated on the complete dataset.

Metrics computed:

* Domain Accuracy
* Intent Accuracy
* Endpoint Accuracy
* Parameter Accuracy
* Ontology Accuracy
* End-to-End Accuracy

Results are exported to:

```
results/rule_based/rule_based_results.csv
```

---

## 6.6 Rule-Based Figures

Status: ✅ Completed

Implemented:

```
src/rule_based/generate_rule_based_figures.py
```

Generated visualizations stored in:

```
figures/rule_based/
```

Including:

* Metrics Accuracy
* Domain Accuracy
* Success vs Failure

---

# 7. Experimental Methods

The project compares four approaches.

## Method 1

✅ Rule-Based Intent Mapping

Completed.

---

## Method 2

Embedding-Based Similarity Matching

Status:

⬜ Not implemented yet.

---

## Method 3

Direct LLM Service Selection

Status:

⬜ Not implemented yet.

---

## Method 4

LLM + Ontology Validation

Status:

⬜ Not implemented yet.

---

# 8. Evaluation Metrics

The following metrics will be compared across all methods:

* Domain Accuracy
* Intent Accuracy
* Endpoint Accuracy
* Parameter Accuracy
* Ontology Accuracy
* End-to-End Accuracy
* Hallucination Rate

---

# 9. Error Categories

Errors are classified as:

* Wrong domain
* Wrong intent
* Wrong endpoint
* Wrong parameters
* Ontology inconsistency
* Hallucinated service or parameter

---

# 10. Remaining Tasks

The remaining implementation order is:

1. Embedding-Based Similarity Matching
2. Embedding Evaluation
3. Embedding Figures
4. Direct LLM Service Selection
5. LLM Evaluation
6. LLM Figures
7. LLM + Ontology Validation
8. Final Comparative Evaluation
9. Final Figures and Tables
10. Research Paper
11. Presentation
12. Final Demonstration

---

# 11. Current Progress

Estimated overall project completion:

**≈ 45% completed**

Major infrastructure has been successfully implemented, including:

* OpenAPI specifications
* Dataset
* Ontology
* Rule-Based baseline
* Rule-Based evaluation
* Initial result visualizations

The remaining work focuses on semantic matching methods and comparative evaluation.
