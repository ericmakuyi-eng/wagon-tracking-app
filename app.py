import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(
    page_title="Wagon Tracking & Management System",
    page_icon="🚆",
    layout="wide"
)

DATA_FILE = 'Wagon_Tracking_Database.csv'

def init_db():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'Wagon_Number', 
            'Train_Name', 
            'Train_SO', 
            'Exit_Date', 
            'Return_Date', 
            'Round_Trip_Days', 
            'Status', 
            'Last_Updated'
        ])
        # Add sample data from initial upload if available
        sample_data = [
            {'Wagon_Number': 'U101', 'Train_Name': '370128', 'Train_SO': 'U110', 'Exit_Date': '2026-06-05', 'Return_Date': '2026-06-14', 'Round_Trip_Days': 9, 'Status': 'Completed', 'Last_Updated': '2026-10-05 22:28:19'},
            {'Wagon_Number': 'R221', 'Train_Name': '371235', 'Train_SO': 'B231', 'Exit_Date': '2026-06-13', 'Return_Date': '2026-06-22', 'Round_Trip_Days': 9, 'Status': 'Completed', 'Last_Updated': '2026-10-05 22:28:19'},
            {'Wagon_Number': 'U144', 'Train_Name': '366213', 'Train_SO': 'SO-9921', 'Exit_Date': '2026-04-22', 'Return_Date': '2026-05-23', 'Round_Trip_Days': 31, 'Status': 'Completed', 'Last_Updated': '2026-10-05 22:28:19'},
            {'Wagon_Number': 'U162', 'Train_Name': '370027', 'Train_SO': 'SO-4401', 'Exit_Date': '2026-05-31', 'Return_Date': '2026-06-10', 'Round_Trip_Days': 10, 'Status': 'Completed', 'Last_Updated': '2026-10-05 22:28:19'},
        ]
        df = pd.DataFrame(sample_data)
        df.to_csv(DATA_FILE, index=False)

init_db()

@st.cache_data(ttl=1)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def calculate_days(exit_dt, return_dt):
    if exit_dt and return_dt:
        delta = (return_dt - exit_dt).days
        return max(0, delta)
    return None

st.title("🚆 Wagon Tracking & Management Portal")

st.sidebar.title("Navigation")
menu_option = st.sidebar.radio("Go to:", [
    "📝 Wagon Data Entry & Update", 
    "🔍 Single Wagon Search & Report", 
    "📊 Fleet Overview & Export"
])

# --- 1. DATA ENTRY & UPDATE ---
if menu_option == "📝 Wagon Data Entry & Update":
    st.header("📝 Wagon Data Entry / Edit Form")
    st.markdown("Search an existing wagon number to update its details, or enter a new wagon to record a trip.")

    df = load_data()
    existing_wagons = sorted(df['Wagon_Number'].dropna().astype(str).unique().tolist()) if not df.empty else []

    col_search, col_mode = st.columns([2, 1])
    with col_mode:
        entry_mode = st.radio("Mode:", ["Add New Wagon", "Update Existing Wagon"])

    selected_wagon_no = ""
    existing_row = None

    if entry_mode == "Update Existing Wagon":
        with col_search:
            selected_wagon_no = st.selectbox("Select Wagon Number to Update:", options=[""] + existing_wagons)
        if selected_wagon_no and not df.empty:
            matches = df[df['Wagon_Number'].astype(str) == selected_wagon_no]
            if not matches.empty:
                existing_row = matches.iloc[-1]

    default_wagon_no = selected_wagon_no if selected_wagon_no else ""
    default_train_name = str(existing_row['Train_Name']) if existing_row is not None and pd.notna(existing_row['Train_Name']) else ""
    default_train_so = str(existing_row['Train_SO']) if existing_row is not None and pd.notna(existing_row['Train_SO']) else ""

    try:
        default_exit_date = pd.to_datetime(existing_row['Exit_Date']).date() if existing_row is not None and pd.notna(existing_row['Exit_Date']) else datetime.date.today()
    except Exception:
        default_exit_date = datetime.date.today()

    try:
        default_return_date = pd.to_datetime(existing_row['Return_Date']).date() if existing_row is not None and pd.notna(existing_row['Return_Date']) else datetime.date.today()
    except Exception:
        default_return_date = datetime.date.today()

    with st.form("wagon_entry_form", clear_on_submit=False):
        st.subheader("Wagon Trip Details")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            wagon_number = st.text_input("Wagon Number *", value=default_wagon_no)
        with c2:
            train_name = st.text_input("Train Name", value=default_train_name)
        with c3:
            train_so = st.text_input("Train SO (Service Order)", value=default_train_so)

        c4, c5, c6 = st.columns(3)
        with c4:
            exit_date = st.date_input("Exit / Departure Date", value=default_exit_date)
        with c5:
            return_date = st.date_input("Return / Completion Date", value=default_return_date)
        with c6:
            status = st.selectbox("Trip Status", ["In Transit", "Completed", "Maintenance / On Hold"], 
                                  index=1 if (existing_row is not None and existing_row.get('Status') == 'Completed') else 0)

        submit_btn = st.form_submit_button("💾 Save / Update Record")

    if submit_btn:
        if not wagon_number.strip():
            st.error("Please provide a valid Wagon Number.")
        else:
            rt_days = calculate_days(exit_date, return_date) if return_date >= exit_date else None
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_data = {
                'Wagon_Number': wagon_number.strip(),
                'Train_Name': train_name.strip(),
                'Train_SO': train_so.strip(),
                'Exit_Date': str(exit_date),
                'Return_Date': str(return_date) if return_date else "",
                'Round_Trip_Days': rt_days,
                'Status': status,
                'Last_Updated': now_str
            }

            if entry_mode == "Update Existing Wagon" and selected_wagon_no:
                df = df[df['Wagon_Number'].astype(str) != selected_wagon_no]

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.cache_data.clear()
            st.success(f"Successfully saved record for Wagon **{wagon_number}**!")

# --- 2. SINGLE WAGON SEARCH & REPORT ---
elif menu_option == "🔍 Single Wagon Search & Report":
    st.header("🔍 Single Wagon Search & Instant Report")
    st.markdown("Look up any single wagon to analyze its full movement summary and extract a report.")

    df = load_data()
    if df.empty:
        st.info("No records in database. Please add wagons using the Data Entry tab.")
    else:
        search_kw = st.text_input("Enter Wagon Number or Train SO:")
        
        if search_kw:
            filtered_df = df[
                df['Wagon_Number'].astype(str).str.contains(search_kw, case=False, na=False) |
                df['Train_SO'].astype(str).str.contains(search_kw, case=False, na=False)
            ]

            if not filtered_df.empty:
                st.subheader(f"Results for: `{search_kw}`")
                
                top_row = filtered_df.iloc[-1]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Wagon No.", str(top_row['Wagon_Number']))
                m2.metric("Train Name", str(top_row['Train_Name']) if pd.notna(top_row['Train_Name']) else "N/A")
                m3.metric("Train SO", str(top_row['Train_SO']) if pd.notna(top_row['Train_SO']) else "N/A")
                m4.metric("Status", str(top_row['Status']))

                st.markdown("---")
                st.write("### Trip History")
                st.dataframe(filtered_df, use_container_width=True)

                csv_report = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download Report for Wagon {search_kw} (CSV)",
                    data=csv_report,
                    file_name=f"Wagon_{search_kw}_Report.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"No matching records found for '{search_kw}'.")

# --- 3. FLEET OVERVIEW & EXPORT ---
elif menu_option == "📊 Fleet Overview & Export":
    st.header("📊 Complete Fleet Tracking Table")
    df = load_data()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        full_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Full Fleet Report (CSV)",
            data=full_csv,
            file_name="Full_Wagon_Tracking_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("No wagon records available in database yet.")
