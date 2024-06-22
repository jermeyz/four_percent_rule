import streamlit as st
import pandas as pd
import numpy as np
from vega_datasets import data
import altair as alt

@st.cache_data
def build_data_set(principal, future_percent_return, periods, withdrawal_rate, rate_of_inflation):
    _init_amount = principal
    _periods = periods
    _future_percent_return = future_percent_return
    _withdrawal_rate = withdrawal_rate
    df = pd.DataFrame(index=range(_periods), columns=['principal', 'interest_earned', 'withdrawal_amount'])
    df.at[0, 'principal'] = _init_amount
    df.at[0, 'interest_earned'] = _init_amount * _future_percent_return
    df.at[0, 'withdrawal_amount'] = (df.at[0, 'interest_earned'] + _init_amount) * _withdrawal_rate
    last_withdrawal_percent = _withdrawal_rate
    for period in range(1, _periods + 1):
        previous = df.at[period - 1, 'principal']
        interest = previous * _future_percent_return
        df.at[period, 'interest_earned'] = interest
        new_balance = interest + previous
        df.at[period, 'withdrawal_amount'] = new_balance * last_withdrawal_percent
        last_withdrawal_percent = last_withdrawal_percent * (1 + rate_of_inflation)
        df.at[period, 'principal'] = new_balance - df.at[period, 'withdrawal_amount']

    df.index.name = "index"
    df.reset_index(inplace=True)
    return df

def build_data_set_actual_data(principal, withdrawal_rate, real_data):
    _principal = principal
    steps = 30
    _withdrawal_rate = withdrawal_rate
    df = pd.DataFrame(index=range(steps), columns=['principal', 'interest_earned', 'withdrawal_amount', 'yearly_returns', 'inflation_rate'])
    df.at[0, 'principal'] = _principal
    df.at[0, 'interest_earned'] = _principal * (real_data.at[0, "sp_returns"] / 100)
    df.at[0, 'withdrawal_amount'] = (df.at[0, 'interest_earned'] + _principal) * _withdrawal_rate
    df.at[0, "yearly_returns"] = real_data.at[0, "sp_returns"]
    df.at[0, "inflation_rate"] = real_data.at[0, "inflation_rate"]
    last_withdrawal_percent = _withdrawal_rate
    for period in range(1, steps):
        previous = df.at[period - 1, 'principal']
        interest = previous * (real_data.at[period, "sp_returns"] / 100)
        df.at[period, 'interest_earned'] = interest
        df.at[period, "yearly_returns"] = real_data.at[period, "sp_returns"]
        df.at[period, "inflation_rate"] = real_data.at[period, "inflation_rate"]
        new_balance = interest + previous
        df.at[period, 'withdrawal_amount'] = new_balance * last_withdrawal_percent
        last_withdrawal_percent = last_withdrawal_percent * (1 + (real_data.at[period, "inflation_rate"] / 100))
        df.at[period, 'principal'] = new_balance - df.at[period, 'withdrawal_amount']

    df.index.name = "index"
    df.reset_index(inplace=True)
    return df

def get_chart(data):
    hover = alt.selection_point(
        fields=["index", "principal"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Growth of initial principal over time factoring in withdrawals")
        .mark_line()
        .encode(
            x=alt.X("index", axis=alt.Axis(title="Years")),
            y=alt.Y("principal", axis=alt.Axis(title="Total Amount Remaining"))
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
                alt.Tooltip("principal", format='$,.2f', title="Total Amount Remaining"),
            ],
        )
        .add_params(hover)
    )

    points = lines.transform_filter(hover).mark_circle(size=65)

    return lines + points + tooltips  # .interactive()

'''
# 4% Withdrawal Rule Calculator

This is a demonstration of the 4% rule.

This rule says you can withdraw no more than 4% per year in retirement for the first year and adjust the withdrawal amount for inflation every year after.  

This should allow your money to last approximately 30 years.

**As an example:**

> _Starting amount = $100,000_
>
> _Assuming inflation = 3%_
>
> _Assuming zero rate of return_
>
> ***First year you can withdraw = (.04 * 100,000) =  $4000***
>
> ***Second year you can withdraw = ((.04 * 1.03) * 96,000) = $3955.20***
'''

with st.sidebar:
    principal = st.number_input("**Starting amount**", value=1000000, key="principal", step=100)
    percent_increase = st.number_input("**Average percent gain for future**", value=9.58, key="percent_increase", step=1.0)
    years = st.number_input("**Years to live**", value=30, key="years", step=1)
    percent_withdrawal = st.number_input("**Percent Withdrawal**", value=4.0, key="percent_withdrawal", step=1.0)
    inflation_rate = st.number_input("**Inflation Rate**", value=2.53, key="inflation_rate", step=0.5)

source = build_data_set(principal, percent_increase / 100, years, percent_withdrawal / 100, inflation_rate / 100)
real_returns = {
    "Year": ["1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"],
    "sp_returns": [7.06, -1.54, 34.11, 20.26, 31.01, 26.67, 19.53, -10.14, -13.04, -23.37, 26.38, 8.99, 3.00, 13.62, 3.53, -38.49, 23.45, 12.78, 0.00, 13.41, 29.60, 11.39, -0.73, 9.54, 19.42, -6.24, 28.88, 16.26, 26.89, -19.44, 24.23],
    "inflation_rate": [2.70, 2.70, 2.50, 3.30, 1.70, 1.60, 2.70, 3.40, 1.60, 2.40, 1.90, 3.30, 3.40, 2.50, 4.10, 0.10, 2.70, 1.50, 3.00, 1.70, 1.50, 0.80, 0.70, 2.10, 2.10, 1.90, 2.30, 1.40, 7.00, 6.50, 3.40]
}
rdf = pd.DataFrame(real_returns)

avg_returns = rdf['sp_returns'].mean()
avg_inflation = rdf['inflation_rate'].mean()

with st.container(border=True):
    st.write(f"**Total interest earned:** ${source['interest_earned'].sum():,.2f}")
    st.write(f"**Total amount withdrawn:** ${source['withdrawal_amount'].sum():,.2f}")
    st.altair_chart(
        get_chart(source),
        use_container_width=True
    )
    renamed_source = source.rename(columns={
    'principal': 'Principal Amount',
    'interest_earned': 'Interest Earned',
    'withdrawal_amount': 'Withdrawal Amount'
    }).drop(columns=['index'])
    styled_dataset = renamed_source.style.format({'Principal Amount': '${:,.2f}', 'Interest Earned': '${:,.2f}', 'Withdrawal Amount': '${:,.2f}'})

    with st.expander("See dataset"):
        st.table(styled_dataset)



real_data = build_data_set_actual_data(principal, percent_withdrawal / 100, rdf)
real_data_renamed = real_data.rename(columns={
    'principal': 'Principal Amount',
    'interest_earned': 'Interest Earned',
    'withdrawal_amount': 'Withdrawal Amount',
    'yearly_returns': 'Yearly Return for S&P',
    'inflation_rate': 'Yearly Inflation Rate',
}).drop(columns=['index'])
styled_dataset = real_data_renamed.style.format({'Principal Amount': '${:,.2f}', 'Interest Earned': '${:,.2f}', 'Withdrawal Amount': '${:,.2f}', 'Yearly Return for S&P': '{:,.2f}%', 'Yearly Inflation Rate': '{:,.2f}%'})

with st.container(border=True):
    st.write(f"**Total interest earned against real data:** ${real_data['interest_earned'].sum():,.2f}")
    st.write(f"**Total amount withdrawn  against real data:** ${real_data['withdrawal_amount'].sum():,.2f}")
    st.write(f"**Average Returns:** {avg_returns/100:,.2%}")
    st.write(f"**Average Inflation:** {avg_inflation/100:,.2%}")
    st.altair_chart(
        get_chart(real_data),
        use_container_width=True
    )
    with st.expander("See dataset"):
        st.table(styled_dataset)