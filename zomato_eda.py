import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from numpy import mean

## Will use this sometime in future
# def returnDict(values):
#     d = dict()
#     for index, i in enumerate(values):
#         d.update({i: index})
#     return d


## Reading into data frame
path = r'<your file path>'
data = pd.read_csv(path + r'\zomato.csv', encoding='utf-8')
data['dish_liked_count'] = data.dish_liked.str.count(',')

## Some cleaning and changes into data for ease of usage
data['approx_cost(for two people)'] = data['approx_cost(for two people)'].str.replace(',', '')
data['approx_cost(for two people)'] = data['approx_cost(for two people)'].astype(float)

## Removing all rows where location is not available
data = data[data.location.notnull()]
data = data[data.rate.str.split('/').str[0] != '-']

## The code commented on top, this set of code will use that - will use in future.
# all_loc_codes = returnDict(data.location.unique())
# data['location'] = data['location'].map(all_loc_codes)
# rest_types = returnDict(data.rest_type.unique())
# data['rest_type'] = data['rest_type'].map(rest_types)
# data.book_table.replace('Yes', 1).replace('No', 0)

## Again some data cleaning
data['rate'] = data['rate'].str.split('/').str[0].str.strip()
data['rate'] = data['rate'].replace('NEW', None)
data['rate'] = data['rate'].astype(float)

## For each missing rating, I'm, using mean of (rating of the restaurant chain & rating of all the restaurants in that area)
## Reason for choosing these two as parameters is that the taste remains mostly same within the food chain, things such as hygiene, staff, crowd, etc. vary with location.
mean_name = data.groupby('name').rate.mean().rename('rating_name')
mean_location = data.groupby('location').rate.mean().rename('rating_location')
data = (data.join(mean_name, on='name').join(mean_location, on='location'))
# data['rating_name'].fillna(0, inplace=True) ## Was going to use this, but simply using location rating won't do justice in some cases.
data['rating_fill'] = (data['rating_location'] + data['rating_name'])/2
data['rate'] = data['rate'].combine_first(data['rating_fill'])
data.drop(columns=['phone', 'rating_name', 'rating_location', 'rating_fill'], inplace=True)

## Now we'll start visualizing data
## Count of restaurants in each location
sns.factorplot(x='location', data=data, kind='count', height=2, aspect=3, order=data['location'].value_counts().index).set_xticklabels(rotation=90)
plt.title('Restaurants per location')

## Average cost for two in each location
sns.catplot(x='location', y='approx_cost(for two people)', data=data, estimator=mean, height=2, aspect=3, kind='bar')
plt.xticks(rotation=90)
plt.title('Average cost in each location')
plt.show('hold')

## Top restaurant chains (no of restaurants)
res_chains = data.name.value_counts()[:10]
sns.barplot(x=res_chains, y=res_chains.index)
plt.title('Top 10 Restaurant chains')
plt.show('hold')

## Most expensive Restaurants
most_expensive_res = data[['name', 'approx_cost(for two people)']].groupby('name')['approx_cost(for two people)'].max().sort_values(ascending=False)[:10]
sns.barplot(x=most_expensive_res, y=most_expensive_res.index)
plt.title('Top 10 expensive restaurants')
plt.show('hold')

## Restaurants which take online order
accept_orders = data.online_order.value_counts()
accept_orders.plot.pie(autopct='%.1f%%', startangle=90)
plt.title('Restaurants taking online order')
plt.show('hold')

## Restaurants where table booking is available
table_book = data.book_table.value_counts()
table_book.plot.pie(autopct='%.1f%%', startangle=450)
plt.title('Restaurants where booking is available')
plt.show('hold')

## Distribution of ratings
sns.kdeplot(data=data, x='rate')
plt.title('Rating Distribution')
plt.show('hold')

## Distribution of cost per two persons
sns.kdeplot(data=data, x='approx_cost(for two people)')
plt.title('Average cost for two persons distribution')
plt.show('hold')

## Relation between cost per two persons and rating
sns.scatterplot(x='rate', y='approx_cost(for two people)', data=data)
plt.title('Relation between average cost / 2 person and rating')
plt.show('hold')

## Top 10 of restaurants type (count)
type_rest = data.groupby('rest_type').size().sort_values(ascending=False)[:10]
sns.barplot(x=type_rest, y=type_rest.index)
plt.title('Top 10 restaurants per type')
plt.show('hold')

## Top 10 cuisines
## For this I had to do write some extra code; get the name of all cuisines and then count the occurances
all_cuisines = dict()
distinct_cuisines = set()
for index, i in enumerate(data.cuisines.unique()):
    try:
        distinct_cuisines.add(*[j for j in i.split(',')])
    except:
        pass
df = pd.DataFrame(columns=['Cuisines', 'Count'])
for index, i in enumerate(distinct_cuisines):
    df.loc[index] = [i] + [data[~data.cuisines.isna() & data.cuisines.str.contains(i)]['name'].count()]
    # all_cuisines.update({i: data[~data.cuisines.isna() & data.cuisines.str.contains(i)]['name'].count()})
df = df.sort_values(by='Count', ascending=False)[:10]
sns.barplot(data=df, x='Count', y='Cuisines')
plt.show('hold')

## Most popular Ice Cream parlors (I love ice creams :p)
ice_cream_par = data[~data.cuisines.isna() & data.cuisines.str.contains('Ice Cream')].groupby('name').size().sort_values(ascending=False)[:10]
sns.barplot(x=ice_cream_par, y=ice_cream_par.index)
plt.title('Most popular ice cream parlours')
plt.show('hold')

## Most no of restaurants in an area serving each cuisine
for i in distinct_cuisines:
    print(i.ljust(13), ' - ',*data[~data.cuisines.isna() & data.cuisines.str.contains(i)].groupby('location').size().nlargest(1).index.tolist())

## Restaurant type count for each location
print(pd.pivot_table(data, values='name', index='location', columns='listed_in(type)', aggfunc='count'))
