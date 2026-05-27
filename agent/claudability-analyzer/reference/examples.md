# Claudability Analysis Examples

20 diverse examples showing how to break down any profession into Claude Code use cases.

**NOTE:** Each analysis should include a "Day In Your Life" narrative - see the Guitar Teacher example for the full format.

---

## FULL EXAMPLE: 🎸 Private Music Teacher (Guitar)

### Technical Specification

**Context:** Teaches 15 private students, schedules lessons, tracks progress, communicates with parents, assigns practice.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Lesson Preparation** | ⭐⭐⭐⭐⭐ | 30 min/student |
| **Progress Tracking** | ⭐⭐⭐⭐ | 1 hr/week |
| **Parent Updates** | ⭐⭐⭐⭐⭐ | 2 hrs/month |
| **Payment Tracking** | ⭐⭐⭐⭐⭐ | 30 min/month |

**Folder Structure:**
```
guitar-teaching/
├── CLAUDE.md                    # Teaching methodology, preferences
├── students/
│   ├── dana.md                  # Profile + full history
│   └── ...
├── curriculum/
│   ├── beginner.md              # Progression path
│   └── songs/                   # Songs by level
├── templates/
│   ├── lesson-plan.md
│   ├── progress-report.md
│   └── payment-reminder.md
└── .claude/skills/
    ├── lesson-prep/
    ├── parent-update/
    └── payment-tracker/
```

**Tech Stack:**
- **Skills:** lesson-prep (reads history → curriculum → generates plan)
- **MCP/APIs:** WhatsApp (send updates), Google Calendar (scheduling)
- **Libraries:** Markdown→PDF for reports

---

### A Day With Claude Code: Private Guitar Teacher

#### BEFORE (The Pain)

**07:30** - Wake up, 3 WhatsApp messages: "Can we reschedule?", "Yonatan is sick", "When is payment due?"

**08:00** - Open Excel with student list. Try to remember what Dana learned last week. Was it chords or still strumming? No idea.

**09:00** - First lesson. Mid-lesson, remember promised to send Yoav a link to a song. Forget.

**12:00** - Need to plan next month. Open blank document. Stare at it.

**18:00** - Noam's mom calls: "How is he progressing?" Have nothing organized to say.

**21:00** - Remember didn't send payment reminders. Too late now.

**Feeling:** Scattered, unprofessional, always catching up.

---

#### AFTER (The Magic)

**07:30** - Wake up, open terminal:

```bash
claude "מה המצב להיום?"
```

> **בוקר טוב! היום יש לך 4 שיעורים:**
>
> - 09:00 דנה - **עברה לאקורדים בשבוע שעבר**, היום G-C-D
> - 11:00 יואב - **עדיין חייב לו קישור לשיר "יש בי אהבה"** - לשלוח?
> - 14:00 נועם - אמא שלו שאלה על התקדמות, **הכנתי טיוטת דוח**
> - 17:00 תומר - שיעור ראשון, **הכנתי תוכנית היכרות**
>
> **גם:** 3 תלמידים לא שילמו החודש (יונתן, מיכל, אורי)

```bash
"תשלח ליואב את הקישור ותזכורת תשלום לשלושת הנ״ל"
```

> שולח ליואב: [קישור + "כמו שדיברנו, תתרגל את הקטע הזה"]
> שולח תזכורת תשלום ל-3 (מותאם אישית לכל אחד)
> ...נשלח ✓

---

**09:00** - Before Dana's lesson:

```bash
claude "תכין לי את השיעור של דנה"
```

> **שיעור דנה - 45 דק'**
>
> **חימום (5 דק'):** תרגילי אצבעות + חזרה על Am-E
>
> **עיקרי (30 דק'):**
> - למידת אקורד G (אחיזה, מעברים)
> - מעבר G→C→D
> - שיר: "שיר משמח" - רק 3 האקורדים האלה
>
> **משימה לבית:** 10 דק' מעברים + הקלטה
>
> **לשים לב:** בפעם הקודמת התקשתה עם אצבע 4

After the lesson:

```bash
"דנה סיימה, הלך טוב, עדיין קשה לה עם הזרת"
```

> עודכן ב-students/dana.md ✓

---

**14:00** - Before Noam's lesson:

```bash
claude "תכין דוח התקדמות לאמא של נועם"
```

> **דוח התקדמות - נועם (3 חודשים ראשונים)**
>
> **מה למדנו:** אחיזה, 4 אקורדים, 2 שירים, התחלת פריטה
> **חוזקות:** קצב מעולה, מתרגל בבית
> **לעבוד על:** דיוק במעברים
> **המלצה:** להמשיך בקצב, עוד חודש מוכן לשיר עם פריטה
>
> רוצה שאשלח לאמא?

```bash
"כן"
```

> נשלח PDF מעוצב לוואטסאפ ✓

---

**21:00** - End of day:

```bash
claude "סיכום יום"
```

> **סיכום 28.1:**
> - 4 שיעורים ✓
> - נשלחו: קישור ליואב, 3 תזכורות, דוח לאמא
> - יונתן שילם (התקבל אישור)
>
> **מחר:** 3 שיעורים, להכין תוכנית לתומר
>
> **שבוע הבא:** דנה מתקרבת לשיר שלם ראשון - לתכנן חגיגה?

**Feeling:** In control, professional, everything tracked.

---

#### What's Happening Behind the Scenes

| Component | What It Does |
|-----------|--------------|
| **CLAUDE.md** | "I teach guitar, my method is progressive, I like short daily practice over long sessions..." |
| **students/*.md** | Full history - every lesson, every note, every observation |
| **lesson-prep skill** | Reads history → checks curriculum → picks appropriate song → generates plan |
| **WhatsApp MCP** | Actually sends messages (not just drafts) |
| **PDF generation** | Creates professional reports from markdown |

#### The Magic Moments

1. **Claude remembers** - You never told it about Yoav's link, but it tracked it from a previous conversation
2. **Claude prepares** - Before you even ask, it noticed the mom asked about progress
3. **Claude acts** - Doesn't just suggest sending a reminder, actually sends it
4. **Claude learns** - If you always want reports in a certain format, it adapts

---

## 1. 🎓 High School Teacher (Gemara/Religious Studies)

**Context:** Teaches Talmud, prepares worksheets, grades exams, tracks student progress, coordinates trips.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Exam Grading Pipeline** | ⭐⭐⭐⭐ | 3 hrs/week |
| Scan answers → Grade with rubric → Generate feedback → Update student tracker → Identify struggling students |
| **Worksheet Generator** | ⭐⭐⭐⭐⭐ | 2 hrs/week |
| Topic → Pull relevant texts → Format with questions → Add illustrations → Export PDF |
| **Student Progress Dashboard** | ⭐⭐⭐⭐ | 1 hr/week |
| Aggregate grades → Identify patterns → Flag at-risk students → Generate parent reports |
| **Trip Logistics Manager** | ⭐⭐⭐⭐ | 4 hrs/trip |
| Checklist → Vendor coordination → Permission slips → Timeline → Day-of logistics |

---

## 2. 🏠 Real Estate Agent

**Context:** Manages listings, coordinates showings, communicates with clients, prepares contracts.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Listing Description Generator** | ⭐⭐⭐⭐⭐ | 30 min/listing |
| Property details → Generate description → Multiple versions (web, print, social) |
| **Client Communication Manager** | ⭐⭐⭐⭐ | 2 hrs/week |
| Track all clients → Auto-draft follow-ups → Schedule check-ins → Log interactions |
| **Showing Coordinator** | ⭐⭐⭐⭐ | 1 hr/week |
| Match availability → Propose times → Send confirmations → Reminders → Feedback collection |
| **Market Analysis Reports** | ⭐⭐⭐⭐ | 2 hrs/report |
| Pull comparable sales → Analyze trends → Generate report → Personalize for client |

---

## 3. 👰 Wedding Planner (or DIY Couple)

**Context:** 500 tasks across 12 months, multiple vendors, budget tracking, guest management.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Vendor Comparison Engine** | ⭐⭐⭐⭐ | 5 hrs/category |
| Research vendors → Create comparison matrix → Track quotes → Decision support |
| **Guest List Manager** | ⭐⭐⭐⭐⭐ | 3 hrs/month |
| Track RSVPs → Dietary restrictions → Seating suggestions → Thank you note tracking |
| **Budget Tracker** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Log expenses → Compare to budget → Alert on overruns → Generate reports |
| **Timeline Orchestrator** | ⭐⭐⭐⭐ | 2 hrs/week |
| What needs to happen when → Send reminders → Track completion → Adjust timeline |

---

## 4. 🍳 Home Cook / Meal Planner

**Context:** Plans weekly meals, shops for groceries, tracks pantry, manages recipes.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Weekly Meal Planner** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Preferences + pantry → Generate meal plan → Shopping list → Prep schedule |
| **Recipe Organizer** | ⭐⭐⭐⭐⭐ | 30 min/week |
| Collect recipes from anywhere → Standardize format → Tag and categorize → Search |
| **Pantry Manager** | ⭐⭐⭐⭐ | 30 min/week |
| Track what you have → Expiration alerts → Suggest meals based on inventory |
| **Dietary Tracker** | ⭐⭐⭐⭐ | 15 min/day |
| Log meals → Calculate nutrition → Track goals → Weekly summary |

---

## 5. 📦 Small E-commerce Seller

**Context:** Sells on Etsy/eBay, manages inventory, ships orders, handles customer service.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Order Processing Pipeline** | ⭐⭐⭐⭐ | 1 hr/day |
| New order → Print label → Update inventory → Send shipping notification |
| **Customer Service Responder** | ⭐⭐⭐⭐ | 2 hrs/day |
| Categorize inquiries → Draft responses → Track resolution → Escalate complex |
| **Listing Optimizer** | ⭐⭐⭐⭐⭐ | 30 min/listing |
| Analyze competitors → Suggest keywords → Generate descriptions → A/B test titles |
| **Inventory Forecaster** | ⭐⭐⭐⭐ | 1 hr/week |
| Track sales patterns → Predict restocking needs → Alert low inventory |

---

## 6. 🎸 Music Teacher (Private Lessons)

**Context:** Teaches guitar/piano, schedules lessons, tracks student progress, assigns practice.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Lesson Planner** | ⭐⭐⭐⭐⭐ | 30 min/student/week |
| Student level + goals → Generate lesson plan → Practice assignments → Resources |
| **Progress Tracker** | ⭐⭐⭐⭐ | 1 hr/week |
| Log each lesson → Track skills mastered → Identify gaps → Parent updates |
| **Practice Reminder System** | ⭐⭐⭐⭐⭐ | 15 min/day |
| Daily reminders → Practice log → Weekly summary → Encouragement messages |
| **Recital Organizer** | ⭐⭐⭐⭐ | 3 hrs/event |
| Program creation → Schedule slots → Parent communications → Day-of runsheet |

---

## 7. 🏋️ Personal Trainer / Fitness Coach

**Context:** Creates workout plans, tracks client progress, manages scheduling, nutrition advice.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Workout Generator** | ⭐⭐⭐⭐⭐ | 1 hr/client/week |
| Client goals + history → Generate workout → Progressions → Export to PDF |
| **Client Progress Dashboard** | ⭐⭐⭐⭐ | 2 hrs/week |
| Aggregate metrics → Visualize progress → Identify plateaus → Adjust programs |
| **Check-in Automator** | ⭐⭐⭐⭐⭐ | 30 min/day |
| Weekly check-in form → Analyze responses → Flag concerns → Draft feedback |
| **Content Creator** | ⭐⭐⭐⭐⭐ | 2 hrs/week |
| Generate workout tips → Social posts → Email newsletters → Video scripts |

---

## 8. 📚 Book Editor / Proofreader

**Context:** Edits manuscripts, tracks revisions, communicates with authors, manages deadlines.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Manuscript Organizer** | ⭐⭐⭐⭐⭐ | 1 hr/book |
| Incoming files → Standardize format → Create chapter structure → Version control |
| **Style Consistency Checker** | ⭐⭐⭐⭐ | 2 hrs/book |
| Scan for inconsistencies (names, dates, terms) → Flag for review |
| **Author Communication Hub** | ⭐⭐⭐⭐ | 1 hr/week |
| Track all queries → Draft responses → Log decisions → Timeline updates |
| **Invoice & Project Tracker** | ⭐⭐⭐⭐⭐ | 30 min/week |
| Log hours → Generate invoices → Track payments → Project status dashboard |

---

## 9. 🏥 Medical Office Manager

**Context:** Schedules appointments, manages patient communications, handles insurance, orders supplies.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Appointment Reminder System** | ⭐⭐⭐⭐⭐ | 1 hr/day |
| Tomorrow's appointments → Send reminders → Track confirmations → Fill cancellations |
| **Insurance Verification Prep** | ⭐⭐⭐⭐ | 2 hrs/day |
| Pull patient info → Check eligibility requirements → Prepare documents |
| **Supply Inventory Manager** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Track usage → Predict needs → Generate orders → Compare vendors |
| **Patient Follow-up Coordinator** | ⭐⭐⭐⭐ | 1 hr/day |
| Post-visit instructions → Follow-up scheduling → Reminder sequences |

---

## 10. 🎨 Freelance Designer

**Context:** Manages clients, creates proposals, tracks projects, handles billing.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Proposal Generator** | ⭐⭐⭐⭐⭐ | 1 hr/proposal |
| Client brief → Generate proposal → Pricing options → Timeline → Export PDF |
| **Project Status Tracker** | ⭐⭐⭐⭐ | 30 min/day |
| Track all projects → Milestone updates → Client communications → Deadline alerts |
| **Portfolio Updater** | ⭐⭐⭐⭐ | 1 hr/month |
| New project → Generate case study → Update portfolio → Social announcements |
| **Client Onboarding** | ⭐⭐⭐⭐⭐ | 30 min/client |
| Welcome sequence → Collect requirements → Set up project folder → Kickoff agenda |

---

## 11. 🌱 Home Gardener

**Context:** Plans garden, tracks planting schedules, monitors plant health, researches solutions.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Planting Calendar** | ⭐⭐⭐⭐⭐ | 2 hrs/season |
| Your zone + plants → Optimal planting dates → Reminders → Harvest predictions |
| **Plant Health Tracker** | ⭐⭐⭐⭐ | 15 min/week |
| Log observations → Identify issues → Research solutions → Track treatments |
| **Garden Journal** | ⭐⭐⭐⭐⭐ | 10 min/day |
| Daily log → Photo organization → Season summaries → Lessons learned |
| **Seed & Supply Manager** | ⭐⭐⭐⭐⭐ | 30 min/month |
| Inventory → Order suggestions → Vendor comparison → Budget tracking |

---

## 12. 🎙️ Podcast Host

**Context:** Plans episodes, books guests, edits shows, manages promotion.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Episode Planner** | ⭐⭐⭐⭐⭐ | 1 hr/episode |
| Topic → Research → Outline → Interview questions → Show notes draft |
| **Guest Coordinator** | ⭐⭐⭐⭐ | 2 hrs/guest |
| Outreach emails → Scheduling → Pre-interview brief → Post-interview thank you |
| **Show Notes Generator** | ⭐⭐⭐⭐⭐ | 30 min/episode |
| Transcript → Key points → Timestamps → Links → SEO description |
| **Promotion Automator** | ⭐⭐⭐⭐⭐ | 1 hr/episode |
| Generate clips suggestions → Social posts → Email newsletter → Cross-platform posting |

---

## 13. 📊 Non-Profit Program Manager

**Context:** Manages programs, tracks outcomes, writes reports, communicates with donors.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Grant Report Generator** | ⭐⭐⭐⭐ | 4 hrs/report |
| Pull program data → Match to grant requirements → Generate narrative → Format |
| **Donor Communication Manager** | ⭐⭐⭐⭐⭐ | 2 hrs/week |
| Track donors → Personalized updates → Thank you letters → Renewal reminders |
| **Volunteer Coordinator** | ⭐⭐⭐⭐ | 2 hrs/week |
| Scheduling → Reminders → Hour tracking → Recognition → Surveys |
| **Impact Dashboard** | ⭐⭐⭐⭐ | 1 hr/week |
| Aggregate outcomes → Visualize impact → Compare to goals → Board reports |

---

## 14. 🏠 Property Manager (Small Portfolio)

**Context:** Manages 5-10 rental units, handles maintenance, collects rent, communicates with tenants.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Rent Collection Tracker** | ⭐⭐⭐⭐⭐ | 1 hr/month |
| Track payments → Send reminders → Log late fees → Generate statements |
| **Maintenance Request Handler** | ⭐⭐⭐⭐ | 2 hrs/week |
| Receive requests → Categorize → Assign contractors → Track completion → Invoice |
| **Lease Renewal Manager** | ⭐⭐⭐⭐ | 1 hr/tenant |
| Track expiration → Send notices → Generate renewal docs → Follow-up sequence |
| **Expense Tracker** | ⭐⭐⭐⭐⭐ | 1 hr/month |
| Log expenses by property → Categorize → Tax reports → P&L statements |

---

## 15. 🍷 Wine Enthusiast / Collector

**Context:** Tracks collection, logs tastings, plans purchases, manages cellar.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Cellar Inventory Manager** | ⭐⭐⭐⭐⭐ | 30 min/month |
| Track bottles → Drinking windows → Location mapping → Value tracking |
| **Tasting Notes Organizer** | ⭐⭐⭐⭐⭐ | 10 min/tasting |
| Log tasting → Structured notes → Rating → Food pairings → Photos |
| **Purchase Advisor** | ⭐⭐⭐⭐ | 1 hr/month |
| Based on preferences → Suggest purchases → Compare prices → Track allocations |
| **Dinner Party Planner** | ⭐⭐⭐⭐⭐ | 30 min/event |
| Menu → Wine pairings from cellar → Serving order → Temperature timeline |

---

## 16. 🎓 PhD Student / Researcher

**Context:** Manages literature, writes papers, tracks experiments, navigates bureaucracy.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Literature Review Manager** | ⭐⭐⭐⭐ | 5 hrs/week |
| Organize papers → Extract key findings → Track citations → Identify gaps |
| **Writing Assistant** | ⭐⭐⭐⭐ | 2 hrs/paper section |
| Outline → Draft sections → Consistency check → Citation formatting |
| **Experiment Tracker** | ⭐⭐⭐⭐ | 1 hr/week |
| Log experiments → Track parameters → Document results → Version control |
| **Admin Navigator** | ⭐⭐⭐⭐ | 2 hrs/semester |
| Deadline tracking → Form preparation → Email drafts → Meeting scheduling |

---

## 17. 🐕 Dog Walker / Pet Sitter

**Context:** Manages schedule, tracks pets, communicates with owners, handles billing.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Schedule Optimizer** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Client requests → Route optimization → Conflict detection → Confirmations |
| **Pet Profile Manager** | ⭐⭐⭐⭐⭐ | 15 min/pet |
| Vet info → Medications → Preferences → Emergency contacts → Updates |
| **Client Update Automator** | ⭐⭐⭐⭐⭐ | 30 min/day |
| Visit completed → Photo + note → Send update → Log in system |
| **Invoice Generator** | ⭐⭐⭐⭐⭐ | 30 min/week |
| Track visits → Calculate charges → Generate invoices → Payment reminders |

---

## 18. ✈️ Travel Planner (Personal or Professional)

**Context:** Plans trips, compares options, manages itineraries, tracks bookings.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Trip Research Engine** | ⭐⭐⭐⭐ | 3 hrs/trip |
| Destination → Activities → Restaurants → Logistics → Comparison matrix |
| **Itinerary Builder** | ⭐⭐⭐⭐⭐ | 2 hrs/trip |
| All bookings → Day-by-day schedule → Maps → Confirmation numbers |
| **Booking Tracker** | ⭐⭐⭐⭐⭐ | 30 min/trip |
| All confirmations → Organized by date → Reminder system → Cancellation tracking |
| **Packing List Generator** | ⭐⭐⭐⭐⭐ | 15 min/trip |
| Destination + activities → Customized packing list → Weather-appropriate |

---

## 19. 📱 Social Media Manager (Small Business)

**Context:** Creates content, schedules posts, tracks engagement, manages community.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Content Calendar Manager** | ⭐⭐⭐⭐⭐ | 2 hrs/week |
| Plan themes → Generate post ideas → Schedule → Track what's posted |
| **Post Adapter** | ⭐⭐⭐⭐⭐ | 30 min/post |
| One piece of content → Adapt for each platform → Optimal formatting |
| **Engagement Tracker** | ⭐⭐⭐⭐ | 1 hr/week |
| Pull metrics → Identify top performers → Suggest improvements → Report |
| **Comment Responder** | ⭐⭐⭐⭐ | 1 hr/day |
| Monitor comments → Draft responses → Flag issues → Track sentiment |

---

## 20. 🏠 Parent Managing Family Life

**Context:** Coordinates schedules, manages household, tracks kids' activities, handles logistics.

| Use Case | Claudability | Time Saved |
|----------|--------------|------------|
| **Family Calendar Coordinator** | ⭐⭐⭐⭐ | 2 hrs/week |
| All activities → Conflict detection → Carpool coordination → Reminders |
| **School Communication Hub** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Track all school emails → Extract action items → Calendar integration → Follow-up |
| **Household Task Manager** | ⭐⭐⭐⭐⭐ | 1 hr/week |
| Chore rotation → Reminders → Tracking → Reward system |
| **Activity Logistics** | ⭐⭐⭐⭐ | 1 hr/week |
| Soccer practice, piano, etc. → Equipment checklists → Schedule → Carpools |

---

## Pattern Recognition

Across all 20 examples, the most common high-value use cases are:

1. **Communication Management** (emails, messages, updates)
2. **Schedule/Calendar Coordination** (conflicts, reminders, logistics)
3. **Progress Tracking** (students, clients, projects)
4. **Document Generation** (reports, invoices, proposals)
5. **Research & Comparison** (vendors, options, data)
6. **Inventory/Asset Management** (supplies, files, collections)

These patterns appear in virtually EVERY profession.
