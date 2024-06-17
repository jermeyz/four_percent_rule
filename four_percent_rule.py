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