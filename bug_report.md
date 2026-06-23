# Bug Report — Pretty Good AI Athena Voice Agent

Tested by: Siddhesh Patil
Test Date: June 22–23, 2026
Test Number Called: +1-805-439-8008
Caller Number Used: [your Twilio number in E.164 format]
Total Calls Made: 11

---

## Bug 1 — Agent Assumes Caller Identity from Phone Number

**Severity:** Critical
**Found in:** All 11 calls
**Transcript:** All call transcripts, first AGENT line

**What happened:**
Every call began with the agent asking "Am I speaking with John?" regardless of which patient introduced themselves. The agent was pulling a record associated with our Twilio phone number and assuming that was the caller.

**Why it's a problem:**
In real clinics, multiple family members and caregivers call from the same number. Assuming identity from caller ID alone is a HIPAA risk. When patients corrected the agent ("No, this is Maria Garcia"), the agent acknowledged but continued trying to verify against John's records, causing all verification attempts to fail.

**Expected behavior:**
Agent should ask "Who am I speaking with?" first, confirm the name, then look up records. Never assume identity from caller ID alone.

---

## Bug 2 — Patient Verification System Completely Broken

**Severity:** Critical
**Found in:** All 11 calls
**Transcript:** All call transcripts

**What happened:**
Every single call failed patient verification despite patients providing correct name, date of birth, and phone number. The agent consistently responded with "Something's not right" or "I'm unable to verify your information" and transferred to a representative.

**Why it's a problem:**
The core function of the AI agent is to handle patient requests autonomously. If verification always fails, the agent cannot fulfill any patient request. This renders the entire system non-functional.

**Expected behavior:**
Demo system should accept test credentials gracefully. Add a fallback verification path when primary verification fails instead of immediately escalating.

---

## Bug 3 — Representative Transfer Leads to Dead End

**Severity:** Critical
**Found in:** All 11 calls
**Transcript:** All call transcripts, final AGENT lines

**What happened:**
Every call that failed verification was transferred to a representative. The transfer always ended with: "Hello, you've reached the pretty good AI test line, goodbye." The patient was immediately disconnected with no help.

**Why it's a problem:**
Patients with urgent needs — Emily Chen with a 103°F fever, Maria Garcia with only 3 days of medication left — were completely abandoned after being promised a representative. This is the worst possible patient experience.

**Expected behavior:**
Representative transfer should connect to an actual support queue, offer a callback, or at minimum allow the patient to leave a message. The test line should not immediately hang up.

---

## Bug 4 — Garbled and Incomplete Agent Responses

**Severity:** High
**Found in:** Calls 01, 03, 04, 05, 06, 08, 09, 10
**Transcript:** Multiple locations across transcripts

**What happened:**
The agent frequently produced meaningless, cut-off, or nonsensical responses mid-conversation:

- "Buy those details." — Call 01
- "Could you please?" — Call 03 (cut off mid-sentence)
- "3 4." — Call 05 (random numbers)
- "14 followed up." — Call 04 (meaningless)
- "and," — Call 08 (single word)
- "cancel that" — Call 01 (out of context)
- "On." — Call 01 (single word response to patient greeting)

**Why it's a problem:**
Patients cannot understand what the agent is saying. Conversations break down completely. These responses suggest the agent's LLM output is being cut off before completion or the TTS is receiving incomplete text.

**Expected behavior:**
Add response validation before TTS conversion. Filter responses under 3 words or without a complete sentence structure. Use a fallback phrase like "I'm sorry, could you repeat that?" when response generation fails or is incomplete.

---

## Bug 5 — Date of Birth Requested Multiple Times in Same Call

**Severity:** High
**Found in:** Calls 03, 04, 05, 06, 08, 10
**Transcript:** Multiple DOB requests within single conversations

**What happened:**
The agent asked patients for their date of birth 3 to 4 times within the same call after the patient had already provided it and the agent had acknowledged it.

Example from Call 05 (Robert Johnson):
- Turn 4: Patient provides DOB April 12, 1948
- Turn 5: Agent confirms it
- Turn 9: Agent asks for DOB again
- Turn 11: Agent asks for DOB a third time

**Why it's a problem:**
Deeply frustrating for patients, especially elderly ones. Signals the agent has no working memory within a single conversation. Erodes patient trust immediately.

**Expected behavior:**
Store all verified information in conversation state. Once DOB is collected and acknowledged, never request it again in the same call.

---

## Bug 6 — Agent Cannot Handle Cancel and Rebook in Same Call

**Severity:** High
**Found in:** Call 01 (Simple Appointment Scheduling — latest run)
**Transcript:** call_01_Simple_Appointment_Scheduling_20260623_030046.txt

**What happened:**
When John Smith learned he already had an existing appointment and asked to cancel it and book a new one, the agent said "I'm unable to book a new routine checkup until your current one is canceled" — but never confirmed whether the cancellation actually happened. Patient was transferred to a dead-end representative line without resolution.

**Why it's a problem:**
Cancel and rebook is an extremely common patient workflow. The agent should be able to handle both actions sequentially in one call.

**Expected behavior:**
Agent should confirm cancellation first, then immediately offer available slots for the new appointment in the same conversation flow.

---

## Bug 7 — Contradictory Appointment Confirmation

**Severity:** High
**Found in:** Early test call (Simple Appointment Scheduling)
**Transcript:** call_01_Simple_Appointment_Scheduling_20260622_220513.txt

**What happened:**
After patient confirmed a Monday June 29th 10:00 AM appointment with Dr. Kelly Noble, the agent said "There was a problem booking your appointment" and then in the very next turn confirmed the appointment was successfully booked.

**Why it's a problem:**
Patients have no idea whether their appointment is actually confirmed. This could lead to missed appointments, double bookings, or patients calling back unnecessarily.

**Expected behavior:**
Booking confirmation should be a single definitive response. Implement proper error handling that retries the booking before informing the patient of a failure.

---

## Bug 8 — Call Dropped Prematurely

**Severity:** Medium
**Found in:** Call 07 (Weekend Appointment Request)
**Transcript:** call_07_Weekend_Appointment_Request_20260622_223647.txt

**What happened:**
The Michael Brown call transcript ended after only 2 exchanges. The agent had just acknowledged David's correction and the call disconnected without any resolution.

**Why it's a problem:**
Patient request was never handled. Premature disconnection with no callback or resolution is a poor patient experience.

**Expected behavior:**
Implement call stability monitoring. If a call drops unexpectedly, trigger an automatic callback or log the incomplete interaction for follow-up.

---

## Bug 9 — Agent Cannot Answer Basic Clinic Questions

**Severity:** Medium
**Found in:** Call 04 (Insurance Question — Susan White)
**Transcript:** call_04_Insurance_Question_20260622_223647.txt

**What happened:**
Susan White asked repeatedly whether the clinic accepts Aetna PPO insurance. The agent never answered the question directly and instead transferred her to a representative after 17 exchanges.

**Why it's a problem:**
Insurance acceptance is one of the most common questions patients ask before scheduling. This should be answerable instantly without human escalation. The agent wasted the patient's time across 17 turns before failing to help.

**Expected behavior:**
Agent should have access to a clinic knowledge base covering accepted insurance plans, office hours, location, and parking. These FAQs should never require human escalation.

---

## Bug 10 — Speech Recognition Errors Cause Wrong Agent Behavior

**Severity:** Medium
**Found in:** Calls 01, 03
**Transcript:** call_01, call_03 transcripts

**What happened:**
- "in the morning" was transcribed and acted upon as "in the boarding"
- Phone numbers were misheard: "555-123-4567" became "55512 3 4 5" causing verification to fail

**Why it's a problem:**
The agent acts on incorrect transcriptions without asking for clarification, leading to wrong responses and failed verifications. A patient's entire request can fail because of a single speech recognition error.

**Expected behavior:**
Add confidence thresholds on speech recognition. When confidence is low, ask the patient to repeat rather than acting on garbled input. For critical fields like phone numbers and dates, always read back and confirm before proceeding.

---

## Summary Table

| # | Bug | Severity | Calls Affected |
|---|-----|----------|----------------|
| 1 | Assumes caller identity from phone number | Critical | All 11 |
| 2 | Verification system completely broken | Critical | All 11 |
| 3 | Representative transfer is a dead end | Critical | All 11 |
| 4 | Garbled and incomplete responses | High | 8 of 11 |
| 5 | DOB requested multiple times | High | 6 of 11 |
| 6 | Cannot cancel and rebook in same call | High | 1 of 11 |
| 7 | Contradictory appointment confirmation | High | 1 of 11 |
| 8 | Call dropped prematurely | Medium | 1 of 11 |
| 9 | Cannot answer basic clinic questions | Medium | 1 of 11 |
| 10 | Speech recognition errors cause wrong behavior | Medium | 2 of 11 |