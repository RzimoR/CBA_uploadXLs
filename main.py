from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
import numpy_financial as npf
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/calculate", response_class=HTMLResponse)
async def calculate_cba(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Errore nella lettura del file: {str(e)}"})

    required_columns = {"Name", "CAPEX", "OPEX", "Benefits", "Years", "DiscountRate"}
    if not required_columns.issubset(df.columns):
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Colonne mancanti. Richieste: {', '.join(required_columns)}"})

    results = []
    for _, row in df.iterrows():
        try:
            name = row['Name']
            capex = float(row['CAPEX'])
            opex = float(row['OPEX'])
            benefit = float(row['Benefits'])
            years = int(row['Years'])
            discount_rate = float(row['DiscountRate'])

            cash_flows = [-capex] + [benefit - opex] * years

            npv = npf.npv(discount_rate, cash_flows)
            irr = npf.irr(cash_flows)
            cb_ratio = sum([(benefit - opex) / ((1 + discount_rate) ** (i + 1)) for i in range(years)]) / capex

            results.append({
                "Name": name,
                "NPV": round(npv, 2),
                "IRR": round(irr, 4) if irr is not None else "N/A",
                "CBR": round(cb_ratio, 2)
            })
        except Exception as e:
            results.append({"Name": row.get("Name", "Unknown"), "Error": str(e)})

    return templates.TemplateResponse("index.html", {"request": request, "results": results})
