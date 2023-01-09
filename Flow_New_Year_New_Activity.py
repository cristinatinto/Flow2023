#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")


# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[4]:


st.title('Flow New Year New Activity')
st.write('')
st.markdown('The holidays and New Year are often chaotic in the crypto and DEFI space, as users make a spree of new transactions and wallets as they receive (and give) some cash and coins as holiday gifts.')
st.markdown(' The idea of this work is to try to respond if this flurry of winter activity has impacted the Flow ecosystem, if users are creating new wallets or buying tokens with their newfound holiday wealth.')
st.write('This dashboard comprehens the following sections:')
st.markdown('1. Flow main activity comparison before and after holidays')
st.markdown('2. Flow supply before and after holidays')
st.markdown('3. Flow development before and after holidays')
st.markdown('4. Flow staking activity before and after holidays')
st.write('')
st.subheader('1. Flow main activity')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the activity of Flow ecosystem during this past month. More specifically, we will analyze the following data:')
st.markdown('● Total number transactions')
st.markdown('● Total active users')
st.markdown('● Total volume moved')
st.write('')

sql="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct payer) as n_wallets,
  sum(gas_limit) as fee_luna
from flow.core.fact_transactions
  where block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(payer) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  payer
from flow.core.fact_transactions
group by payer
)
  where date >= '2022-12-08' and date <= '2023-01-08'
group by date
)

select 
  t.*,
    case when t.date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""

st.experimental_memo(ttl=50000)
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
    


with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily transactions evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Transactions comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active wallets evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active wallets comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily fees evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Fees comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new users evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New users comparison',width=300))
    
    


# In[6]:


st.subheader("2. Supply before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the FLOW supply. More specifically, we will analyze the following data:')
st.markdown('● $FLOW supply')
st.markdown('● Circulating supply')



sql="""
with SEND as 
(select SENDER,
  sum(AMOUNT) as sent_amount
from 
flow.core.ez_token_transfers
WHERE
token_contract ilike 'A.1654653399040a61.FlowToken'
group by SENDER
  ),
  
RECEIVE as 
(select recipient,
  sum(AMOUNT) as received_amount
from 
flow.core.ez_token_transfers
WHERE
token_contract ilike 'A.1654653399040a61.FlowToken'
group by recipient
  ),
total_supp as (select sum(received_amount) as total_supply 
  from RECEIVE r 
  left join SEND s on r.recipient=s.SENDER 
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when token_out_contract ilike 'A.1654653399040a61.FlowToken' then token_in_amount else null end) as from_amountt,
sum(case when token_in_contract ilike 'A.1654653399040a61.FlowToken' then token_in_amount else null end) as to_amountt,
from_amountt-to_amountt as circulating_volume
from
  flow.core.ez_swaps
group by 1
), 
  t3 as (select 
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio 
  from t3 join total_supp
where 
date=CURRENT_DATE-30

    """

sql2="""
with SEND as 
(select SENDER,
  sum(AMOUNT) as sent_amount
from 
flow.core.ez_token_transfers
WHERE
token_contract ilike 'A.1654653399040a61.FlowToken'
group by SENDER
  ),
  
RECEIVE as 
(select recipient,
  sum(AMOUNT) as received_amount
from 
flow.core.ez_token_transfers
WHERE
token_contract ilike 'A.1654653399040a61.FlowToken'
group by recipient
  ),
total_supp as (select sum(received_amount) as total_supply 
  from RECEIVE r 
  left join SEND s on r.recipient=s.SENDER 
  where sent_amount is null),
t1 as
(select date_trunc('day',BLOCK_TIMESTAMP) as date,
sum(case when token_out_contract ilike 'A.1654653399040a61.FlowToken' then token_in_amount else null end) as from_amountt,
sum(case when token_in_contract ilike 'A.1654653399040a61.FlowToken' then token_in_amount else null end) as to_amountt,
from_amountt-to_amountt as circulating_volume
from
  flow.core.ez_swaps
group by 1
), 
  t3 as (select 
sum(circulating_volume) over (order by date) as circulating_supply ,
  DATE from t1
  )
select total_supply,circulating_supply,  circulating_supply*100/total_supply as ratio 
  from t3 join total_supp
where 
date=CURRENT_DATE-1
"""

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

with st.expander("Check the analysis"):
    col1,col2=st.columns(2)
    with col1:
        st.metric('Total supply before holidays',df['total_supply'])
    col2.metric('Total supply after holidays',df2['total_supply'])
    
    col1,col2=st.columns(2)

    with col1:
        st.metric('Circulating supply before holidays',df['circulating_supply'])
    col2.metric('Circulating supply after holidays',df2['circulating_supply'])
    
    col1,col2=st.columns(2)
    with col1:
        st.metric('Ratio before holidays',df['ratio'])
    col2.metric('Ratio after holidays',df2['ratio'])
    
    


# In[7]:


st.subheader("3. Ecosystem development before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Flow main ecosystem development. More specifically, we will analyze the following data:')
st.markdown('● New deployed contracts')
st.markdown('● Used contracts')
st.markdown('● Swaps activity')



sql="""
with
  
  debuts as (
  SELECT
distinct event_contract,
min(block_timestamp) as debut
from flow.core.fact_events
group by 1
  )
SELECT
trunc(debut,'day') as date,
   case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
count(distinct event_contract) as n_contracts
from debuts where date >= '2022-12-08' and date <= '2023-01-08'

group by 1,2 order by 1


"""


sql2="""
SELECT
trunc(block_timestamp,'day') as date,
   case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
count(distinct event_contract) as n_contracts
from flow.core.fact_events where date >= '2022-12-08' and date <= '2023-01-08'
group by 1,2 order by 1
"""


sql3="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
      case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  count(distinct tx_id) as n_txns,
  count(distinct trader) as n_wallets,
  sum(TOKEN_IN_AMOUNT/1e6) as volume
from flow.core.ez_swaps
  where block_timestamp >= '2022-12-08' and block_timestamp <= '2023-01-08'
  and TOKEN_IN_CONTRACT = 'A.1654653399040a61.FlowToken'
group by date, period
order by date desc
),
new_wallets as (
select 
  date,
  count(trader) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  trader
from flow.core.ez_swaps
group by trader
)
   where date >= '2022-12-08' and date <= '2023-01-08'
group by date
)

select 
  t.*,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""




results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily new contracts evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='New contracts comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily active contracts evolution',width=300))
    
    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='Active contracts comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily swaps evolution',width=300))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Swaps comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active swappers evolution',width=300))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active swappers comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='volume:Q',color='period')
        .properties(title='Daily swapped volume evolution',width=300))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='volume:Q',color='period')
        .properties(title='Swapped volume comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new swappers evolution',width=300))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New swappers comparison',width=300))
    


# In[8]:


st.subheader("4. Staking before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra staking. More specifically, we will analyze the following data:')
st.markdown('● Staking actions')
st.markdown('● Stakers')
st.markdown('● Volume staked')



sql="""
--credits: adriaparcerisas
WITH
  staking as (
  SELECT
trunc(block_timestamp,'day') as date,
--case when action in ('DelegatorTokensCommitted','TokensCommitted') then 'Staking',
--when action in ('UnstakedTokensWithdrawn','DelegatorUnstakedTokensWithdrawn') then 'Unstaking'
--  end as actions,
count(distinct tx_id) as transactions,
count(distinct delegator) as delegators,
sum(amount) as volume
from flow.core.ez_staking_actions  where action in ('DelegatorTokensCommitted','TokensCommitted')
   and date >= '2022-12-08' and date <= '2023-01-08'
  group by 1 order by 1 asc
  ),
unstaking as (
    SELECT
trunc(block_timestamp,'day') as date,
--case when action in ('DelegatorTokensCommitted','TokensCommitted') then 'Staking',
--when action in ('UnstakedTokensWithdrawn','DelegatorUnstakedTokensWithdrawn') then 'Unstaking'
--  end as actions,
count(distinct tx_id) as transactions,
count(distinct delegator) as delegators,
sum(amount) as volume
from flow.core.ez_staking_actions  where action in ('UnstakedTokensWithdrawn','DelegatorUnstakedTokensWithdrawn')
   and date >= '2022-12-08' and date <= '2023-01-08'
  group by 1 order by 1 asc
)
SELECT
x.date,
      case when x.date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
x.transactions as staking_transactions,y.transactions as unstaking_transactions,
x.delegators as staking_delegators,y.delegators as unstaking_delegators,
x.volume as staked_volume, y.volume*(-1) as unstaked_volume
from staking x
left outer join unstaking y on x.date=y.date 
order by 1 asc 
"""



results = memory(sql)
df = pd.DataFrame(results.records)
df.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='staking_transactions:Q',color='period')
        .properties(title='Daily staking actions evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='staking_transactions:Q',color='period')
        .properties(title='Staking actions comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='unstaking_transactions:Q',color='period')
        .properties(title='Daily unstaking actions evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='unstaking_transactions:Q',color='period')
        .properties(title='Unstaking actions comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='staking_delegators:Q',color='period')
        .properties(title='Daily active stakers evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='staking_delegators:Q',color='period')
        .properties(title='Active stakers comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='unstaking_delegators:Q',color='period')
        .properties(title='Daily unstakers evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='unstaking_delegators:Q',color='period')
        .properties(title='Active unstakers comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='staked_volume:Q',color='period')
        .properties(title='Daily staked volume evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='staked_volume:Q',color='period')
        .properties(title='Staked volume comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='unstaked_volume:Q',color='period')
        .properties(title='Daily unstaked volume evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='unstaked_volume:Q',color='period')
        .properties(title='Unstaked volume comparison',width=300))
    


# In[9]:


st.subheader("5. NFT activity before and after holidays")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Flow NFT activity. More specifically, we will analyze the following data:')
st.markdown('● NFT sales')
st.markdown('● Buyers')
st.markdown('● NFT price')



sql="""
SELECT 
  	date_trunc('day', block_timestamp) as date,
      case when date>='2022-12-23' then 'Holidays period' else 'Before Holidays' end as period,
  	COUNT(DISTINCT tx_id) as sales,
  	sum(price) as sales_volume,
  	avg(price) as average_price,
  	COUNT(DISTINCT buyer) as buyers,
  	min(price) as floor_price
  
FROM flow.core.ez_nft_sales
   where date >= '2022-12-08' and date <= '2023-01-08'
GROUP BY 1,2 
"""



results = memory(sql)
df = pd.DataFrame(results.records)
df.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='sales:Q',color='period')
        .properties(title='Daily NFT actions evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='sales:Q',color='period')
        .properties(title='NFT sales comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='buyers:Q',color='period')
        .properties(title='Daily NFT buyers evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='buyers:Q',color='period')
        .properties(title='Buyers comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='sales_volume:Q',color='period')
        .properties(title='Daily sales volume evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='sales_volume:Q',color='period')
        .properties(title='Sales volume comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='average_price:Q',color='period')
        .properties(title='Daily average NFT price evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='average_price:Q',color='period')
        .properties(title='NFT price comparison',width=300))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='floor_price:Q',color='period')
        .properties(title='Daily NFT floor price evolution',width=300))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='floor_price:Q',color='period')
        .properties(title='NFT floor price comparison',width=300))


# In[10]:


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**.')


# In[ ]:




