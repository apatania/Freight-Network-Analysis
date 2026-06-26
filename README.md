# Freight-Network-Analysis
Python project that optimizes freight cost or CO2 emissions between various freight hubs in the United States. Includes a web app that provides a user friendly interface for use of the program.

###  FAF5 Freight Route Optimization Dashboard

An interactive Streamlit-based web application that utilizes the **Freight Analysis Framework (FAF5)** data to calculate optimal shipping lanes. This tool helps logistics planners route inter-regional freight between key United States hubs while optimizing for either **financial expenses** or **environmental impact**.

* * *

###  Key Features

*   **FAF5 Data Processing:** Efficiently filters, groups, and maps high-volume federal freight datasets.
*   **Multi-Modal Routing:** Evaluates transport legs across **Truck**, **Rail**, and **Air** modes.
*   **Network Optimization:** Utilizes **Dijkstra’s Algorithm** via the `networkx` library to find the absolute shortest path.
*   **Capacity Bottleneck Alerts:** Checks lane constraints and skips routes that exceed maximum available capacity.
*   **Dual-Objective Solvers:** Instantly switch between minimizing **Total Cost ($)** or **Carbon Footprint (CO2)**.
*   **Interactive UI:** Streamlit sidebar selectors for easy origin, destination, and strategy dispatching.

* * *

### ⚙️ Prerequisites & Installation

Ensure you have Python 3.8+ installed, then install the required dependencies:

bash

    pip install pandas networkx streamlit
    

Use code with caution.

* * *

### 📁 Dataset Setup

This application relies on the Federal Highway Administration's **FAF5.7.1 CSV dataset**.

1.  Download the raw CSV data from the official [Federal Highway Administration (FHWA)](https://ops.fhwa.dot.gov/freight/freight_analysis/faf/) website.
2.  Open the application script file.
3.  Locate the `file_path` variable at the top of the script and update it to your local file path:
    
    python
    
        # Update this path to where your file is located
        file_path = "/Users/YOUR_USERNAME/Downloads/FAF5.7.1/FAF5.7.1.csv"
        
    
    Use code with caution.
    

* * *

###  How to Run

Navigate to the directory containing your script (e.g., `app.py`) in your terminal and run:

bash

    streamlit run app.py
    

Use code with caution.

The app will automatically spin up a local development server and open the dashboard in your default web browser (usually at `http://localhost:8501`).

* * *

###  Dashboard Walkthrough

1.  **Route Dispatch Parameters (Sidebar):** Select your shipping origin hub, destination hub, and primary network objective.
2.  **Recommended Dispatch Routing Strategy:** View the optimal node sequence arrow map (e.g., `Birmingham, AL ➡️ Mobile, AL`).
3.  **Manifest Details for Selected Path Links:** Inspect a complete breakdown table of every leg in the journey including mode, distance, cost, and emissions.
4.  **Summary Metrics:** View total aggregate manifest cost and carbon footprint calculations instantly.
