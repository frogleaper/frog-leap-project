# Bar Soap Production Forecast using Frog Leap Algorithm (FLA)

This project uses the **Frog Leap Algorithm (FLA)**, a metaheuristic optimization method, to forecast production for the next 5 months in a Bar Soap company.

---

## 🔍 Problem Statement

You are given past monthly production data from a Bar Soap manufacturing company. Your task is to **predict/forecast** the production quantity for the next 5 months using the **Frog Leap Algorithm**.

---

## 🧠 Methodology

### What is the Frog Leap Algorithm?
The **Frog Leap Algorithm (FLA)** mimics the behavior of frogs searching for food. It works by:
- Dividing frogs (solutions) into **memplexes**
- Evolving each memplex by **local search** (leaps)
- Sharing information globally by **shuffling frogs**

### Steps Followed
5. Export the forecasted results to an Excel file
1. Simulate historical monthly production data
2. Fit a **polynomial model** to production using optimized parameters
3. Use FLA to minimize the **mean squared error** of the model
4. Forecast the next 5 months using the best-fit model

---

## 📊 Data

Simulated production data for 10 months:

```
[1020, 1100, 1080, 1150, 1200, 1180, 1250, 1300, 1290, 1350]
```

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

```bash
python app.py
```

This will:
- Run the FLA to find the best polynomial model
- Predict production for the next 5 months
- Show a plot of historical vs forecasted data

---

## 📈 Output

- `forecast_output.xlsx` – Excel file with 5-month forecast

- Optimized model parameters
- Forecasted production values
- Visualization plot

---

## 📁 Files

- `main.py` – Core Python script
- `requirements.txt` – Dependencies
- `README.md` – Documentation

---

## 👨‍💻 Author

CHIBUIKE ORAEKWUOTU  
Python | Optimization | Forecasting

---





# Frog Leap Production Forecast - Web App

A Flask web app to forecast the next 5 months of production for a bar soap company using the Frog Leap Algorithm.

## 🔧 Features
- Forecasts 5 future production values
- Download results as Excel
- Simple web UI
- Deployable on Render

## 🖥 How to Run Locally
```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:port` to use the app.

## 🌍 Deployment (Render.com)
- Use the included `render.yaml`
- Connect this folder to a Render web service
