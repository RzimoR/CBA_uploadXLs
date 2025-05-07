# CBA Web App

This is a FastAPI web application for performing Cost-Benefit Analysis (CBA) based on input data provided in an Excel file.

## 📂 Project Structure

- `main.py`: FastAPI backend logic to parse Excel files and compute NPV, IRR, CB Ratio.
- `templates/index.html`: Web interface for uploading the Excel file and displaying results.
- `requirements.txt`: Python dependencies.
- `render.yaml`: Configuration file for deploying to [Render](https://render.com/).

## 📥 How to Use

1. Prepare an Excel file (`.xls` or `.xlsx`) with the following columns:

```
Name | CAPEX | OPEX | Benefits | Years | DiscountRate
```

Example:

```
Alternative 1 | 10000 | 1000 | 3000 | 5 | 0.05
```

2. Go to the homepage and upload your Excel file using the form.

3. The app will calculate:
   - Net Present Value (NPV)
   - Internal Rate of Return (IRR)
   - Cost-Benefit Ratio (CB Ratio)

4. Results will be shown in a table on the same page.

## 🚀 Deployment on Render

1. Create a new Web Service on Render.
2. Select `cba_project_render.zip` as the source.
3. Ensure the start command is:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

4. Expose port `10000`.

## 🧮 Calculations

- **NPV**: computed with `numpy_financial.npv(discount_rate, cash_flows)`
- **IRR**: computed with `numpy_financial.irr(cash_flows)`
- **CB Ratio**: discounted benefits divided by CAPEX

