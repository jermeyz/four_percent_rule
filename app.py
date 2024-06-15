import streamlit as st
import pandas as pd
import numpy as np
from vega_datasets import data
import altair as alt




# def format_currency(x):
#     return "${:,.2f}".format(x)

st.write("This is a demonstration of the 4% rule.  This rule says you should withdraw no more than 4% per year in retirement for the first year and adjust the withdrawl amount for inflation every year after.  This should allow your money to last approx 30 years.")

principal = st.number_input("Starting amount",value=1000000,key="principal",step=100)
percent_increase = st.number_input("Average percent gain for future",value=8.0,key="percent_increase",step=1.0)
years = st.number_input("Years to live",value=30,key="years",step=1)
# times_per_year = st.number_input("Compounding steps",value=1,key="times_per_year",step=1)
percent_withdrawl = st.number_input("Percent Withdrawl",value=4.0,key="percent_withdrawl",step=1.0)
# st.write("The current number is ", principal)

# # Calculate the total number of compounding periods
# total_periods = times_per_year * years

# # Create a DataFrame to hold the calculations
# df = pd.DataFrame(index=range(total_periods + 1), columns=['Period', 'Principal', 'Interest',"Withdrawl","Amount Left"])
# df2 = pd.DataFrame(index=range(total_periods + 1), columns=[ 'Principal'])
# df['Period'] = df.index
# df.at[0, 'Principal'] = principal
# df.at[0, 'Interest'] = 0

# for period in range(1, total_periods + 1):
#     previous_principal = df.at[period - 1, 'Principal']
#     interest = previous_principal * ((percent_increase/100) / times_per_year)
#     new_principal = previous_principal + interest
    
    
#     df.at[period, 'Interest'] = interest
#     withdrawl_amount = new_principal * (percent_withdrawl / 100)
#     df.at[period, 'Withdrawl'] = withdrawl_amount
#     df.at[period, 'Principal'] =  new_principal - withdrawl_amount
#     df.at[period, 'Amount Left'] =  new_principal - withdrawl_amount
#     df2.at[period,"Principal"] = new_principal

# df



# #df.drop(columns="Period")
# #df['Principal'] = df['Principal'].apply(format_currency)
# st.area_chart(df2)




# We use @st.cache_data to keep the dataset in cache
@st.cache_data
def build_data_set(principal,ror,periods,withdrawl_rate):
    # source = data.stocks()
    # source = source[source.date.gt("2004-01-01")]
    init_amount = principal
    steps = periods
    interest_rate = ror
    withdrawl_percent = withdrawl_rate
    df = pd.DataFrame(index=range(steps ), columns=[ 'principal','interest_earned','withdrawl_amount'])
    df.at[0,'principal'] = init_amount
    for period in range(1, steps + 1):
        #interest = previous_principal * ((percent_increase/100) / times_per_year)
        previous = df.at[period-1,'principal']
        interest = previous  * ( interest_rate)
        df.at[period,'interest_earned'] = interest
        new_balance = interest + previous
        df.at[period,'withdrawl_amount'] =  (new_balance * withdrawl_percent)
        df.at[period,'principal'] = new_balance - (df.at[period,'withdrawl_amount'])

    sdf = df.style.format({'principal': '${:,.2f}','interest_earned': '${:,.2f}','withdrawl_amount': '${:,.2f}'})
    #sdf
    df.index.name = "index"
    df.reset_index(inplace=True)
    return df

source = build_data_set(principal,percent_increase/100,years,percent_withdrawl/100)

def get_chart2(data):
    hover = alt.selection_single(
        fields=["index","principal"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="4% Rule")
        .mark_line()
        .encode(
            x="index",
            y="principal" 
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
                alt.Tooltip("index", title="Date"),
                alt.Tooltip("principal",format='$,.2f', title="Price (USD)"),
            ],
        )
        .add_selection(hover)
    )

    points = lines.transform_filter(hover).mark_circle(size=65)

    return (lines + points +tooltips)#.interactive()


chart = get_chart2(source)

st.altair_chart(
    (chart ),
    use_container_width=True
)
styled_dataset = source.style.format({'principal': '${:,.2f}','interest_earned': '${:,.2f}','withdrawl_amount': '${:,.2f}'})


st.write(f"Total interest earned: ${source['interest_earned'].sum():,.2f}")
st.write(f"Total amount withdrawn: ${source['withdrawl_amount'].sum():,.2f}")

styled_dataset