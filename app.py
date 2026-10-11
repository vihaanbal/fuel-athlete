import base64
import json
import os
import re
import secrets
import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
from requests_oauthlib import OAuth1
from supabase import create_client
from supabase.client import ClientOptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


st.set_page_config(page_title="Fuel Athlete", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(rgba(247,245,238,.82), rgba(230,239,235,.86)),
        url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=2200&q=85') center / cover fixed;
}
[data-testid="stMainBlockContainer"] { max-width: 1250px; padding-top: 2rem; }
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,251,245,.88);
    border: 1px solid rgba(204,220,213,.9);
    backdrop-filter: blur(8px);
}
[data-testid="stSidebar"] { background: #103e46; }
[data-testid="stSidebar"] p { color: #f4faf8; }
[data-testid="stMainBlockContainer"] :is(h1,h2,h3,p,label) { color: #183e46; }
[data-testid="stWidgetLabel"] p { font-weight: 600; }
input::placeholder { color: #87999c; opacity: 1; }
button[kind="primary"] { background: #2f8188; border-color: #2f8188; }
button[kind="primary"] p { color: white; }
</style>
""", unsafe_allow_html=True)

def config(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except Exception:
        return None


SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_KEY = config("SUPABASE_KEY")
USDA_KEY = config("USDA_API_KEY")
FATSECRET_KEY = config("FATSECRET_CONSUMER_KEY")
FATSECRET_SECRET = config("FATSECRET_CONSUMER_SECRET")
APP_URL = (config("APP_URL") or "https://fuel-athlete-cn7ftxcdmnrlemk25camwp.streamlit.app").rstrip("/") + "/"
CALENDAR_SCOPE = ["https://www.googleapis.com/auth/calendar.events.readonly"]


def admin_key(key):
    if key.startswith("sb_secret_"):
        return True
    try:
        encoded = key.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        return claims.get("role") == "service_role"
    except (IndexError, ValueError, TypeError):
        return False


if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Add your Supabase URL and publishable key to the app's secrets.")
    st.stop()
if admin_key(SUPABASE_KEY):
    st.error("Use a publishable Supabase key, not a service-role key.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class ResetStore:
    def __init__(self, reset_id):
        self.path = f"/tmp/fuel_reset_{reset_id}.json"

    def get_item(self, key):
        try:
            with open(self.path) as handle:
                return json.load(handle).get(key)
        except (OSError, ValueError):
            return None

    def set_item(self, key, value):
        data = {}
        try:
            with open(self.path) as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            pass
        data[key] = value
        fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(data, handle)

    def remove_item(self, key):
        try:
            with open(self.path) as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            return
        data.pop(key, None)
        fd = os.open(self.path, os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(data, handle)


def reset_client(reset_id):
    return create_client(SUPABASE_URL, SUPABASE_KEY, options=ClientOptions(
        storage=ResetStore(reset_id), flow_type="pkce"
    ))


def fatsecret_search(query):
    auth = OAuth1(FATSECRET_KEY, FATSECRET_SECRET, signature_type="QUERY")
    response = requests.get(
        "https://platform.fatsecret.com/rest/foods/search/v1",
        params={"search_expression": query, "max_results": 15, "format": "json"},
        auth=auth, timeout=12,
    )
    response.raise_for_status()
    foods = response.json().get("foods", {}).get("food", [])
    if isinstance(foods, dict):
        foods = [foods]
    found = []
    for food in foods:
        found.append({
            "fdcId": "fatsecret:" + str(food.get("food_id", "")),
            "description": food.get("food_name", "Unknown food"),
            "brandOwner": food.get("brand_name", ""),
            "source": "FatSecret",
            "fatsecretFoodId": food.get("food_id", ""),
            "nutritionComparable": False,
            "servingDescription": "see serving details",
            "foodNutrients": [],
        })
    return found


def fatsecret_details(food_id):
    auth = OAuth1(FATSECRET_KEY, FATSECRET_SECRET, signature_type="QUERY")
    response = requests.get(
        "https://platform.fatsecret.com/rest/food/v5",
        params={"food_id": food_id, "format": "json"},
        auth=auth, timeout=12,
    )
    response.raise_for_status()
    item = response.json().get("food", {})
    servings = item.get("servings", {}).get("serving", [])
    if isinstance(servings, dict):
        servings = [servings]
    if not servings:
        return None

    def weight(serving):
        try:
            quantity = float(serving.get("metric_serving_amount") or 0)
        except (ValueError, TypeError):
            quantity = 0
        if str(serving.get("metric_serving_unit") or "").lower() in ("g", "gram", "grams") and quantity > 0:
            return quantity
        if re.fullmatch(r"100\s*g", str(serving.get("serving_description", "")), re.I):
            return 100.0
        return None

    serving = next((s for s in servings if weight(s) == 100), None)
    if serving is None:
        serving = next((s for s in servings if weight(s)), servings[0])
    grams = weight(serving)

    def nutrient(field):
        try:
            value = float(serving.get(field) or 0)
            return round(value * (100 / grams), 2) if grams else value
        except (ValueError, TypeError):
            return 0.0

    return {
        "fdcId": "fatsecret:" + str(item.get("food_id", food_id)),
        "description": item.get("food_name", "Unknown food"),
        "brandOwner": item.get("brand_name", ""),
        "source": "FatSecret",
        "fatsecretFoodId": food_id,
        "nutritionComparable": grams is not None,
        "servingDescription": "100 g" if grams else serving.get("serving_description", "serving"),
        "foodNutrients": [
            {"nutrientName": "Carbohydrate", "value": nutrient("carbohydrate")},
            {"nutrientName": "Protein", "value": nutrient("protein")},
            {"nutrientName": "Total lipid (fat)", "value": nutrient("fat")},
        ],
    }


def search_foods(query):
    results = []
    failed = 0
    providers = 0
    if FATSECRET_KEY and FATSECRET_SECRET:
        providers += 1
        try:
            results = fatsecret_search(query)
        except (requests.RequestException, ValueError, KeyError, TypeError):
            failed += 1
    if not results and USDA_KEY:
        providers += 1
        try:
            response = requests.get(
                "https://api.nal.usda.gov/fdc/v1/foods/search",
                params={"api_key": USDA_KEY, "query": query, "pageSize": 15},
                timeout=12,
            )
            response.raise_for_status()
            results = response.json().get("foods", [])
            for item in results:
                item["source"] = "USDA"
                item["servingDescription"] = "100 g"
                item["nutritionComparable"] = True
        except (requests.RequestException, ValueError, KeyError, TypeError):
            failed += 1
    if not providers:
        st.error("Food search is not configured. Add your FatSecret or USDA key.")
    elif failed == providers:
        st.error("The food databases are unavailable. Please try again.")
    return results


def macros(food):
    carbs = protein = fat = 0.0
    for nutrient in food.get("foodNutrients", []):
        name = str(nutrient.get("nutrientName", "")).lower()
        try:
            value = float(nutrient.get("value") or 0)
        except (ValueError, TypeError):
            continue
        if "carbohydrate" in name:
            carbs = value
        elif "protein" in name:
            protein = value
        elif "total lipid" in name or "total fat" in name:
            fat = value
    return carbs, protein, fat


def ranked_foods(foods, minutes=60, recovery=False):
    ranked = []
    for food in foods:
        if food.get("nutritionComparable") is False:
            continue
        carbs, protein, fat = macros(food)
        if carbs == protein == fat == 0:
            continue
        if recovery:
            score = 1.5 * carbs + 2 * protein - .5 * fat
        elif minutes <= 30:
            score = 2 * min(carbs, 60) - 3 * min(fat, 25) - min(protein, 30)
        elif minutes <= 90:
            score = 1.5 * min(carbs, 60) + .5 * min(protein, 30) - 1.5 * min(fat, 25)
        else:
            score = min(carbs, 60) + min(protein, 30) - min(fat, 25)
        ranked.append((score, food))
    return sorted(ranked, key=lambda item: item[0], reverse=True)[:3]


def readiness(energy, hours, meal, workout, hydration):
    score = 100 - {"High": 0, "Medium": 10, "Low": 25}[energy]
    deductions = {"Full meal": (5, 15, 25), "Light meal": (10, 20, 30), "Snack": (15, 25, 35)}
    if hours == 4:
        score -= deductions[meal][0]
    elif hours in (5, 6):
        score -= deductions[meal][1]
    elif hours >= 7:
        score -= deductions[meal][2]
    if workout in ("Cardio / Endurance", "Strength Training", "HIIT / Conditioning", "Game / Competition") and hours >= 4:
        score -= 5
    score -= {"Well hydrated": 0, "A little thirsty": 10, "Very thirsty": 25}[hydration]
    return max(score, 0)


def google_flow(state=None):
    client_id = config("GOOGLE_CLIENT_ID")
    client_secret = config("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None
    client_config = {"web": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [APP_URL],
    }}
    return Flow.from_client_config(client_config, scopes=CALENDAR_SCOPE,
                                   state=state, redirect_uri=APP_URL,
                                   autogenerate_code_verifier=False)


def calendar_connection(show_button=False):
    user_id = str(uuid.UUID(str(st.session_state.user_id)))
    token_path = f"/tmp/fuel_calendar_{user_id}.json"
    state_path = f"/tmp/fuel_calendar_state_{user_id}.txt"

    if os.path.isfile(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, CALENDAR_SCOPE)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                fd = os.open(token_path, os.O_WRONLY | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w") as handle:
                    handle.write(creds.to_json())
            if creds.valid:
                return creds
        except Exception:
            st.caption("Reconnect Google Calendar from Settings.")
        try:
            os.remove(token_path)
        except OSError:
            pass

    code = st.query_params.get("code")
    if code and not st.query_params.get("reset"):
        try:
            with open(state_path) as handle:
                previous_state = handle.read()
            if st.query_params.get("state") != previous_state:
                raise ValueError("The Calendar login state did not match.")
            flow = google_flow(previous_state)
            if flow is None:
                raise ValueError("Calendar credentials are missing.")
            flow.fetch_token(code=code, timeout=15)
            fd = os.open(token_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as handle:
                handle.write(flow.credentials.to_json())
            os.remove(state_path)
            st.query_params.clear()
            st.rerun()
        except Exception:
            st.error("Google Calendar could not be connected. Try again in Settings.")
            st.query_params.clear()
        return None

    if show_button:
        flow = google_flow()
        if flow is None:
            st.caption("Google Calendar is not configured.")
        else:
            url, state = flow.authorization_url(access_type="offline", prompt="consent")
            fd = os.open(state_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as handle:
                handle.write(state)
            st.link_button("Connect Google Calendar", url, use_container_width=True)
    return None


def calendar_events(creds):
    service = build("calendar", "v3", credentials=creds)
    now = datetime.now(timezone.utc).isoformat()
    result = service.events().list(calendarId="primary", timeMin=now,
                                   maxResults=20, singleEvents=True,
                                   orderBy="startTime").execute()
    return [event for event in result.get("items", []) if event.get("start", {}).get("dateTime")]


def load_water(user_id, today):
    try:
        data = (supabase.table("water_logs")
                .select("log_date,cups,goal_cups")
                .eq("user_id", user_id)
                .order("log_date", desc=True).limit(1).execute()).data or []
        if data:
            goal = max(1, min(20, int(data[0].get("goal_cups") or 12)))
            cups = int(data[0].get("cups") or 0) if str(data[0].get("log_date")) == today else 0
            return max(0, min(goal, cups)), goal, True
        return 0, 12, True
    except Exception:
        return 0, 12, False


def save_water():
    if not st.session_state.water_sync:
        return
    try:
        supabase.table("water_logs").upsert({
            "user_id": st.session_state.user_id,
            "log_date": st.session_state.water_day,
            "cups": st.session_state.water_cups,
            "goal_cups": st.session_state.water_goal,
        }, on_conflict="user_id,log_date").execute()
    except Exception:
        st.session_state.water_sync = False


def save_checkin(data):
    record = dict(data)
    record["user_id"] = st.session_state.user_id
    result = supabase.table("checkins").insert(record).execute()
    return result.data[0]["id"] if result.data else None


def recent_days(history):
    grouped = {}
    for item in history:
        date_str = str(item.get("created_at", ""))[:10]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            score = float(item.get("score"))
        except (ValueError, TypeError):
            continue
        grouped.setdefault(date_str, []).append(max(0, min(100, score)))
    return [(day, round(sum(grouped[day]) / len(grouped[day]))) for day in sorted(grouped)[-7:]]


def show_days(history):
    days = recent_days(history)
    if not days:
        st.caption("Your check-in scores will appear here.")
        return
    st.caption("Average readiness for the last seven dates you checked in.")
    for column, (day, score) in zip(st.columns(len(days)), days):
        with column:
            st.caption(datetime.strptime(day, "%Y-%m-%d").strftime("%a, %b %d"))
            st.write(f"**{score}**")
            st.progress(score)


def history_table(items):
    if not items:
        st.info("No check-ins yet. Do your first fuel check-in to start tracking.")
        return

    rows = []
    for item in items:
        date = str(item.get("created_at") or "")[:10]
        try:
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
        except ValueError:
            pass
        try:
            score = int(round(float(item["score"])))
        except (TypeError, ValueError, KeyError):
            score = None
        rows.append({
            "Date": date,
            "Workout": item.get("workout") or "—",
            "Duration": item.get("duration"),
            "Energy": item.get("energy") or "—",
            "Hydration": item.get("hydration") or "—",
            "Score": score,
            "Feedback": item.get("feedback") or "—",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True,
                 column_config={
                     "Duration": st.column_config.NumberColumn("Duration (min)"),
                     "Score": st.column_config.ProgressColumn("Readiness", min_value=0, max_value=100),
                 })


if "user_id" not in st.session_state:
    st.session_state.user_id = None

reset_id = st.query_params.get("reset")
reset_code = st.query_params.get("code")
if reset_id:
    if not re.fullmatch(r"[a-zA-Z0-9_-]{12,128}", reset_id) or not reset_code:
        st.error("Invalid reset link. Request a new password-reset email.")
        if st.button("Back to log in"):
            st.query_params.clear()
            st.rerun()
        st.stop()
    try:
        response = reset_client(reset_id).auth.exchange_code_for_session({"auth_code": reset_code})
        st.session_state.user_id = response.user.id
        st.session_state.access_token = response.session.access_token
        st.session_state.refresh_token = response.session.refresh_token
        st.session_state.selected_foods = []
        st.session_state.result_score = None
        st.session_state.pop("last_checkin_id", None)
        st.session_state.recovering = True
        try:
            os.remove(f"/tmp/fuel_reset_{reset_id}.json")
        except OSError:
            pass
        st.query_params.clear()
        st.rerun()
    except Exception:
        st.error("This reset link has expired. Please request another one.")
        if st.button("Back to log in"):
            st.query_params.clear()
            st.rerun()
        st.stop()

if st.session_state.get("access_token") and st.session_state.get("refresh_token"):
    try:
        session = supabase.auth.set_session(st.session_state.access_token,
                                            st.session_state.refresh_token)
        st.session_state.user_id = session.user.id
        st.session_state.access_token = session.session.access_token
        st.session_state.refresh_token = session.session.refresh_token
    except Exception:
        st.session_state.user_id = None
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)

if st.session_state.get("recovering") and st.session_state.user_id:
    st.title("Set a new password")
    st.write("Enter your new password below.")
    _, middle, _ = st.columns([1, 1.2, 1])
    with middle, st.container(border=True):
        with st.form("new_password_form"):
            first = st.text_input("New password", type="password")
            second = st.text_input("Confirm password", type="password")
            changed = st.form_submit_button("Update password", type="primary", use_container_width=True)
        if changed:
            if len(first) < 6:
                st.error("Use at least six characters.")
            elif first != second:
                st.error("Passwords don't match.")
            else:
                try:
                    supabase.auth.update_user({"password": first})
                    supabase.auth.sign_out()
                    st.session_state.user_id = None
                    st.session_state.recovering = False
                    st.session_state.password_updated = True
                    st.session_state.pop("access_token", None)
                    st.session_state.pop("refresh_token", None)
                    st.rerun()
                except Exception:
                    st.error("Password update failed. Try the reset link again.")
    st.stop()

if st.session_state.user_id is None:
    st.title("⚡ Fuel Athlete")
    st.write("Plan what to eat before your workout, using foods you already have.")
    _, middle, _ = st.columns([1, 1.1, 1])
    with middle, st.container(border=True):
        if st.session_state.pop("password_updated", False):
            st.success("Password changed. You can log in now.")
        choice = st.radio("Account", ["Log in", "Sign up"], horizontal=True,
                          label_visibility="collapsed")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(
                "Create account" if choice == "Sign up" else "Log in",
                type="primary", use_container_width=True,
            )
        if submit:
            try:
                if choice == "Sign up":
                    result = supabase.auth.sign_up({"email": email, "password": password})
                else:
                    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if result.session:
                    st.session_state.user_id = result.user.id
                    st.session_state.access_token = result.session.access_token
                    st.session_state.refresh_token = result.session.refresh_token
                    st.rerun()
                st.success("Account created. Check your email if confirmation is required.")
            except Exception:
                st.error("Could not sign in. Check your email and password.")

        if choice == "Log in":
            with st.expander("Forgot password?"):
                with st.form("reset_request"):
                    reset_email = st.text_input("Account email")
                    reset_submit = st.form_submit_button("Send reset link")
                if reset_submit:
                    if not reset_email.strip():
                        st.warning("Enter your email.")
                    else:
                        nonce = secrets.token_urlsafe(18)
                        try:
                            reset_client(nonce).auth.reset_password_for_email(
                                reset_email.strip(), {"redirect_to": APP_URL + "?reset=" + nonce}
                            )
                            st.success("If that account exists, a reset link has been sent.")
                        except Exception:
                            st.error("Unable to send a reset email right now.")
    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "Check-in"
if "selected_foods" not in st.session_state:
    st.session_state.selected_foods = []
if "result_score" not in st.session_state:
    st.session_state.result_score = None

today = datetime.now().strftime("%Y-%m-%d")
if st.session_state.get("water_user") != st.session_state.user_id or st.session_state.get("water_day") != today:
    cups, goal, synced = load_water(st.session_state.user_id, today)
    st.session_state.water_cups = cups
    st.session_state.water_goal = goal
    st.session_state.water_sync = synced
    st.session_state.water_day = today
    st.session_state.water_user = st.session_state.user_id

with st.sidebar:
    st.header("⚡ Fuel Athlete")
    st.caption("Workout food and hydration")
    st.divider()
    pages = ["Check-in", "Water", "History", "Insights", "Fuel Guide", "Settings"]
    page = st.radio("Pages", pages, index=pages.index(st.session_state.page), label_visibility="collapsed")
    st.session_state.page = page
    st.divider()
    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.clear()
        st.rerun()

titles = {
    "Check-in": "Your fuel plan", "Water": "Water tracker",
    "History": "Workout history", "Insights": "Your progress",
    "Fuel Guide": "Fuel guide", "Settings": "Settings",
}
st.title(titles[page])
if page == "Check-in":
    st.caption("Check how you feel, add foods you have, and compare options for your workout.")
elif page == "History":
    st.caption("Your previous check-ins and post-workout feedback.")
elif page == "Water":
    st.caption("Log your water one 8 oz cup at a time.")
else:
    st.caption("Fuel Athlete • Food choices for training days")

history = []
if page in ("Check-in", "History", "Insights"):
    try:
        history = (supabase.table("checkins").select("*")
                   .eq("user_id", st.session_state.user_id)
                   .order("created_at", desc=True).execute()).data or []
    except Exception:
        st.warning("Saved check-ins aren't available right now.")

if page == "Check-in":
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("1. Your check-in")
        energy = st.radio("Energy level", ["High", "Medium", "Low"], horizontal=True)
        hours = st.number_input("Hours since you last ate", 0, 8, 4)
        meal = st.selectbox("Last meal", ["Full meal", "Light meal", "Snack"])
        hydration = st.radio("Hydration", ["Well hydrated", "A little thirsty", "Very thirsty"], horizontal=True)
        warning = st.checkbox("I feel dizzy, faint, confused, or sick")

        st.divider()
        st.subheader("2. Your workout")
        workout = st.selectbox("Workout type", [
            "Light / Recovery Workout", "Cardio / Endurance", "Strength Training",
            "Team / Sport Practice", "HIIT / Conditioning", "Game / Competition",
        ])
        calendar_duration = None
        calendar_minutes = None
        creds = calendar_connection()
        if creds:
            if st.button("Load upcoming Calendar events"):
                try:
                    st.session_state.calendar_events = calendar_events(creds)
                except Exception:
                    st.error("Couldn't load Calendar events.")
            events = st.session_state.get("calendar_events", [])
            if events:
                labels = ["Enter manually"]
                for event in events:
                    start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                    labels.append(f"{event.get('summary', 'Event')} — {start.strftime('%b %d, %I:%M %p')}")
                selected = st.selectbox("Calendar event", range(len(labels)), format_func=lambda i: labels[i])
                if selected:
                    event = events[selected - 1]
                    start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                    remaining = int((start - datetime.now(start.tzinfo)).total_seconds() / 60)
                    if 0 <= remaining <= 120:
                        calendar_minutes = remaining
                    if event.get("end", {}).get("dateTime"):
                        end = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                        calendar_duration = max(0, int((end - start).total_seconds() / 60))
        else:
            st.caption("Connect Google Calendar in Settings if you want to use a scheduled workout.")
        if calendar_duration:
            duration = calendar_duration
            st.caption(f"Selected event is {duration} minutes long.")
        else:
            duration = st.number_input("Workout duration (minutes)", 30, 150, 90, step=15)
        if calendar_minutes is not None:
            minutes = calendar_minutes
            st.caption(f"Your event starts in {minutes} minutes.")
        else:
            minutes = st.number_input("Time until workout (minutes)", 0, 120, 60, step=5)

        st.divider()
        st.subheader("3. Foods you have")
        with st.form("search_form"):
            food_query = st.text_input("Search for a food", placeholder="Try banana, yogurt, or oatmeal")
            searching = st.form_submit_button("Search foods", type="primary", use_container_width=True)
        if searching:
            st.session_state.food_query = food_query.strip()
            if len(food_query.strip()) < 2:
                st.warning("Enter at least two characters.")
                st.session_state.food_results = []
            else:
                with st.spinner("Searching..."):
                    st.session_state.food_results = search_foods(food_query.strip())
        found = st.session_state.get("food_results", [])
        if found:
            found.sort(key=lambda item: (bool(item.get("brandOwner")), str(item.get("description", ""))))
            choice = st.selectbox("Choose a food", range(len(found)), format_func=lambda i: (
                found[i].get("description", "Food") +
                (" — " + str(found[i]["brandOwner"]) if found[i].get("brandOwner") else "")
            ))
            if st.button("Add food", use_container_width=True):
                food = found[choice]
                if food.get("source") == "FatSecret":
                    try:
                        food = fatsecret_details(food["fatsecretFoodId"]) or food
                    except (requests.RequestException, ValueError, KeyError):
                        st.warning("Couldn't load nutritional details for this food.")
                if not any(str(f["fdcId"]) == str(food["fdcId"]) for f in st.session_state.selected_foods):
                    st.session_state.selected_foods.append(food)
                    st.rerun()
            if found[0].get("source") == "FatSecret":
                st.caption("Food data: FatSecret Platform API")
        elif st.session_state.get("food_query"):
            st.caption("No matches found. Try a shorter food name.")

        if st.session_state.selected_foods:
            st.write("**Added foods**")
            for food in st.session_state.selected_foods:
                st.write("•", food["description"])
            if st.button("Clear foods"):
                st.session_state.selected_foods = []
                st.rerun()
            st.caption("Nutrition comparisons use 100 g values when available. Check labels for allergens.")
        else:
            st.caption("Add a few foods you have at home to compare them.")

        if st.button("See My Fuel Plan →", type="primary", use_container_width=True):
            if warning:
                st.session_state.result_score = None
                st.session_state.pop("last_checkin_id", None)
                st.error("Don't start your workout yet. Tell a parent, coach, trainer, or nurse how you're feeling.")
            else:
                score = readiness(energy, hours, meal, workout, hydration)
                st.session_state.result_score = score
                st.session_state.result_minutes = minutes
                st.session_state.result_hydration = hydration
                try:
                    st.session_state.last_checkin_id = save_checkin({
                        "workout": workout, "duration": duration,
                        "hours_since_eating": hours, "minutes_until_practice": minutes,
                        "last_food": meal, "energy": energy,
                        "hydration": hydration, "score": score,
                    })
                except Exception:
                    st.session_state.pop("last_checkin_id", None)
                    st.warning("Your result is ready, but it couldn't be saved to History.")

    with right:
        st.subheader("Fuel readiness")
        score = st.session_state.result_score
        if score is None:
            st.caption("Complete the check-in to see your score.")
        else:
            st.metric("Readiness score", f"{score}/100")
            st.progress(score / 100)
            if st.session_state.get("result_hydration") == "Very thirsty":
                st.warning("Drink water and reassess before a strenuous workout.")
            elif score >= 85:
                st.success("Your answers gave you a higher readiness score.")
            elif score >= 70:
                st.info("Consider a snack or some water before your workout.")
            else:
                st.warning("Your answers suggest you may need food or water before exercising.")
            if st.session_state.get("result_hydration") == "A little thirsty":
                st.caption("Drink some water before starting.")
            st.caption("This score comes from simple rules; it isn't a medical assessment.")

        st.divider()
        st.subheader("Food before your workout")
        if score is None:
            st.caption("Add foods and complete the check-in to compare them.")
        else:
            picks = ranked_foods(st.session_state.selected_foods, st.session_state.get("result_minutes", 60))
            if picks:
                st.write("**Best match:**", picks[0][1]["description"])
                carbs, protein, fat = macros(picks[0][1])
                st.caption(f"Per 100 g: {carbs:.1f} g carbs, {protein:.1f} g protein, {fat:.1f} g fat")
                for _, food in picks[1:]:
                    st.write("•", food["description"])
            else:
                st.caption("Add foods with comparable nutrient information for a ranking.")

        st.divider()
        st.subheader("After your workout")
        if score is None:
            st.caption("Recovery options appear after you submit your check-in.")
        else:
            picks = ranked_foods(st.session_state.selected_foods, recovery=True)
            if picks:
                st.caption("Carbohydrate and protein are weighted more heavily for recovery.")
                for _, food in picks:
                    st.write("•", food["description"])
            else:
                st.caption("Add foods to compare recovery options.")
            st.caption("Check food labels if you have allergies or dietary restrictions.")

    st.divider()
    st.subheader("Recent check-ins")
    show_days(history)
    a, b = st.columns(2, gap="large")
    with a:
        st.write("**Post-workout feedback**")
        feedback = st.selectbox("How was your energy during the workout?", ["Choose an answer", "Great", "Okay", "Low"])
        if st.button("Save feedback"):
            last_id = st.session_state.get("last_checkin_id")
            if not last_id:
                st.warning("Complete a check-in first.")
            elif feedback == "Choose an answer":
                st.warning("Choose an option first.")
            else:
                try:
                    (supabase.table("checkins").update({"feedback": feedback})
                     .eq("id", last_id).eq("user_id", st.session_state.user_id).execute())
                    st.success("Feedback saved.")
                except Exception:
                    st.error("Feedback couldn't be saved.")
    with b:
        st.write("**Recent feedback**")
        ratings = [x.get("feedback") for x in history[:10] if x.get("feedback") in ("Great", "Okay", "Low")]
        if len(ratings) < 3:
            st.caption("Add feedback after a few workouts to compare results.")
        else:
            st.write(f"Last ten check-ins: {ratings.count('Great')} Great, "
                     f"{ratings.count('Okay')} Okay, {ratings.count('Low')} Low")

elif page == "Water":
    cups, goal = st.session_state.water_cups, st.session_state.water_goal
    if not st.session_state.water_sync:
        st.info("Water logs are saved only in this session until water_logs is set up in Supabase.")
    st.metric("Today", f"{cups} of {goal} cups")
    st.progress(cups / goal)
    a, b, c = st.columns(3)
    a.metric("Water logged", f"{cups * 8} oz")
    b.metric("Progress", f"{round(cups / goal * 100)}%")
    c.metric("Cups left", goal - cups)

    left, right = st.columns([1.4, .6], gap="large")
    with left:
        st.subheader("Your cups")
        for start in range(0, goal, 4):
            row = st.columns(4)
            for column, number in zip(row, range(start, min(goal, start + 4))):
                with column:
                    st.markdown("### " + ("💧" if number < cups else "◯"))
                    st.caption(f"Cup {number + 1}")
    with right:
        st.subheader("Update your water")
        st.caption("Each cup represents 8 oz.")
        less, more = st.columns(2)
        if less.button("− Drain", disabled=cups == 0, use_container_width=True):
            st.session_state.water_cups -= 1
            save_water()
            st.rerun()
        if more.button("+ Fill", type="primary", disabled=cups >= goal, use_container_width=True):
            st.session_state.water_cups += 1
            save_water()
            st.rerun()
        if st.button("Reset today", disabled=cups == 0, use_container_width=True):
            st.session_state.water_cups = 0
            save_water()
            st.rerun()
        if cups >= goal:
            st.success("You've reached today's target!")

elif page == "History":
    st.subheader("Recent check-in days")
    show_days(history)
    st.subheader("Saved workouts")
    history_table(history)

elif page == "Insights":
    valid_scores = [float(item["score"]) for item in history if item.get("score") is not None]
    a, b, c, d = st.columns(4)
    a.metric("Check-ins", len(history))
    b.metric("Average readiness", round(sum(valid_scores) / len(valid_scores)) if valid_scores else "—")
    c.metric("Highest readiness", round(max(valid_scores)) if valid_scores else "—")
    d.metric("Latest readiness", round(valid_scores[0]) if valid_scores else "—")
    st.subheader("Workout feedback")
    ratings = [x.get("feedback") for x in history]
    a, b, c = st.columns(3)
    a.metric("Great", ratings.count("Great"))
    b.metric("Okay", ratings.count("Okay"))
    c.metric("Low", ratings.count("Low"))
    if sum(ratings.count(v) for v in ("Great", "Okay", "Low")) < 3:
        st.caption("Log feedback after a few workouts to see patterns.")
    st.subheader("Recent readiness")
    show_days(history)

elif page == "Fuel Guide":
    st.subheader("Before a workout")
    st.write("With less time before a workout, the food ranking favors carbohydrates and less fat.")
    st.subheader("More time to digest")
    st.write("With more time available, a mix of carbohydrates and protein may work better.")
    st.subheader("Hydration")
    st.write("If you're very thirsty, drink water and check how you feel before intense activity.")
    st.subheader("After a workout")
    st.write("Recovery foods often contain both carbohydrates and protein.")
    with st.expander("How the readiness score works"):
        st.write("The score starts at 100. It subtracts points for low energy, time since your last meal, "
                 "workout type, and thirst. The food ranking is a separate calculation.")
    st.info("Fuel Athlete offers general guidance, not medical advice. Check labels for allergens.")
    st.caption("Nutrition data: FatSecret Platform API and USDA FoodData Central.")

elif page == "Settings":
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Google Calendar")
        if calendar_connection(show_button=True):
            st.success("Calendar is connected.")
        else:
            st.caption("Connect Calendar to select an upcoming workout during check-in.")
    with right:
        st.subheader("Current plan")
        st.write("Foods added:", len(st.session_state.selected_foods))
        st.write("Fuel score:", st.session_state.result_score if st.session_state.result_score is not None else "Not calculated")
        target = st.number_input("Daily water target (8 oz cups)", 1, 20, value=st.session_state.water_goal)
        if target != st.session_state.water_goal:
            st.session_state.water_goal = target
            st.session_state.water_cups = min(st.session_state.water_cups, target)
            save_water()
            st.rerun()
        if st.button("Clear selected foods", use_container_width=True):
            st.session_state.selected_foods = []
            st.rerun()
        if st.button("Reset fuel plan", use_container_width=True):
            st.session_state.result_score = None
            st.session_state.pop("last_checkin_id", None)
            st.rerun()
    st.caption("Your check-ins are stored under your Supabase account.")
