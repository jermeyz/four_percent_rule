import streamlit as st
import pandas as pd
import numpy as np
from vega_datasets import data
import altair as alt

@st.cache_data
def build_data_set(principal,ror,periods,withdrawl_rate,rate_of_inflation):
    init_amount = principal
    steps = periods
    interest_rate = ror
    withdrawl_percent = withdrawl_rate
    df = pd.DataFrame(index=range(steps ), columns=[ 'principal','interest_earned','withdrawl_amount'])
    df.at[0,'principal'] = init_amount
    df.at[0,'interest_earned'] = init_amount * interest_rate
    df.at[0,'withdrawl_amount'] = (df.at[0,'interest_earned'] +  init_amount) * withdrawl_percent
    last_withdrawal_percent = withdrawl_percent
    for period in range(1, steps + 1):
        previous = df.at[period-1,'principal']
        interest = previous  * ( interest_rate)
        df.at[period,'interest_earned'] = interest
        new_balance = interest + previous
        df.at[period,'withdrawl_amount'] =  (new_balance * last_withdrawal_percent)
        last_withdrawal_percent = last_withdrawal_percent * (1 + rate_of_inflation)
        df.at[period,'principal'] = new_balance - (df.at[period,'withdrawl_amount'])

    df.index.name = "index"
    df.reset_index(inplace=True)
    return df

def get_chart(data):
    hover = alt.selection_point(
        fields=["index","principal"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Growth of initial principal over time factoring in withdrawals")
        .mark_line()
        .encode(
            x=alt.X("index",axis=alt.Axis(title="Years")),
            y=alt.Y("principal",axis=alt.Axis(title="Total Amount Remaining")) 
        )
    )
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="index",
            y="principal",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("index", title="Year"),
                alt.Tooltip("principal",format='$,.2f', title="Price (USD)"),
            ],
        )
        .add_params(hover)
    )

    points = lines.transform_filter(hover).mark_circle(size=65)

    return (lines + points +tooltips)#.interactive()


'''
# 4% Withdrawal Rule Calculator

This is a demonstration of the 4% rule.

This rule says you can withdraw no more than 4% per year in retirement for the first year and adjust the withdrawl amount for inflation every year after.  

This should allow your money to last approx 30 years.

**As an example:**

> _Starting amount = $100,000_
>
> _Assuming inflation = 3%_
>
> _Assuming zero rate of return_
>
> ***First year you can withdrawal = (.04 * 100,000) =  $4000***
>
> ***Second year you can withdrawal = ((.04 * 1.03) * 96,000) = $3955.20***
'''

with st.sidebar:
    principal = st.number_input("**Starting amount**",value=1000000,key="principal",step=100)
    percent_increase = st.number_input("**Average percent gain for future**",value=8.0,key="percent_increase",step=1.0)
    years = st.number_input("**Years to live**",value=30,key="years",step=1)
    percent_withdrawl = st.number_input("**Percent Withdrawl**",value=4.0,key="percent_withdrawl",step=1.0)
    inflation_rate =  st.number_input("**Inflation Rate**",value=2.0,key="inflation_rate",step=0.5)



source = build_data_set(principal,percent_increase/100,years,percent_withdrawl/100,inflation_rate/100)

with st.container(border=True):

    st.write(f"**Total interest earned:** ${source['interest_earned'].sum():,.2f}")
    st.write(f"**Total amount withdrawn:** ${source['withdrawl_amount'].sum():,.2f}")

    st.altair_chart(
        (get_chart(source) ),
        use_container_width=True
)
styled_dataset = source.style.format({'principal': '${:,.2f}','interest_earned': '${:,.2f}','withdrawl_amount': '${:,.2f}'})


st.table(styled_dataset)


inflation_data = {
    'Year': [1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'Inflation Rate (%)': [2.70, 2.70, 2.50, 3.30, 1.70, 1.60, 2.70, 3.40, 1.60, 2.40, 1.90, 3.30, 3.40, 2.50, 4.10, 0.10, 2.70, 1.50, 3.00, 1.70, 1.50, 0.80, 0.70, 2.10, 2.10, 1.90, 2.30, 1.40, 7.00, 6.50, 3.40],
    'Interest Rate (%)': [3.00, 5.50, 5.50, 5.25, 5.50, 4.75, 5.50, 6.50, 1.75, 1.25, 1.00, 2.25, 4.25, 5.25, 4.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.50, 0.75, 1.50, 2.50, 1.75, 0.25, 0.25, 4.50, 5.50],
    'Economic Condition': [
        "Expansion (2.7%)", "Expansion (4.0%)", "Expansion (2.7%)", "Expansion (3.8%)", 
        "Expansion (4.4%)", "Expansion (4.5%)", "Expansion (4.8%)", "Expansion (4.1%)", 
        "March peak, November trough (1.0%)", "Expansion (1.7%)", "Expansion (2.8%)", 
        "Expansion (3.8%)", "Expansion (3.5%)", "Expansion (2.8%)", "December peak (2.0%)", 
        "Expansion (0.1%)", "June trough (-2.6%)", "Expansion (2.7%)", "Expansion (1.6%)", 
        "Expansion (2.3%)", "Expansion (2.1%)", "Expansion (2.5%)", "Expansion (2.9%)", 
        "Expansion (1.8%)", "Expansion (2.5%)", "Expansion (3.0%)", "Expansion (2.5%)", 
        "Contraction (-2.2%)", "Expansion (5.8%)", "Expansion (1.9%)", "Expansion (2.5%)"
    ],
    'Notable Events': [
        "Balanced Budget Act", "", "", "Welfare reform", "Fed raised rates", 
        "Long-term capital management crisis", "Glass-Steagall Act repealed", 
        "Tech bubble burst", "Bush tax cut; 9/11 attacks", "War on Terror", 
        "Jobs and Growth Tax Relief Reconciliation Act", "", "Hurricane Katrina; Bankruptcy Act", 
        "", "Bank crisis", "Financial crisis", "American Recovery and Reinvestment Act", 
        "Affordable Care Act; Dodd-Frank Act", "Debt ceiling crisis", "", 
        "Government shutdown, sequestration", "Quantitative easing ends", 
        "Deflation in oil and gas prices", "", "", "", "", 
        "COVID-19 pandemic", "COVID-19 pandemic", "Russia invades Ukraine", 
        "Fed raised rates"
    ]
}

# Creating DataFrame
df = pd.DataFrame(inflation_data)
df


returns = {
    "Year": [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000, 1999, 1998, 1997, 1996, 1995, 1994, 1993],
    "Average Closing Price": [5097.58, 4283.73, 4097.49, 4273.41, 3217.86, 2913.36, 2746.21, 2449.08, 2094.65, 2061.07, 1931.38, 1643.80, 1379.61, 1267.64, 1139.97, 948.05, 1220.04, 1477.18, 1310.46, 1207.23, 1130.65, 965.23, 993.93, 1192.57, 1427.22, 1327.33, 1085.50, 873.43, 670.49, 541.72, 460.42, 451.61],
    "Year Open": [4742.83, 3824.14, 4796.56, 3700.65, 3257.85, 2510.03, 2695.81, 2257.83, 2012.66, 2058.20, 1831.98, 1462.42, 1277.06, 1271.87, 1132.99, 931.80, 1447.16, 1416.60, 1268.80, 1202.08, 1108.48, 909.03, 1154.67, 1283.27, 1455.22, 1228.10, 975.04, 737.01, 620.73, 459.11, 465.44, 435.38],
    "Year High": [5473.23, 4783.35, 4796.56, 4793.06, 3756.07, 3240.02, 2930.75, 2690.16, 2271.72, 2130.82, 2090.57, 1848.36, 1465.77, 1363.61, 1259.78, 1127.78, 1447.16, 1565.15, 1427.09, 1272.74, 1213.55, 1111.92, 1172.51, 1373.73, 1527.46, 1469.25, 1241.81, 983.79, 757.03, 621.69, 482.00, 470.94],
    "Year Low": [4688.68, 3808.10, 3577.03, 3700.65, 2237.40, 2447.89, 2351.10, 2257.83, 1829.08, 1867.61, 1741.89, 1457.15, 1277.06, 1099.23, 1022.58, 676.53, 752.44, 1374.12, 1223.69, 1137.50, 1063.23, 800.73, 776.76, 965.80, 1264.74, 1212.19, 927.69, 737.01, 598.48, 459.11, 438.92, 429.05],
    "Year Close": [5473.23, 4769.83, 3839.50, 4766.18, 3756.07, 3230.78, 2506.85, 2673.61, 2238.83, 2043.94, 2058.90, 1848.36, 1426.19, 1257.60, 1257.64, 1115.10, 903.25, 1468.36, 1418.30, 1248.29, 1211.92, 1111.92, 879.82, 1148.08, 1320.28, 1469.25, 1229.23, 970.43, 740.74, 615.93, 459.27, 466.45],
    "Annual % Change": ["14.75%", "24.23%", "-19.44%", "26.89%", "16.26%", "28.88%", "-6.24%", "19.42%", "9.54%", "-0.73%", "11.39%", "29.60%", "13.41%", "0.00%", "12.78%", "23.45%", "-38.49%", "3.53%", "13.62%", "3.00%", "8.99%", "26.38%", "-23.37%", "-13.04%", "-10.14%", "19.53%", "26.67%", "31.01%", "20.26%", "34.11%", "-1.54%", "7.06%"]
}

# Create DataFrame
df = pd.DataFrame(returns)

#https://www.macrotrends.net/2526/sp-500-historical-annual-returns