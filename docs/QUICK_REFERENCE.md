# Quick Reference Guide: NYC Taxi Pulse Dashboard

## 🚀 30-Second Start

```bash
# 1. Clone
git clone https://github.com/yourusername/nyc-mobility-dashboard.git
cd nyc-mobility-dashboard

# 2. Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run
python app.py

# 4. Open
# http://localhost:8050
```

---

## 📊 Dashboard at a Glance

| Component | What It Does | How to Use |
|-----------|-------------|-----------|
| **Date Range Picker** | Select analysis period (Jan-Mar 2023) | Click start/end dates |
| **Hour Slider** | Filter by time-of-day (0-23) | Drag slider left/right |
| **Payment Dropdown** | Choose payment method | Select from list |
| **Weather Filter** | Rainy vs Clear days | Choose option |
| **Day Type Filter** | Weekday vs Weekend | Select from list |
| **KPI Cards** | Key metrics update | Shows filtered stats |
| **Time Series** | Daily trips over time | Drag to select period (triggers all charts) |
| **Heatmap** | Hour × Day patterns | Hover for values, linked to time series |
| **Scatter Plot** | Distance vs Fare | Color = payment type, linked to filters |
| **Borough Chart** | Fare distribution | Boxplot shows variation by area |

---

## 🔗 Linking & Brushing Guide

### What's Linked?
✅ **Time Series → Everything**  
- Drag on time series = filter all other charts to that date range

✅ **Filters → Everything**  
- Change any filter = all charts update instantly

✅ **Payment Type → Color Encoding**  
- Scatter plot color shows payment type
- Heatmap optional color encoding

### How to Trigger Linking

| Action | Effect |
|--------|--------|
| Drag on time series chart | All charts filter to selected dates |
| Change date range picker | Time series + all charts update |
| Change hour slider | All temporal patterns update |
| Change payment filter | Charts color/data changes |
| Change weather filter | Impact analysis updates |
| Change day-type filter | Weekday vs weekend patterns shown |

---

## 📈 Reading the Charts

### Time Series (Top Left)
- **X-axis**: Date (left to right = earlier to later)
- **Y-axis**: Number of trips
- **Orange line**: 7-day moving average (trend)
- **Blue line**: Daily values (noise + trend)
- **Interaction**: Drag to select time window

**Read**: "Trip count generally stable around 900-1100 daily, with peaks on Fridays"

### Heatmap (Bottom Left)
- **Rows**: Days of week (Mon-Sun)
- **Columns**: Hours (0-23 = midnight to 11 PM)
- **Color intensity**: Dark = more trips
- **Pattern**: Notice bright spots for peak times

**Read**: "Friday evenings (6 PM column) show darkest colors = busiest time"

### Distance vs Fare Scatter (Right)
- **X-axis**: Trip distance in miles
- **Y-axis**: Fare amount in dollars
- **Color**: Payment type (blue = credit, orange = cash)
- **Size**: Passenger count
- **Pattern**: Diagonal trend (more distance = more fare)

**Read**: "Generally linear relationship, but some outliers: short-distance high-fare trips (surge pricing)"

### Borough Boxplots (Bottom Center)
- **X-axis**: Boroughs (Manhattan, Brooklyn, etc.)
- **Box**: Median ± middle 50%
- **Whiskers**: Range
- **Dots**: Outliers

**Read**: "Manhattan median fare = $16, outer boroughs = $12; Manhattan has more outliers (high fares)"

---

## 🎯 Common Questions & Answers

### Q: "Why are my selected dates not appearing?"
**A**: The range slider might have reset. Try clicking directly on dates in the date picker.

### Q: "Why do the numbers jump when I change filters?"
**A**: Because we're now showing a different subset of data. This is correct!
- Filter to "Credit Card only" → trip count drops (card ≠ all payments)

### Q: "Which borough has the highest demand?"
**A**: Manhattan (65% of all pickups). Check the heatmap - Manhattan dominates.

### Q: "How do I see weather impact?"
**A**: 
1. Note current average fare (all data)
2. Change weather filter to "Rainy"
3. Compare new average fare
4. Usually +$1-2 on rainy days

### Q: "Can I export the data?"
**A**: Currently, no export button. But you can:
1. Screenshot the charts
2. Use browser dev tools to inspect data
3. Or access raw data on our GitHub repo

### Q: "Why is the first load slow?"
**A**: 
- First time: Downloads data from NYC TLC (12-15 seconds)
- Second time: Uses cache (1-2 seconds)
- Filters: Always <400ms

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Dashboard won't load** | Check internet, refresh page, clear cache |
| **Charts blank** | Wait 20 seconds (first load), or reload |
| **Filters not working** | Refresh page, ensure you're on latest version |
| **Slow performance** | Clear browser cache, reduce filters |
| **Data looks wrong** | Double-check filters at top (might be filtering to 0 records) |

---

## 📚 File Guide

```
📦 Project Root
├── 📄 app.py                    ← START HERE: Run this to launch dashboard
├── 📄 requirements.txt          ← Install: pip install -r requirements.txt
├── 📄 README.md                 ← Full documentation
│
├── 📁 src/
│   ├── data_loader.py           ← Data loading & preprocessing functions
│   ├── visualizations.py        ← Chart creation code
│
├── 📁 notebooks/
│   └── EDA_NYC_Taxi.ipynb       ← Exploratory analysis (view in Jupyter)
│
├── 📁 data/
│   └── processed/               ← Cached Parquet files (auto-generated)
│
├── 📁 docs/
│   ├── DEPLOYMENT.md            ← How to deploy (GitHub/Streamlit/Heroku)
│   ├── DATA_PROCESSING.md       ← Data pipeline details
│   └── PRESENTATION_OUTLINE.md  ← Slides & speaker notes
│
└── index.html                   ← GitHub Pages portfolio site
```

---

## 🌐 Important Links

| Link | Purpose |
|------|---------|
| **Live Dashboard** | https://nyc-taxi-pulse-dashboard.streamlit.app |
| **GitHub Repository** | https://github.com/yourusername/nyc-mobility-dashboard |
| **Portfolio Site** | https://yourusername.github.io/nyc-mobility-dashboard |
| **Dataset Source** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page |
| **Plotly Dash Docs** | https://dash.plotly.com/ |
| **GeoPandas Guide** | https://geopandas.org/ |

---

## 💡 Tips & Tricks

### 1. **Comparing Two Scenarios**
- Note KPI metrics for Scenario A
- Change filters to Scenario B
- Compare metrics side-by-side

Example: Credit card vs cash tipping
- Filter to "Credit Card" → avg tip ~18%
- Change to "Cash" → avg tip ~0%

### 2. **Identifying Outliers**
- Look at scatter plot points far from main trend
- These represent unusual trips (high surge, short-distance expensive, etc.)

### 3. **Peak Hour Analysis**
- Set hour range to just 1 hour (e.g., 18:00-18:00)
- Observe which day of week is busiest for that hour
- Heatmap will highlight the pattern

### 4. **Weather Impact Deep Dive**
- Compare "Rainy" vs "Clear" with fixed hour range
- Example: 6-8 PM rainy vs clear to see evening rush pattern

---

## 📱 Mobile Viewing

The dashboard is responsive and works on:
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)
- ✅ Tablets (iPad, Android tablets)
- ⚠️ Mobile phones (layout optimized but limited screen space)

**Tip**: Landscape mode recommended for mobile

---

## ⚡ Performance Expectations

| Action | Expected Time |
|--------|---|
| Initial page load (first time) | 15-20 seconds |
| Page load (cached) | 1-2 seconds |
| Change filter | <400 ms |
| Drag on time series | <300 ms |
| Chart rendering | 50-200 ms |

**Note**: Times vary based on:
- Internet speed
- Browser performance
- Device specs
- Time of day (server load)

---

## 🎓 Learning Resources

### For Understanding the Dashboard
1. Read README.md first
2. Explore live dashboard
3. Try each filter individually
4. Review EDA notebook for data insights

### For Understanding the Code
1. Look at `app.py` - start with callback definitions
2. Read `data_loader.py` - data pipeline
3. Study `visualizations.py` - chart functions
4. Run locally: `python app.py`

### For Extending the Dashboard
1. Add new data source: Edit `data_loader.py`
2. Add new chart: Edit `visualizations.py` + `app.py`
3. Add new filter: Edit `app.py` layout + callback
4. Modify colors: Edit CSS in `app.py` or `style.css`

---

## 🎥 Recording a Demo Video

### Quick Setup (OBS Studio - Free)
1. Download OBS Studio
2. Create new scene
3. Add display capture source
4. Start recording
5. Open dashboard, demonstrate features
6. Stop recording, save file
7. Upload to YouTube

### What to Show (5-7 minutes)
1. Dashboard intro (30 sec)
2. Default state & KPI metrics (30 sec)
3. Time series brushing demo (1 min)
4. Filter changes (1 min)
5. Weather impact demo (1 min)
6. Final insights (1 min)

---

## 🚀 Deployment Reminders

- [ ] Code pushed to GitHub
- [ ] requirements.txt updated
- [ ] Procfile created (for Heroku)
- [ ] App tested locally
- [ ] Live URL verified
- [ ] README links correct
- [ ] Video link added to GitHub Pages
- [ ] GitHub Pages enabled in repo settings

---

## 🆘 Need Help?

### Check These First
1. **Crashes?** → See logs in browser console (F12 → Console tab)
2. **Slow?** → Check internet, clear browser cache
3. **Filters broken?** → Refresh page
4. **Can't access?** → Check live URL

### Contact Resources
- **Dashboard code**: Issue on GitHub repo
- **Deployment**: Check docs/DEPLOYMENT.md
- **Data questions**: Review docs/DATA_PROCESSING.md
- **Presentation prep**: See docs/PRESENTATION_OUTLINE.md

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Status**: ✅ Production Ready
