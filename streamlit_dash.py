import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os
import warnings
import requests
import datetime
from io import BytesIO
warnings.filterwarnings("ignore")

st.set_page_config(page_title='ETF Dinner Date', page_icon=':chart_with_upwards_trend:', layout='wide')
st.title(':chart_with_upwards_trend: ETF Dinner Competition :chart_with_upwards_trend: :hamburger: :wine_glass: :cocktail:')
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

os.chdir(r'C:\Users\choue\etf_proj')
df = pd.read_csv('etf_hist.csv', encoding = 'ISO-8859-1')

col1, col2, col3 = st.columns((3))
df['startdate'] = [pd.to_datetime(str(t), format='%Y%m%d') for t in df['startdate']]

#get the min and max dates from the startdate column
min_date = pd.to_datetime(df['startdate'].min()).date()
max_date = datetime.date.today()

with col1:
    date1 = st.date_input('Rebase Start Date', min_date, min_value=min_date, max_value=max_date)
with col2:
    date2 = st.date_input('End Date', max_date, min_value=min_date, max_value=max_date)

# df = df[(df['startdate'] >= date1) & (df['startdate'] <= date2)]




########################################################################################################


start_date = date1.strftime('%Y-%m-%d')
end_date = date2.strftime('%Y-%m-%d')

etfnms = pd.read_csv(r'C:\Users\choue\etf_proj\etf_hist.csv')
etfnms['startdate'] = [pd.to_datetime(str(t), format='%Y%m%d') for t in etfnms['startdate']]


ndict = {}
for chg in etfnms.columns[1:]:
   print((etfnms[chg].values[1:] != etfnms[chg].values[:-1]))
   cc = (etfnms[chg].values[1:] != etfnms[chg].values[:-1]).sum().item()
   ndict[chg] = cc
rebals_df = pd.DataFrame.from_dict(ndict, orient='index', columns=['Rebals'])
rebals_df['Contribution'] = rebals_df['Rebals'].apply(lambda x: 100 * x)
total_fund = rebals_df['Contribution'].sum()

#create a data frame for each person showing what rebalances they have done


st.sidebar.header('Rebalance Summary: ')
rebals = (st.sidebar.table(rebals_df))
st.sidebar.markdown('#')
st.sidebar.markdown(f'Total Rebal Drink Fund: **${total_fund:.0f}**' )

unique_values = set()
for col in etfnms.columns[1:]:
    unique_values.update(etfnms[col].unique())
unique_values = list(unique_values)


#px data
all_prices = []
for etf in unique_values:
    r = requests.get(f'https://stooq.com/q/d/l/?s={etf.lower()}.us&i=d')
    prices = pd.read_csv(BytesIO(r.content))
    prices = prices.set_index('Date')['Close'].rename(etf)
    all_prices.append(prices)
pxs = pd.concat(all_prices, axis=1).sort_index()
pxs = pxs.loc[start_date:]

#convert px data to returns
rets = pxs.copy()
for col in rets.columns:
    rets[col] = rets[col].pct_change()
rets = rets.fillna(0).reset_index()
rets['Date'] = pd.to_datetime(rets.Date)
rets = rets.set_index('Date')
rets_dict = {col: rets[col].to_dict() for col in rets.columns}









cumrets = pd.DataFrame(rets.reset_index()['Date'])
cumrets = pd.merge_asof(cumrets, etfnms, left_on='Date', right_on='startdate', direction='backward').drop(columns=['startdate'])

#fill df3 with the values from df2 based on the values/date combo in df3
for col in cumrets.columns[1:]:
    cumrets[col] = cumrets.apply(lambda row: rets_dict.get(row[col], {}).get(row['Date']), axis=1)

#convert to cumulative returns
for col in cumrets.columns[1:]:
    cumrets[col] = (1 + cumrets[col]).cumprod() - 1
cumrets = cumrets.set_index('Date')

cumrets = cumrets.loc[date1:date2] # filter the dataframe based on the start date

######################################################################################################



# fl = st.file_uploader(':file_folder: Upload your rebalance file', type=['csv', 'xlsx'], label_visibility='collapsed')
# if fl is not None:
#     filename = fl.name
#     st.write(filename)
#     df = pd.read_csv(filename, encoding='ISO-8859-1')
# else:

# if not performance:
#     disp_rets = cumrets.copy()
# else:
#     disp_rets = cumrets[performance]




fig = px.line(cumrets, template='plotly_white')
fig.layout.yaxis.tickformat = ',.1%'
fig.layout.xaxis.tickformat = '%Y-%m-%d'
fig.update_yaxes(title_text='Percent Change', title_font=dict(size=20))
fig.update_xaxes(title_text='Date', title_font=dict(size=20))
fig.update_layout(title_text='Contest Performance', title_x=0.5, title_font=dict(size=24))
fig.update_layout(width=1500, height=1000)
st.markdown('#', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False)

st.markdown('#', unsafe_allow_html=True)
st.subheader('ETF Position History:')
etfnms['startdate'] = [i.date() for i in etfnms['startdate']]
etfnms = etfnms.set_index('startdate')
st.table(etfnms)
