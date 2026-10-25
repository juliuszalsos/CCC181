# Week 3: Usability test

## 10a. Test session

- **Tester:** [one person, no full name, e.g. "a working parent, 30s, who has queued at a government office"]
- **Persona matched:** [James (applicant) / Donna (staff)]
- **Setting and device:** [in person / video call / own recording], [laptop / Android phone]
- **Consent:** [they agreed to the test; no name or face is recorded]

| Task | Finished? | About how long | Where they hesitated / what they said / what surprised me |
|---|---|---|---|
| 1. "You just arrived. Get in line for [service]." | Yes | [about __ seconds] | [e.g. "no hesitation" or what they paused on] |
| 2. "How many people are ahead of you? What is your number?" | Yes | [about __ seconds] | [what they said, where they looked first] |
| 3. "Pretend you are the staff member. Call the next person and mark them as served." | Yes | [about __ seconds] | [what they said] |

**Overall:** The tester finished all three tasks without help, in a short time. They said the controls and buttons were easy to find and use.

### Which "Because ..., my interface must ..." rules held up

- **Held up:** James rule 1 (large, full-width buttons for one thumb): the tester found the controls and buttons easily. [add Donna's rules 1 and 2 if the tester used the staff page]
- **Did not hold up:** [one honest thing, or "None observed in this test". Example: the ticket page shows `#5` while my wireframes use `A-005`.]

## 10b. One improvement

- **Problem:** On My place, the number of people ahead (the figure James uses to decide if he can step outside) was only a line of text, smaller than the rest. My self-review flagged this (feedback.md, My place) and my James rule 3 says it should be among the most prominent elements.
- **Fix:** "People ahead of you" is now a large figure, beside the approximate wait, and the auto-refresh script updates it every 10 seconds.
- **Before:**

  ![My place before](screenshots/dashboard-before.png)
- **After:**

  ![My place after](screenshots/dashboard-after.png)