# TripShield AI — Demo Guide

## Overview

This guide walks through the key demo scenarios for TripShield AI. The demo is designed to be completed in **under 2 minutes** and showcases the core innovation: recovering an entire journey, not just individual bookings.

---

## Pre-Demo Setup

1. Start the backend: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Open `http://localhost:3000` in your browser

---

## Demo Script

### Step 1: Register & Login (15 seconds)

1. Click "Register"
2. Enter: Name, Email, Password
3. Click "Create Account"
4. You're redirected to the Dashboard

### Step 2: Load Demo Journey (10 seconds)

1. On the Dashboard, click **"Load Demo Journey"**
2. A complete Chennai → Delhi → Paris trip is created with:
   - 10 travel components (flights, hotels, transfers, activities, dining)
   - 9 dependency relationships
   - Full booking details and costs

### Step 3: Explore the Journey Digital Twin (20 seconds)

1. Click on the journey card to open it
2. View the **Timeline** — all components in chronological order
3. Click **"View Digital Twin"** — see the interactive dependency graph
4. All nodes are **green** (confirmed) with connection lines showing dependencies
5. Note the **Resilience Score** — the journey's vulnerability rating

### Step 4: Trigger a Disruption (10 seconds)

1. Go back to Dashboard
2. Click **"Simulate 4-Hour Flight Delay"**
3. Watch what happens:

### Step 5: Watch the Ripple Effect (20 seconds)

The system automatically:
1. ⚠️ Detects the disruption on the first flight
2. 🔄 Runs the **Ripple Impact Engine**
3. 🔴 Marks downstream nodes as **affected** (transfer, hotel check-in, activity)
4. 📊 Calculates the **Impact Score** (severity 0-100)
5. 🔔 Creates a disruption notification

**Key Talking Point:** _"Notice how a single flight delay cascades through 4 downstream bookings. This is why you need to recover the journey, not just the flight."_

### Step 6: Review Recovery Options (20 seconds)

1. Go to **Recovery Center** (or click the disruption alert)
2. See **3-5 recovery strategies**, each showing:
   - Cost impact
   - Time saved/lost
   - Number of changes
   - Preserved bookings
   - Overall score
   - AI explanation
3. The top option has a **"Recommended by TripShield"** badge

**Key Talking Point:** _"Each strategy is scored based on this traveler's personal preferences — someone who prioritizes budget would see a different recommendation than someone who prioritizes speed."_

### Step 7: Read the AI Explanation (10 seconds)

Each recovery option has an explanation like:

> "Option A was selected because it preserves your hotel and activity bookings, arrives 2 hours earlier, requires only one itinerary change, and costs ₹800 less than Option B."

**Key Talking Point:** _"The explanation is generated from actual calculated values — not generic text. The AI uses real impact data and preference weights."_

### Step 8: Approve & Execute Recovery (10 seconds)

1. Click **"Approve Recovery"** on the recommended option
2. The system:
   - Updates affected bookings
   - Rebuilds the itinerary
   - Marks nodes as **recovered** (blue)
   - Creates audit log entry
3. Visit the Digital Twin — nodes are now blue (recovered) instead of red

### Step 9: Show the Audit Trail (10 seconds)

1. Go to **Admin** → **Audit Logs**
2. Show the complete decision trail:
   - Disruption detected at [time]
   - Impact analysis: 4 nodes affected, score 72/100
   - Recovery strategy generated
   - User approved strategy A
   - Recovery executed successfully

---

## Bonus Demos

### What-If Simulator

1. Go to **What-If Simulator**
2. Select the journey
3. Choose "Flight Cancellation"
4. Click **"Run Simulation"**
5. See the hypothetical impact WITHOUT changing real data
6. Compare resilience scores before/after

### TripShield Guardian

1. Go to **TripShield Guardian**
2. Ask: "What happens if my flight is delayed by 3 hours?"
3. The AI responds using actual journey data
4. Ask: "What is my cheapest recovery option?"
5. The AI references real recovery strategies

### Preference Impact

1. Go to **Settings** → **Preferences**
2. Change Budget priority to 90, Speed to 40
3. Re-run recovery generation
4. The recommended strategy changes to prioritize cost savings

---

## Key Messages for Judges

1. **Not a booking platform** — It's a resilience platform that understands journey dependencies
2. **Journey Digital Twin** — Your trip is a live graph, not a flat list
3. **Ripple Impact Engine** — Single disruption → cascading analysis → calculated severity
4. **Personalized Recovery** — Strategies scored by YOUR preferences, not one-size-fits-all
5. **Explainable AI** — Every recommendation backed by real calculated values
6. **What-If Simulation** — Test disruptions safely before they happen
7. **Full Audit Trail** — Every AI decision logged and explainable
8. **Production Architecture** — Modular, testable, deployable, extensible

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend won't start | Check Python 3.11+ installed, `pip install -r requirements.txt` |
| Frontend won't start | Check Node.js 18+ installed, `npm install` |
| "Load Demo Journey" fails | Make sure backend is running at `http://localhost:8000` |
| CORS errors | Check CORS_ORIGINS in `.env` includes frontend URL |
| Empty dashboard | Register a new user first, then load demo journey |

---

## Demo Data Labels

All data in the demo is clearly marked as simulated:
- Flight numbers, prices, and availability are realistic but mocked
- Weather and risk assessments are simulated
- No real bookings are created
- No real money is charged

**This is clearly communicated in the UI with "Demo / Simulated Data" labels.**
