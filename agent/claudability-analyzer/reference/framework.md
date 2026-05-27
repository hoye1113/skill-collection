# The 6 Lenses of Claudability

When analyzing any profession or task, scan through these six lenses to find Claude Code opportunities.

---

## 1. COMPLEXITY Lens 🔀

**Question:** "Where are there many moving parts?"

**Signs:**
- Multiple steps that must happen in sequence
- Many items to track simultaneously
- Dependencies between tasks
- Easy to forget something

**Claude Code Solution:**
- Project folder with all components organized
- CLAUDE.md with the full workflow documented
- Agent that handles the sequence end-to-end

**Example:**
- Planning an event (venue, catering, invites, timeline, budget)
- Managing a project with multiple deliverables
- Coordinating between multiple people/vendors

---

## 2. CONTINUITY Lens ⏳

**Question:** "What happens over time and needs follow-up?"

**Signs:**
- Tasks that span days/weeks/months
- Need to remember what happened before
- Follow-up actions that get forgotten
- Progress tracking over time

**Claude Code Solution:**
- Persistent project folder with history
- CLAUDE.md with context that carries forward
- Regular check-in prompts ("What's the status of X?")
- Timeline tracking in markdown files

**Example:**
- Job search (applications, follow-ups, interviews)
- Learning a skill (curriculum, practice log, progress)
- Client projects (milestones, communications, deliverables)

---

## 3. PATTERNS Lens 🔄

**Question:** "What repeats with slight variations?"

**Signs:**
- Same task done many times with small differences
- Templates that need customization
- Implicit rules ("we always do X when Y")
- Batch processing potential

**Claude Code Solution:**
- Template files in templates/ folder
- Skill that applies the pattern with variables
- Rules documented in CLAUDE.md
- Batch processing scripts

**Example:**
- Generating invoices (same format, different data)
- Writing similar emails (templates with personalization)
- Creating reports (same structure, different periods)

---

## 4. INTEGRATION Lens 🔗

**Question:** "Where is information scattered?"

**Signs:**
- Data in multiple places (email, docs, spreadsheets)
- Manual copying between systems
- "Let me check..." moments
- Tribal knowledge not written down

**Claude Code Solution:**
- Central project folder that aggregates info
- MCP connections to external services
- Scripts that pull data together
- CLAUDE.md as the "brain" with all context

**Example:**
- Customer info across CRM, email, notes
- Research scattered in PDFs, bookmarks, notes
- Project status across chat, docs, tasks

---

## 5. DECISIONS Lens ⚖️

**Question:** "Where do you need to weigh options?"

**Signs:**
- Comparison shopping
- Evaluating candidates/options
- Research before choosing
- Trade-off analysis

**Claude Code Solution:**
- Research agents that gather options
- Comparison tables generated automatically
- Criteria documented in CLAUDE.md
- Decision logs for future reference

**Example:**
- Comparing vendors/suppliers
- Evaluating job candidates
- Choosing tools/software
- Planning trips (flights, hotels, activities)

---

## 6. ACTIONS Lens ⚡

**Question:** "What can be executed, not just analyzed?"

**Signs:**
- Sending communications
- Creating documents
- Publishing content
- Making reservations/bookings

**Claude Code Solution:**
- Skills that produce real output
- MCP integrations (email, WhatsApp, social)
- File generation (PDF, PPTX, images)
- API calls to external services

**Example:**
- Sending reminder emails
- Publishing social media posts
- Generating reports and PDFs
- Creating calendar events

---

## Combining Lenses

The most powerful use cases combine multiple lenses:

| Combination | Example |
|-------------|---------|
| Complexity + Continuity | Project management with phases |
| Patterns + Actions | Batch email campaigns |
| Integration + Decisions | Vendor comparison from multiple sources |
| Continuity + Actions | Follow-up sequences that send automatically |

---

## The Claudability Score

Rate each opportunity:

| Score | Description | Human Involvement |
|-------|-------------|-------------------|
| ⭐⭐⭐⭐⭐ | Fully autonomous | Set and forget |
| ⭐⭐⭐⭐ | Mostly autonomous | Occasional approval |
| ⭐⭐⭐ | Semi-autonomous | Regular check-ins |
| ⭐⭐ | Assisted | Human does most, Claude helps |
| ⭐ | Augmented | Claude provides info, human acts |

**Aim for ⭐⭐⭐⭐ or higher** - that's where the real time savings happen.

---

## The Bottleneck Test

Before recommending a solution, ask:

> "Is there ONE step that absolutely requires the human?"

If yes, design the workflow so Claude does everything EXCEPT that step:
- Prepare everything before the human step
- Take over immediately after
- Minimize the human touchpoint

**Example:** Contract review
- ❌ "Claude reviews and signs contracts" (requires human judgment)
- ✅ "Claude prepares summary, flags issues, human reviews, Claude files and follows up"
