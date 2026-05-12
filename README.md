# 🌟 Calm Corner Check-In

A child-friendly digital check-in tool for behavior support specialists in afterschool programs. Students identify their emotions using the Zones of Regulation framework and choose a calm-down strategy from the calm corner — while specialists quietly track patterns and add private notes from a password-protected dashboard.

## What It Does

- **Guides students through a structured emotional check-in** using the Zones of Regulation framework (Blue, Green, Yellow, Red), with feeling-specific calm corner strategies tailored to each emotion
- **Tracks key context for every visit** — student name, grade, group, whether the student self-referred or was sent by their rec leader, feeling identified, strategy chosen, and time spent
- **Gives behavior support specialists a private dashboard** with per-student check-in histories, zone and referral breakdowns, private observation notes, and downloadable CSV data
- **Fully customizable** — groups, colors, grade assignments, and staff password are all configurable through the dashboard with no code changes required

## How to Use

### For Students
1. Type your name and tap **Let's Start**
2. Select your grade — your rec group options appear automatically
3. Choose how you got to the calm corner — "I asked to come" or "My rec leader sent me"
4. Pick the color zone that matches how your body feels right now
5. Choose the specific feeling that fits best
6. Pick a calm corner tool to try
7. Read your affirmation and tap **New Check-In** when done

The screen automatically resets after 1 minute of inactivity so the next student always starts fresh.

### For Behavior Support Specialists
1. Open the **sidebar** (arrow at top-left)
2. Enter the staff password to unlock the Specialist Dashboard
3. View recent check-ins, zone breakdowns, and referral type data
4. Tap any student's name to see their full individual check-in history
5. Use the small **`+`** button on the completion screen to add private observation notes
6. Download all data or a single student's data as a CSV
7. Tap **Lock Dashboard** when finished to secure the view before the next student

### Customizing for Your Program
1. Unlock the Specialist Dashboard
2. Scroll to **⚙️ Program Settings** at the bottom of the sidebar
3. Under **Groups** — add, edit, or delete groups; set each group's name, color, and which grades it appears for
4. Under **Password** — change the staff password
5. All changes save instantly with no restart required

## Two Versions

| File | Purpose |
|---|---|
| `app.py` | Fully configured for Anna Yates Expanded Learning Program — groups, colors, and grade assignments pre-loaded |
| `app_template.py` | Blank slate for any program to set up from scratch — no groups pre-loaded, default password is `changeme` |

`app_template.py` displays a welcome popup on first load showing the current staff password, making it easy to hand off to any new program.

## Data

All check-in data is saved automatically to `data_ai/checkins.csv`. Each record includes:

| Column | Description |
|---|---|
| `Date` | Date of the check-in |
| `Start Time` | Time the student began the check-in |
| `End Time` | Time the check-in was completed |
| `Duration (min)` | Minutes spent on the check-in |
| `Student Name` | Student's first name as entered |
| `Grade` | Grade level (TK–8th) |
| `Rec Group` | Assigned rec group |
| `Referral Type` | `Self` or `Referred` |
| `Zone` | Zones of Regulation color selected (Blue, Green, Yellow, Red) |
| `Feeling` | Specific feeling chosen within that zone |
| `Strategy Used` | Calm corner tool the student selected |
| `Specialist Notes` | Private notes added by the behavior support specialist |

Data is formatted for direct use in Excel or Google Sheets — no cleanup needed.

## Built With

- [Streamlit](https://streamlit.io) — web app framework
- [Pandas](https://pandas.pydata.org) — data storage and dashboard analytics
- Zones of Regulation framework — four-zone emotional regulation model (Blue, Green, Yellow, Red)
