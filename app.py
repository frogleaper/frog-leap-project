from flask import Flask, render_template, request, send_file
import numpy as np
import pandas as pd
import io
import os
import random

app = Flask(__name__)

# Global storage for export
last_forecast = []
last_input_data = []

degree = 2

def fitness(params):
    predictions = sum([params[i] * X**i for i in range(len(params))])
    return np.mean((y - predictions)**2)

def frog_leap_algorithm(fitness_func, dim, pop_size, memplex_count, max_iter, bounds):
    population = [np.random.uniform(bounds[0], bounds[1], dim) for _ in range(pop_size)]
    population.sort(key=fitness_func)
    memplexes = [[] for _ in range(memplex_count)]

    for i in range(pop_size):
        memplexes[i % memplex_count].append(population[i])

    for iteration in range(max_iter):
        for memplex in memplexes:
            memplex.sort(key=fitness_func)
            best = memplex[0]
            worst = memplex[-1]

            new_frog = worst + random.uniform(0, 1) * (best - worst)
            new_frog = np.clip(new_frog, bounds[0], bounds[1])
            if fitness_func(new_frog) < fitness_func(worst):
                memplex[-1] = new_frog
            else:
                new_frog = np.random.uniform(bounds[0], bounds[1], dim)
                memplex[-1] = new_frog

        population = [frog for memplex in memplexes for frog in memplex]
        population.sort(key=fitness_func)
        for i in range(pop_size):
            memplexes[i % memplex_count][i // memplex_count] = population[i]

    return population[0]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forecast", methods=["POST"])
def forecast():
    global last_forecast, last_input_data, X, y
    data = request.get_json()
    raw_input = data.get('input', '')
    try:
        input_data = [int(x.strip()) for x in raw_input.split(',') if x.strip().isdigit()]
        if len(input_data) != 10:
            return {"error": "Please enter exactly 10 numeric values."}, 400
    except:
        return {"error": "Invalid input format."}, 400

    y = np.array(input_data)
    X = np.arange(1, len(y) + 1)
    last_input_data = input_data

    dim = degree + 1
    pop_size = 30
    memplex_count = 5
    max_iter = 100
    bounds = (-100, 100)

    best_params = frog_leap_algorithm(fitness, dim, pop_size, memplex_count, max_iter, bounds)

    future_months = np.arange(len(y) + 1, len(y) + 6)
    forecast_values = sum([best_params[i] * future_months**i for i in range(len(best_params))])
    forecast_values = forecast_values.astype(int)

    last_forecast = forecast_values.tolist()

    return {"original": input_data, "forecast": last_forecast}

@app.route("/export")
def export():
    if not last_forecast or not last_input_data:
        return "No forecast data to export.", 400

    months_input = [f"Month {i+1}" for i in range(len(last_input_data))]
    months_forecast = [f"Forecast {i+1}" for i in range(len(last_forecast))]
    months_all = months_input + months_forecast
    values_all = last_input_data + last_forecast

    df = pd.DataFrame({
        "Month": months_all,
        "Production": values_all
    })

    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    return send_file(output, as_attachment=True,
                     download_name="forecast_output.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
