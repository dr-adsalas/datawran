import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

url = "https://github.com/cbrown-clu/class_data/raw/refs/heads/main/data/DS_job_roles_UK.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

if "Salary" in df.columns:
    df.rename(columns={"Salary": "Salary Estimate"}, inplace=True)

def extract_min_salary(salary):
    try:
        salary = str(salary).replace("£", "").replace(",", "").lower()
        if "-" in salary:
            return int(salary.split("-")[0].strip().replace("k", "000"))
        elif "per hour" in salary:
            hourly = float(salary.split()[0])
            return int(hourly * 40 * 52)
        elif "k" in salary:
            return int(salary.replace("k", "")) * 1000
        elif salary.isdigit():
            return int(salary)
        else:
            return None
    except:
        return None

df["Min Salary (£)"] = df["Salary Estimate"].apply(extract_min_salary)

# interactive things

# Location filter
locations = sorted(df["Location"].dropna().unique())
selected_location = st.selectbox("Select a location:", locations)

# Job title keyword search
search_term = st.text_input("Search job title:")

# Filter the data
filtered_df = df[
    (df["Location"] == selected_location) &
    (df["Job Title"].str.contains(search_term, case=False, na=False))
]

# Drop rows without salary for plotting
plot_df = filtered_df.dropna(subset=["Min Salary (£)"])

# plots
if not plot_df.empty:
    fig, ax = plt.subplots()
    ax.hist(plot_df["Min Salary (£)"], bins=10)
    ax.set_title(f"Salary Distribution in {selected_location}")
    ax.set_xlabel("Estimated Min Salary (£)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)
else:
    st.warning("No salary data available for this filter.")

# table
st.subheader("Filtered Job Listings")
st.dataframe(filtered_df)

st.subheader("Explore Skills Demand by Location")

# Split  skills into flat list
all_skills = df["Skills"].dropna().str.split(",").explode().str.strip().str.title()
unique_skills = sorted(all_skills.dropna().unique())

selected_skill = st.selectbox("Select a skill:", unique_skills)

skill_filtered_df = df[df["Skills"].str.contains(selected_skill, case=False, na=False)]

if not skill_filtered_df.empty:
    skill_loc_counts = skill_filtered_df["Location"].value_counts().reset_index()
    skill_loc_counts.columns = ["Location", "Job Count"]

    st.write(f"**Locations hiring for: {selected_skill}**")
    st.dataframe(skill_loc_counts)

    # bar chart
    fig3, ax3 = plt.subplots()
    ax3.bar(skill_loc_counts["Location"], skill_loc_counts["Job Count"])
    ax3.set_xticklabels(skill_loc_counts["Location"], rotation=45, ha="right")
    ax3.set_ylabel("Number of Jobs")
    ax3.set_title(f"Demand for '{selected_skill}' by Location")
    st.pyplot(fig3)

    #show jobs that match
    st.write(f"**Jobs that require {selected_skill}:**")
    st.dataframe(skill_filtered_df[["Company", "Job Title", "Location", "Salary Estimate"]])
else:
    st.warning(f"No job listings found for: {selected_skill}")