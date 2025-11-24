Kenya Healthcare System — Interactive Analytics Dashboard

A fully interactive Dash + Plotly dashboard analyzing healthcare accessibility, facility distribution, workforce capacity, and service coverage across 309 Kenyan sub-counties.

🔗 Live Dashboard: Add Render URL here after deployment
📌 Tech Stack: Python, Dash, Plotly, Pandas, Gunicorn
📊 Dataset: Kenya Master Health Facility List + Population Data

🚀 Features
✔ Interactive Filters

Filter by County

Select key metrics (Beds per 10k, Facilities per 10k, Operational %, etc.)

Choose Top N subcounties

✔ Dynamic Visualizations

Bar charts

Scatter-plots

Heatmaps

Radar charts

KPI cards

Dynamic data table with filtering & sorting

✔ Clean Power BI–style UI

Smooth card shadows

Soft borders

Responsive layout

CSS theming

📂 Project Structure
KenyaHealthDashboard/
│-- app.py
│-- requirements.txt
│-- Procfile
│-- README.md
│
├── assets/
│     └── pbi-light.css
│
└── data/
       └── subcounty_metrics.csv

▶️ Running Locally
pip install -r requirements.txt
python app.py


Dashboard loads at:

http://127.0.0.1:8050/

🌐 Deploy to Render (Free Hosting)

Push this entire folder to GitHub

Go to https://render.com

Click New → Web Service

Connect your GitHub repo

Use these settings:

Setting	Value
Runtime	Python
Build Command	pip install -r requirements.txt
Start Command	gunicorn app:app
Region	Any
Instance	Free Tier

Click Deploy 🚀

Copy the live URL & update your README + LinkedIn post

🧑‍💼 Author

Ayush Gajanan Magdum
Data Analyst | Python | Power BI | Analytics | Dashboards
(Add your LinkedIn link here)

💡 License

MIT License — free to use & modify.
