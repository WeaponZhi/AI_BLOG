
# coding: utf-8

# In[1]:


import requests
from matplotlib.font_manager import * 
import matplotlib.pyplot as plt
import pandas as pd  
import numpy as np
import json  
import time


# In[2]:


def get_data(end_time,count): 
    url = "https://forexdata.wallstreetcn.com/kline?prod_code=XAUUSD&candle_period=8&data_count=365&end_time="          "{end_time}"          "&fields=time_stamp%2Copen_px%2Cclose_px%2Chigh_px%2Clow_px".format(end_time=end_time)
    response = requests.get(url)
    data_list = json.loads(response.text)
    data = data_list.get("data").get("candle").get("XAUUSD")
    df = pd.DataFrame(data,columns=['date','open','close','high','low'],index=list(range(count,count+365)))
    return df


# In[3]:


init_time = 1237507200 # 2009年3月20日


# In[4]:


window = 60*60*24*365 # 每次获取365天的数据


# In[5]:


df = pd.DataFrame()
for i in range(10):
    df = pd.concat([df,get_data(init_time + i * window,i*365)])
    print("get data success ",i)
    time.sleep(0.5)


# In[6]:


df


# In[7]:


# 当收盘价高于开盘价返回"True"
up_and_down = df['close']-df['open'] > 0
up_and_down


# In[8]:


# 每日的涨跌幅
rate_of_return = (df['close']-df['open'])/df['open']
rate_of_return


# In[9]:


# 每日涨跌统计
up_and_down_statistic=up_and_down.value_counts()
up_and_down_statistic


# In[10]:


df['close'].plot(figsize=(15,10))
plt.grid(True)
plt.show()


# In[19]:


r = map(lambda x : time.strftime('%Y-%m-%d',time.localtime(x)),df['date'])
df['date'] = list(r) 


# In[22]:


import matplotlib.finance as mpf
from matplotlib.pylab import date2num
import datetime

def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(date,'%Y-%m-%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time

fig,ax = plt.subplots(figsize=(15,10))
mat_data = df.as_matrix()
num_time = date_to_num(mat_data[:,0])
mat_data[:,0] = num_time

fig.subplots_adjust(bottom=0.2)
ax.xaxis_date()
mpf.candlestick_ochl(ax,mat_data,width=0.6,colorup='r',colordown='g')
plt.grid(True)
plt.xlabel('Data')
plt.ylabel('Price')
plt.show()


# In[23]:


with plt.xkcd():
    myfont = FontProperties(fname='/System/Library/Assets/com_apple_MobileAsset_Font4/2e3dd84241cc7676f2fc8c357c9087fee8cd0075.asset/AssetData/Lantinghei.ttc') 

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.bar([-0.125, 1.0-0.125], [up_and_down_statistic[0], up_and_down_statistic[1]], 0.25)
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks([0, 1])
    ax.set_xlim([-0.5, 1.5])
    ax.set_ylim([0, up_and_down_statistic.max()])
    ax.set_xticklabels([u'跌', u'涨'],fontproperties=myfont)
    plt.yticks([])
    plt.title(u'涨跌统计',fontproperties=myfont)
    fig.text(
        0.5, 0.05,
        u'调皮的统计数据',
        ha='center',fontproperties=myfont)
plt.show()


# In[24]:


rate_of_return.describe()


# In[25]:


rate_of_return.plot(kind='line',style='k--',figsize=(15,10))
plt.show()


# In[26]:


rate_of_return.plot(kind='hist',bins=150,alpha=0.3,color='g',normed=1)
rate_of_return.plot(kind='kde',xlim=[-0.1,0.1],style='r',grid=True,figsize=(15,10))
plt.show()


# In[27]:


from __future__ import division  
from sklearn import tree
from collections import deque


window = 2
    

X = deque()
y = deque()
clf = tree.DecisionTreeClassifier()
prediction = 0
test_num = 0
win_num = 0

current_index = 2

for current_index in range(current_index, len(up_and_down)-1, 1):
    fact = up_and_down[current_index+1]
        
    X.append(list(up_and_down[(current_index-window): current_index]))
    y.append(up_and_down[current_index])
    if len(y) > 200:
        test_num += 1
        clf.fit(X, y)
    
        prediction = clf.predict([list(up_and_down[(current_index-window+1): current_index+1])])
        
        if prediction[0] == fact:
            win_num += 1
print("预测准确率为",win_num/test_num)


# In[28]:


import graphviz
dot_data = tree.export_graphviz(clf,out_file=None,
                                filled=True,
                                rounded=True,special_characters=True,
                                feature_names=['first day rate','second day rate'])
graph = graphviz.Source(dot_data)
graph.render("Finance")


# In[31]:


# 窗口期对预测数量的影响
win_ratio = []
window_list = [x for x in range(22) if x != 0]
i = 1
for window in window_list:
    
    X = deque()
    y = deque()
    clf = tree.DecisionTreeClassifier()
    prediction = 0
    test_num = 0
    win_num = 0


    current_index = window
    
    for current_index in range(current_index, len(up_and_down)-1, 1):
        fact = up_and_down[current_index+1]
        
        X.append(list(up_and_down[(current_index-window): current_index]))
        y.append(up_and_down[current_index])
        if len(y) > 100:
            test_num += 1
            clf.fit(X, y)
    
            prediction = clf.predict([list(up_and_down[(current_index-window+1): current_index+1])])
        
            if prediction[0] == fact:
                win_num += 1
    ratio = win_num/test_num
    print("已完成预测",i,'次')
    i += 1
    win_ratio.append(ratio)


# In[32]:


fig = plt.figure(figsize=(12,10))
plt.plot(window_list,win_ratio,'ro--')
plt.show()


# In[33]:


# 样本数量对预测率的影响
window = 2
win_ratio = []
samples_list = [x*5 for x in range(60) if x != 0]

for samples in samples_list:
    
    X = deque()
    y = deque()
    clf = tree.DecisionTreeClassifier()
    prediction = 0
    test_num = 0
    win_num = 0


    current_index = 2

    for current_index in range(current_index, len(up_and_down)-1, 1):
        fact = up_and_down[current_index+1]
        
        X.append(list(up_and_down[(current_index-window): current_index]))
        y.append(up_and_down[current_index])
        if len(y) > samples:
            test_num += 1
            clf.fit(X, y)
    
            prediction = clf.predict([list(up_and_down[(current_index-window+1): current_index+1])])
        
            if prediction[0] == fact:
                win_num += 1
    ratio = win_num/test_num        
    win_ratio.append(ratio)
print("预测完毕")


# In[34]:


fig = plt.figure(figsize=(12,10))
plt.plot(samples_list,win_ratio,'ro--')
plt.show()

