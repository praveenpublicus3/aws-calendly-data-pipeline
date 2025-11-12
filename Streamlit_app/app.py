import streamlit as st
import pandas as pd
import psycopg2
import altair as alt
from psycopg2 import sql

# -------------------------------
# 🔗 Function to connect to Redshift
# -------------------------------
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="dev",
            user="admin",
            password="DEAcademy12",
            host="calendly-workgroup.647132523501.us-east-1.redshift-serverless.amazonaws.com",
            port="5439"
        )
        return conn
    except Exception as e:
        st.error(f"⚠️ Unable to connect to Redshift.\n\nError: {e}")
        return None

# -------------------------------
# 🎨 Streamlit UI Setup
# -------------------------------
st.set_page_config(page_title="Calendly Marketing & Campaign Insights", layout="wide")
st.title("📊 Calendly Marketing & Campaign Insights")
st.caption("End-to-End AWS Pipeline: S3 → Glue → Redshift → Streamlit")

# -------------------------------
# ✅ Test Connection (small check)
# -------------------------------
conn = get_connection()
if conn:
    st.success("✅ Connected to Amazon Redshift!")
    conn.close()
else:
    st.stop()

# -------------------------------
# 🧮 KPI Section (Top Summary)
# -------------------------------
conn = get_connection()
if conn:
    try:
        total_calls_df = pd.read_sql("SELECT COALESCE(SUM(total_bookings),0) AS total_bookings FROM vw_daily_calls", conn)
        total_calls = int(total_calls_df.iloc[0, 0]) if not total_calls_df.empty else 0

        total_spend_df = pd.read_sql("SELECT COALESCE(SUM(total_spend),0) AS spend FROM vw_cost_per_booking", conn)
        total_spend = float(total_spend_df.iloc[0, 0]) if not total_spend_df.empty else 0.0

        avg_cpb_df = pd.read_sql("SELECT COALESCE(AVG(cost_per_booking),0) AS avg_cpb FROM vw_cost_per_booking", conn)
        avg_cpb = float(avg_cpb_df.iloc[0, 0]) if not avg_cpb_df.empty else 0.0

        col1, col2, col3 = st.columns(3)
        col1.metric("📞 Total Bookings", f"{total_calls:,}")
        col2.metric("💵 Total Spend (USD)", f"${total_spend:,.2f}")
        col3.metric("⚖️ Avg Cost/Booking", f"${avg_cpb:,.2f}")
    except Exception as e:
        st.warning(f"⚠️ Unable to fetch KPI metrics: {e}")
    finally:
        conn.close()

# -------------------------------
# 🧭 Tabs (6 Business Metrics)
# -------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Daily Calls by Source",
    "💰 Cost Per Booking",
    "🏆 Channel Summary",
    "📈 Bookings Trend Over Time",
    "🕒 Booking Volume by Time Slot / Day",
    "👥 Meeting Load per Employee"
])

# ----------------------------------------------------------
# 📅 TAB 1: Daily Calls by Source
# ----------------------------------------------------------
with tab1:
    st.subheader("📅 Daily Calls by Source")
    st.caption("Shows how many bookings were made per source per day.")

    conn = get_connection()
    if conn:
        try:
            daily = pd.read_sql("SELECT * FROM vw_daily_calls ORDER BY booking_date", conn)
            if daily.empty:
                st.info("No daily calls data available yet.")
            else:
                st.dataframe(daily, use_container_width=True)

                # ensure date parsing
                if "booking_date" in daily.columns:
                    daily["booking_date"] = pd.to_datetime(daily["booking_date"])

                # Altair multi-line chart (one line per source)
                if {"booking_date", "source", "total_bookings"}.issubset(daily.columns):
                    chart = (
                        alt.Chart(daily)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X("booking_date:T", title="Booking Date"),
                            y=alt.Y("total_bookings:Q", title="Total Bookings"),
                            color=alt.Color("source:N", title="Source"),
                            tooltip=["booking_date", "source", "total_bookings"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("vw_daily_calls does not contain the expected columns.")
        except Exception as e:
            st.error(f"Error fetching Daily Calls data: {e}")
        finally:
            conn.close()

# ----------------------------------------------------------
# 💰 TAB 2: Cost Per Booking
# ----------------------------------------------------------
with tab2:
    st.subheader("💰 Cost Per Booking (CPB) by Channel")
    st.caption("Analyzes cost efficiency across campaigns.")

    conn = get_connection()
    if conn:
        try:
            cpb = pd.read_sql("SELECT * FROM vw_cost_per_booking", conn)
            if cpb.empty:
                st.info("No CPB data available yet.")
            else:
                st.dataframe(cpb, use_container_width=True)
                # Make sure columns exist
                if {"event_type", "cost_per_booking", "total_spend", "total_bookings"}.issubset(cpb.columns):
                    chart = (
                        alt.Chart(cpb)
                        .mark_bar()
                        .encode(
                            x=alt.X("event_type:N", title="Channel"),
                            y=alt.Y("cost_per_booking:Q", title="Cost Per Booking (USD)"),
                            color=alt.Color("event_type:N", legend=None),
                            tooltip=["event_type", "total_spend", "total_bookings", "cost_per_booking"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("vw_cost_per_booking missing expected columns.")
        except Exception as e:
            st.error(f"Error fetching CPB data: {e}")
        finally:
            conn.close()

# ----------------------------------------------------------
# 🏆 TAB 3: Channel Summary
# ----------------------------------------------------------
with tab3:
    st.subheader("🏆 Channel Summary")
    st.caption("Summarizes performance across all channels.")

    conn = get_connection()
    if conn:
        try:
            # Use the cost-per-booking view for summary if it contains totals
            summary = pd.read_sql("SELECT * FROM vw_cost_per_booking", conn)
            if summary.empty:
                st.info("No channel summary data available yet.")
            else:
                st.dataframe(summary, use_container_width=True)

                if {"event_type", "total_bookings", "total_spend"}.issubset(summary.columns):
                    chart = (
                        alt.Chart(summary)
                        .mark_bar()
                        .encode(
                            x=alt.X("event_type:N", title="Channel"),
                            y=alt.Y("total_bookings:Q", title="Total Bookings"),
                            color=alt.Color("event_type:N", legend=None),
                            tooltip=["event_type", "total_bookings", "total_spend", "cost_per_booking"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("vw_cost_per_booking does not contain expected fields for summary.")
        except Exception as e:
            st.error(f"Error fetching Channel Summary data: {e}")
        finally:
            conn.close()

# ----------------------------------------------------------
# 📈 TAB 4: Bookings Trend Over Time
# ----------------------------------------------------------
with tab4:
    st.subheader("📈 Bookings Trend Over Time")
    st.caption("Tracks booking volume across dates and sources.")

    conn = get_connection()
    if conn:
        try:
            trend = pd.read_sql("SELECT * FROM vw_bookings_trend ORDER BY booking_date", conn)
            if trend.empty:
                st.info("No bookings trend data available yet.")
            else:
                st.dataframe(trend, use_container_width=True)

                # parse date
                if "booking_date" in trend.columns:
                    trend["booking_date"] = pd.to_datetime(trend["booking_date"])

                if {"booking_date", "source", "total_bookings"}.issubset(trend.columns):
                    chart = (
                        alt.Chart(trend)
                        .mark_area(opacity=0.4)
                        .encode(
                            x=alt.X("booking_date:T", title="Date"),
                            y=alt.Y("total_bookings:Q", title="Bookings"),
                            color=alt.Color("source:N", title="Source"),
                            tooltip=["booking_date", "source", "total_bookings"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("vw_bookings_trend missing expected columns.")
        except Exception as e:
            st.error(f"Error fetching Bookings Trend data: {e}")
        finally:
            conn.close()

# ----------------------------------------------------------
# 🕒 TAB 5: Booking Volume by Time Slot / Day
# ----------------------------------------------------------
with tab5:
    st.subheader("🕒 Booking Volume by Time Slot / Day of Week")
    st.caption("Visualizes when bookings happen most frequently.")

    conn = get_connection()
    if conn:
        try:
            volume = pd.read_sql("SELECT * FROM vw_booking_volume_time", conn)
            if volume.empty:
                st.info("No booking volume time data available yet.")
            else:
                st.dataframe(volume, use_container_width=True)

                # Expecting: day_of_week, hour_of_day, total_bookings
                if {"day_of_week", "hour_of_day", "total_bookings"}.issubset(volume.columns):
                    # Clean day_of_week strings and set ordering
                    volume["day_of_week"] = volume["day_of_week"].str.strip()
                    # Define weekday order (adjust locale if necessary)
                    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    # If day_of_week values are different, we will still plot but try to use provided order
                    volume["day_of_week"] = pd.Categorical(volume["day_of_week"], categories=weekday_order, ordered=True)

                    # Ensure hour_of_day numeric
                    volume["hour_of_day"] = pd.to_numeric(volume["hour_of_day"], errors="coerce").fillna(0).astype(int)

                    heatmap = (
                        alt.Chart(volume)
                        .mark_rect()
                        .encode(
                            x=alt.X("hour_of_day:O", title="Hour of Day"),
                            y=alt.Y("day_of_week:N", title="Day of Week", sort=weekday_order),
                            color=alt.Color("total_bookings:Q", title="Bookings"),
                            tooltip=["day_of_week", "hour_of_day", "total_bookings"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(heatmap, use_container_width=True)
                else:
                    st.warning("vw_booking_volume_time does not have the expected columns (day_of_week, hour_of_day, total_bookings).")
        except Exception as e:
            st.error(f"Error fetching Booking Volume data: {e}")
        finally:
            conn.close()

# ----------------------------------------------------------
# 👥 TAB 6: Meeting Load per Employee
# ----------------------------------------------------------
with tab6:
    st.subheader("👥 Meeting Load per Employee")
    st.caption("Displays employee-level meeting load over time.")

    conn = get_connection()
    if conn:
        try:
            meeting = pd.read_sql("SELECT * FROM vw_meeting_load", conn)
            if meeting.empty:
                st.info("No meeting load data available yet.")
            else:
                st.dataframe(meeting, use_container_width=True)

                if {"employee_id", "avg_meetings_per_week"}.issubset(meeting.columns):
                    chart = (
                        alt.Chart(meeting)
                        .mark_bar()
                        .encode(
                            x=alt.X("employee_id:N", title="Employee ID"),
                            y=alt.Y("avg_meetings_per_week:Q", title="Avg Meetings / Week"),
                            color=alt.Color("employee_id:N", legend=None),
                            tooltip=["employee_id", "total_meetings", "avg_meetings_per_week"]
                        )
                        .properties(height=420)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("vw_meeting_load missing required columns.")
        except Exception as e:
            st.error(f"Error fetching Meeting Load data: {e}")
        finally:
            conn.close()
