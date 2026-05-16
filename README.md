# 🌊 HydroGeoAI Analyst: Intelligent GIS Assistant

An AI-powered web companion designed specifically for GIS engineers, hydrologists, and spatial analysts. This application leverages advanced Gemini LLM models to generate robust Python automation scripts (ArcPy/GeoPandas), troubleshoot complex terrain manipulation pipelines, and correctly interpret localized geographic constraints.

---

## 🚀 Key Features

*   **Hydro-GIS & Terrain Expert:** Get context-aware guidance on handling raw DEMs, filling sinks, mapping drainage networks, and preparing inputs for HEC-HMS/HEC-RAS models.
*   **ArcPy Automation Framework:** Converts conceptual workflows or ModelBuilder diagrams into production-grade Python scripts using optimal memory cursors (`arcpy.da`).
*   **Coordinate Integrity Guardrail:** Natively prioritizes proper projection spaces, specifically optimizing regional mapping assignments such as Egypt 1907 / Red Belt (EPSG:22991).
*   **Interactive Streaming UI:** Built with Streamlit for near-zero latency text generation, integrated session memory, and isolated chat histories.

---

## 📸 Interface Preview & Demo

### Application Interface
![Application Main Screenshot](https://raw.githubusercontent.com/your-username/your-repo-name/main/assets/screenshot.png)
*Figure 1: The application sidebar allows you to hot-swap between GIS specialties and dynamic system configurations.*

### Interactive Workflow Demo
![Application Working Demo](https://raw.githubusercontent.com/your-username/your-repo-name/main/assets/demo.gif)
*Figure 2: Streaming Python script generation with custom error handling tailored to spatial datasets.*

---

## 🛠️ Step-by-Step Installation

Follow these steps to run the application locally on your machine:

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name