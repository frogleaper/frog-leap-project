from flask import Flask, render_template, request, send_file
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image, Spacer
from reportlab.lib import colors

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

    # Generate the plot as an image in memory
    plt.figure(figsize=(8, 4))
    months_all = [f"Month {i+1}" for i in range(len(last_input_data))] + [f"Forecast {i+1}" for i in range(len(last_forecast))]
    values_all = last_input_data + last_forecast

    plt.plot(months_all, values_all, marker='o', color='#2980b9')
    plt.title('Bar Soap Production Forecast')
    plt.xlabel('Months')
    plt.ylabel('Production Quantity')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)

    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "Bar Soap Production Forecast")

    # Insert the image (chart)
    img = Image(img_buffer)
    img_width = 480
    img_height = 240
    img.drawHeight = img_height
    img.drawWidth = img_width
    img.wrapOn(c, width, height)
    img.drawOn(c, 60, height - 320)

    # Table data
    table_data = [["Month", "Production Quantity"]]
    for m, v in zip(months_all, values_all):
        table_data.append([m, v])

    table = Table(table_data, colWidths=[200, 150])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # Position the table below the image
    table.wrapOn(c, width, height)
    table_height = 20 * len(table_data)  # Approximate row height * number of rows
    table.drawOn(c, 80, height - 350 - table_height)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True,
                     download_name="production_forecast.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
