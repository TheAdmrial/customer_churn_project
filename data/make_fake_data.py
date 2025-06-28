import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
np.random.seed(986)

n = 1000
plans = ['Free', 'Basic', 'Premium']
regions = ['North', 'South', 'East', 'West']
today = pd.to_datetime('2023-12-31')

customers = pd.DataFrame({
    'customer_id': range(1, n+1)
    , 'join_date': pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 365*3, size = n), unit = 'D') # 'app launch date' plus random number of days
    , 'subscription_plan': np.random.choice(plans, size = n, p = [0.2, 0.5, 0.3])
    , 'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Debit'], size = n)
    , 'region': np.random.choice(regions, size = n)
    , 'age': np.random.randint(18, 70, size =n)
    , 'gender': np.random.choice(['Male', 'Female', 'Prefer not to answer'], size = n)
})

customers['days_since_signup'] = (today - customers['join_date']).dt.days

#Simulate Churn: short-tenure customers more likely to churn
customers['churned'] = np.where(
    customers['days_since_signup'] < 180
    , np.random.binomial(n = 1, p = 0.5, size = n)
    , np.random.binomial(n = 1, p = 0.2, size = n)
)

#generating date_of_last_login
# if churned, last login is before today. today = 12/31/2023
# if active, last login is in the last 30 days

last_login_dates = []
for i, row in customers.iterrows():
    if row['churned'] == 1:
        # if churned, simulate an older last login date
        last_login = row['join_date'] + pd.to_timedelta(
            np.random.randint(10, row['days_since_signup'] if row['days_since_signup'] > 10 else 11), unit = 'D'
        )
    else:
        # if active, last login in the last 30 days
        last_login = today - pd.to_timedelta(np.random.randint(0,31), unit = 'D')
    last_login_dates.append(last_login)

customers = customers.drop(columns = ['days_since_signup'])
customers['date_of_last_login'] = pd.to_datetime(last_login_dates)
customers['days_since_last_login'] = (today - customers['date_of_last_login']).dt.days

# adding tenure per customer in days
# a) if customer is churned then date_of_last_login - join_date
# b) if customer is not churned then today - join_date
customers['tenure_days'] = np.where(
    customers['churned'] == 1
    , (customers['date_of_last_login'] - customers['join_date']).dt.days
    , (today - customers['join_date']).dt.days                              
                                    )




customers.to_csv(
    'data/faker_churn_data.csv'
)
