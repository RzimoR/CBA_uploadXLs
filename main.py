from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np
import numpy_financial as npf
import io

app = FastAPI()

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

    max_npv = max([r["NPV"] for r in results if "NPV" in r and isinstance(r["NPV"], (int, float))], default=None)

    return templates.TemplateResponse("index.html", {"request": request, "results": results, "max_npv": max_npv})

@app.post("/download", response_class=StreamingResponse)
async def download_excel(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    output = []
    for _, row in df.iterrows():
        try:
            capex = float(row['CAPEX'])
            opex = float(row['OPEX'])
            benefit = float(row['Benefits'])
            years = int(row['Years'])
            discount_rate = float(row['DiscountRate'])
            cash_flows = [-capex] + [benefit - opex] * years
            npv = npf.npv(discount_rate, cash_flows)
            irr = npf.irr(cash_flows)
            cb_ratio = sum([(benefit - opex) / ((1 + discount_rate) ** (i + 1)) for i in range(years)]) / capex
            row['NPV'] = round(npv, 2)
            row['IRR'] = round(irr, 4) if irr is not None else "N/A"
            row['CB Ratio'] = round(cb_ratio, 2)
        except:
            row['NPV'] = "Error"
            row['IRR'] = "Error"
            row['CB Ratio'] = "Error"
        output.append(row)
    result_df = pd.DataFrame(output)
    stream = io.BytesIO()
    result_df.to_excel(stream, index=False)
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=results.xlsx"})
