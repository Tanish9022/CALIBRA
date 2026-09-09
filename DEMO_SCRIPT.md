# CALIBRA - Mock Demo Script

This document provides a narrative script to accompany a live demo of the CALIBRA MVP prototype.

## Setup
Before starting the demo:
1. Run `docker-compose up -d --build` (or start `uvicorn` and `npm run dev` manually).
2. Open `http://localhost:5175` in your browser.
3. Keep the browser Developer Tools (F12) closed for a clean presentation, unless you want to show the JSON trace.

## The Pitch
> "Hello! Today we are showing CALIBRA, an explainable Legal Metrology compliance engine built to solve SIH26035. Unlike traditional systems that just print pass/fail PDFs, CALIBRA executes compliance rules deterministically and generates an immutable, explainable evidence chain for every single calculation."

## Step 1: The Dashboard
*(Start on the Dashboard)*
> "This is the CALIBRA Dashboard. We have a 'Sleek Dark Mode' theme tailored for a laboratory environment. The dashboard gives us an overview of active test sessions. Let's start a new test."

## Step 2: Instrument Profile (The 'Given')
*(Click on 'Instruments' in the sidebar)*
> "To test an instrument, we first define its profile. Here we have a Class III Non-Automatic Weighing Instrument (NAWI) with a max capacity of 30 kg and a verification interval of 10g."
> 
> *(Click 'Validate Profile & Generate Test Plan')*
> 
> "When we click validate, CALIBRA dynamically generates a Test Session on the backend, customized specifically to this instrument's class and capacity based on OIML R76 rules."

## Step 3: Test Workspace & Passing Scenario
*(You are now in the Test Workspace)*
> "The technician is now conducting the Weighing Performance test. Let's say they place a 10 kg reference load on the scale."
> 
> *(Ensure Reference Load is `10` and Indication is `10.008`)*
> 
> *(Click 'Validate & Calculate')*
> 
> "The engine calculates an error of +8g. The applicable Maximum Permissible Error (MPE) for a 10kg load on this Class III instrument is ±10g. So we get a clear PASS."

## Step 4: The Explainability Engine ("WHY?")
> "But here is the real magic of CALIBRA. How did the software decide it was a PASS? If an auditor asks, we must prove it."
> 
> *(Click the 'WHY?' button)*
> 
> "CALIBRA generates an Evidence Chain. It preserves the exact raw inputs, the exact formula used to calculate the error, the specific R76 rule that was applied, and the final deterministic logic decision. This entire trace is serialized and stored immutably."

## Step 5: Failing Scenario
> "What happens if it fails?"
> 
> *(Click 'Load Failing Demo Data', Indication becomes `10.012`)*
> *(Click 'Validate & Calculate')*
> 
> "The error is now +12g. The system instantly flags a FAIL because 12g > 10g threshold. The evidence chain is updated to reflect this failure precisely."

## Step 6: Automated Testing 
*(If showing the backend/automation)*
> "Because the compliance engine is entirely API-driven, it can be tested completely automatically. We have a Playwright End-to-End suite that can simulate this entire demo flow headlessly to guarantee the compliance rules are behaving exactly as expected before every deployment."
