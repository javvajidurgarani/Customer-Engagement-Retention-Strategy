import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report


# PAGE CONFIG


st.set_page_config(
    page_title="Customer Retention Analytics",
    page_icon="🏦",
    layout="wide"
)


# CUSTOM CSS STYLING


st.markdown("""
<style>

.main {
    background-color: #F8FAFC;
}

h1 {
    color: #0F172A;
    text-align: center;
    font-weight: 700;
}

h2, h3 {
    color: #1E3A8A;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E2E8F0;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

div[data-testid="stSidebar"] {
    background-color: #0F172A;
}

div[data-testid="stSidebar"] * {
    color: white;
}

.stDownloadButton > button {
    background-color: #16A34A;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# LOAD DATA


@st.cache_data
def load_data():
    df = pd.read_csv("European_Bank.csv")
    return df

df = load_data()

# DATA CLEANING


if 'CustomerId' in df.columns:
    df.drop('CustomerId', axis=1, inplace=True)

if 'Surname' in df.columns:
    df.drop('Surname', axis=1, inplace=True)


# DATA VALIDATION


st.markdown("""
<div style="
background: linear-gradient(90deg,#1E3A8A,#2563EB);
padding:25px;
border-radius:15px;
text-align:center;
color:white;
margin-bottom:20px;
">

<h1 style="color:white;">
🏦 Customer Engagement & Product Utilization Analytics
for Retention Strategy
</h1>



</div>
""", unsafe_allow_html=True)




# CUSTOMER SEGMENTATION


conditions = [
    (df['IsActiveMember'] == 1) & (df['NumOfProducts'] >= 2),
    (df['IsActiveMember'] == 0) & (df['NumOfProducts'] == 1),
    (df['IsActiveMember'] == 1) & (df['NumOfProducts'] == 1),
    (df['IsActiveMember'] == 0) & (df['Balance'] > df['Balance'].median())
]

choices = [
    'Loyal Customers',
    'Weak Relationship Customers',
    'Cross-Sell Opportunities',
    'Silent Churners'
]

df['CustomerSegment'] = np.select(
    conditions,
    choices,
    default='Other'
)

# RELATIONSHIP STRENGTH INDEX


df['TenureScore'] = df['Tenure'] / df['Tenure'].max()

df['ProductScore'] = (
    df['NumOfProducts'] /
    df['NumOfProducts'].max()
)

df['ActivityScore'] = df['IsActiveMember']

df['CardScore'] = df['HasCrCard']

df['RelationshipStrengthIndex'] = (
    0.4 * df['ActivityScore'] +
    0.3 * df['ProductScore'] +
    0.2 * df['TenureScore'] +
    0.1 * df['CardScore']
)


# SIDEBAR FILTERS


st.sidebar.title("Dashboard Filters")

country_filter = st.sidebar.multiselect(
    "Select Geography",
    options=df['Geography'].unique(),
    default=df['Geography'].unique()
)

product_filter = st.sidebar.slider(
    "Select Product Range",
    min_value=int(df['NumOfProducts'].min()),
    max_value=int(df['NumOfProducts'].max()),
    value=(1, 4)
)

balance_threshold = st.sidebar.slider(
    "Balance Threshold",
    min_value=0,
    max_value=int(df['Balance'].max()),
    value=50000
)

salary_threshold = st.sidebar.slider(
    "Salary Threshold",
    min_value=0,
    max_value=int(df['EstimatedSalary'].max()),
    value=100000
)


# APPLY FILTERS


filtered_df = df[
    (df['Geography'].isin(country_filter)) &
    (df['NumOfProducts'] >= product_filter[0]) &
    (df['NumOfProducts'] <= product_filter[1])
]


# KPI SECTION


st.header("Key Performance Indicators")

# Engagement Retention Ratio

active_retention = 1 - filtered_df[
    filtered_df['IsActiveMember'] == 1
]['Exited'].mean()

inactive_retention = 1 - filtered_df[
    filtered_df['IsActiveMember'] == 0
]['Exited'].mean()

engagement_ratio = round(
    active_retention / inactive_retention,
    2
)

# Product Depth Index

product_depth_index = round(
    (
        filtered_df['NumOfProducts'].mean() /
        filtered_df['NumOfProducts'].max()
    ) * 100,
    2
)

# High Balance Disengagement Rate

high_balance_customers = filtered_df[
    filtered_df['Balance'] >
    filtered_df['Balance'].quantile(0.75)
]

hbdr = round(
    (
        high_balance_customers[
            high_balance_customers['IsActiveMember'] == 0
        ]['Exited'].mean()
    ) * 100,
    2
)

# Credit Card Stickiness

card_retention = 1 - filtered_df[
    filtered_df['HasCrCard'] == 1
]['Exited'].mean()

non_card_retention = 1 - filtered_df[
    filtered_df['HasCrCard'] == 0
]['Exited'].mean()

ccss = round(
    card_retention / non_card_retention,
    2
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Engagement Retention Ratio",
    engagement_ratio
)

k2.metric(
    "Product Depth Index",
    f"{product_depth_index}%"
)

k3.metric(
    "High Balance Disengagement Rate",
    f"{hbdr}%"
)

k4.metric(
    "Credit Card Stickiness",
    ccss
)

st.markdown("---")


# OVERVIEW METRICS


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Customers",
        len(filtered_df)
    )

with col2:
    churn_rate = round(
        filtered_df['Exited'].mean() * 100,
        2
    )

    st.metric(
        "Churn Rate",
        f"{churn_rate}%"
    )

with col3:
    active_rate = round(
        filtered_df['IsActiveMember'].mean() * 100,
        2
    )

    st.metric(
        "Active Members",
        f"{active_rate}%"
    )

with col4:
    avg_products = round(
        filtered_df['NumOfProducts'].mean(),
        2
    )

    st.metric(
        "Average Products",
        avg_products
    )

with col5:
    avg_balance = round(
        filtered_df['Balance'].mean(),
        2
    )

    st.metric(
        "Average Balance",
        f"₹ {avg_balance:,.0f}"
    )


# ENGAGEMENT VS CHURN


st.header("Engagement vs Churn")

engagement_churn = filtered_df.groupby(
    'IsActiveMember'
)['Exited'].mean().reset_index()

engagement_churn['IsActiveMember'] = (
    engagement_churn['IsActiveMember']
    .map({0: 'Inactive', 1: 'Active'})
)

fig1 = px.bar(
    engagement_churn,
    x='IsActiveMember',
    y='Exited',
    color='IsActiveMember',
    color_discrete_sequence=['#DC2626', '#2563EB'],
    title='Active vs Inactive Customer Churn'
)

st.plotly_chart(fig1, use_container_width=True)


# PRODUCT UTILIZATION ANALYSIS


st.header("Product Utilization Analysis")

product_churn = filtered_df.groupby(
    'NumOfProducts'
)['Exited'].mean().reset_index()

fig2 = px.line(
    product_churn,
    x='NumOfProducts',
    y='Exited',
    markers=True,
    title='Number of Products vs Churn'
)
fig2.update_traces(
    line=dict(color='#2563EB', width=4)
)

st.plotly_chart(fig2, use_container_width=True)


# SINGLE VS MULTI PRODUCT


filtered_df['ProductCategory'] = filtered_df[
    'NumOfProducts'
].apply(
    lambda x: 'Single Product'
    if x == 1 else 'Multi Product'
)

single_multi = filtered_df.groupby(
    'ProductCategory'
)['Exited'].mean().reset_index()

fig_single = px.bar(
    single_multi,
    x='ProductCategory',
    y='Exited',
    color='ProductCategory',
    color_discrete_sequence=['#EA580C','#16A34A'],
    title='Single vs Multi Product Retention'
)

st.plotly_chart(fig_single, use_container_width=True)


# BALANCE VS CHURN


st.header("Balance vs Churn")

fig3 = px.box(
    filtered_df,
    x='Exited',
    y='Balance',
    color='Exited',
    title='Balance Distribution by Churn'
)

st.plotly_chart(fig3, use_container_width=True)


# SALARY VS BALANCE


st.header("Salary vs Balance Analysis")

fig_salary = px.scatter(
    filtered_df,
    x='EstimatedSalary',
    y='Balance',
    color='Exited',
    title='Salary vs Balance Relationship'
)

st.plotly_chart(fig_salary, use_container_width=True)


# GEOGRAPHY ANALYSIS


st.header("Geography Wise Churn")

geo_churn = filtered_df.groupby(
    'Geography'
)['Exited'].mean().reset_index()

fig4 = px.bar(
    geo_churn,
    x='Geography',
    y='Exited',
    color='Geography',
    color_discrete_sequence=[
        '#2563EB',
        '#16A34A',
        '#EA580C'
    ],
    title='Country-wise Churn Rate'
)

st.plotly_chart(fig4, use_container_width=True)


# CUSTOMER SEGMENTATION


st.header("Customer Segmentation")

segment_count = (
    filtered_df['CustomerSegment']
    .value_counts()
    .reset_index()
)

segment_count.columns = ['Segment', 'Count']

fig5 = px.pie(
    segment_count,
    names='Segment',
    values='Count',
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Bold,

    title='Customer Segment Distribution'
)

st.plotly_chart(fig5, use_container_width=True)


# RELATIONSHIP STRENGTH INDEX


st.header("Relationship Strength Index")

fig6 = px.histogram(
    filtered_df,
    x='RelationshipStrengthIndex',
    nbins=20,
    color_discrete_sequence=['#2563EB'],
    title='Relationship Strength Distribution'
)

st.plotly_chart(fig6, use_container_width=True)


# HIGH VALUE DISENGAGED CUSTOMERS


st.header("High Value Disengaged Customers")

premium_risk = filtered_df[
    (filtered_df['Balance'] >= balance_threshold) &
    (filtered_df['EstimatedSalary'] >= salary_threshold) &
    (filtered_df['IsActiveMember'] == 0)
]

st.write(
    f"Total At-Risk Premium Customers: {len(premium_risk)}"
)

st.dataframe(
    premium_risk[[
        'Geography',
        'Gender',
        'Age',
        'Balance',
        'EstimatedSalary',
        'NumOfProducts',
        'Exited'
    ]]
)


# STICKY CUSTOMERS


st.header("Sticky Customers")

sticky_customers = filtered_df[
    (filtered_df['IsActiveMember'] == 1) &
    (filtered_df['NumOfProducts'] >= 2) &
    (filtered_df['Tenure'] >= 5)
]

st.write(
    f"Total Sticky Customers: {len(sticky_customers)}"
)

st.dataframe(
    sticky_customers[[
        'Geography',
        'Gender',
        'Age',
        'Balance',
        'NumOfProducts',
        'Tenure'
    ]]
)


# MACHINE LEARNING SECTION


st.markdown("---")

st.header(" Machine Learning Churn Prediction")

ml_df = df.copy()

le = LabelEncoder()

ml_df['Geography'] = le.fit_transform(
    ml_df['Geography']
)

ml_df['Gender'] = le.fit_transform(
    ml_df['Gender']
)

drop_columns = [
    'CustomerSegment'
]

for col in drop_columns:
    if col in ml_df.columns:
        ml_df.drop(col, axis=1, inplace=True)

X = ml_df.drop('Exited', axis=1)

y = ml_df['Exited']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

m1, m2 = st.columns(2)

with m1:
    st.metric(
        "Model Accuracy",
        f"{accuracy*100:.2f}%"
    )

with m2:
    st.metric(
        "Predicted Churn Rate",
        f"{predictions.mean()*100:.2f}%"
    )

# CONFUSION MATRIX

st.subheader("Confusion Matrix")

cm = confusion_matrix(
    y_test,
    predictions
)

fig, ax = plt.subplots(figsize=(5,4))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    ax=ax
)

ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")

st.pyplot(fig)


# FEATURE IMPORTANCE


st.subheader("Feature Importance")

importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': model.feature_importances_
})

importance_df = importance_df.sort_values(
    by='Importance',
    ascending=False
)

fig_importance = px.bar(
    importance_df,
    x='Importance',
    y='Feature',
    orientation='h',
    color='Importance',
    color_continuous_scale='Blues',
    title='Features Affecting Churn'
)

st.plotly_chart(
    fig_importance,
    use_container_width=True
)


# CLASSIFICATION REPORT


st.subheader("Classification Report")

report = classification_report(
    y_test,
    predictions,
    output_dict=True
)

report_df = pd.DataFrame(report).transpose()

st.dataframe(report_df)


# BUSINESS INSIGHTS


st.header("Business Insights & Recommendations")

st.success(
    "Inactive customers show significantly "
    "higher churn probability."
)

st.info(
    "Customers using multiple products "
    "demonstrate stronger retention."
)

st.warning(
    "High-balance inactive customers "
    "represent silent churn risk."
)

st.success(
    "Active single-product customers are "
    "strong cross-sell opportunities."
)

st.info(
    "Relationship strength indicators "
    "can improve retention strategies."
)




# FOOTER


st.markdown("---")

st.markdown("""
<div style='text-align:center;'>

###  Customer Engagement & Product Utilization Analytics

European Central Bank Internship Project

Built using Streamlit • Plotly • Pandas • Scikit-Learn

</div>
""", unsafe_allow_html=True)