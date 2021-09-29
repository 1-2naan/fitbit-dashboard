

import dash
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from datetime import date
import statistics
import requests
import oauth2
import time
from pprint import pprint
import json
import csv

access_token='eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM0JCRjQiLCJzdWIiOiI5NzQ3ODkiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNjY0NDI5NjY1LCJpYXQiOjE2MzI4OTM2NjV9.nDUEDMFqnY_MEqOgj7JV-L_bM4S1r5Qs5_H8IGB_0dg'
user_id='974789'


app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2021, 8, 5),
        max_date_allowed=date(2021, 9, 19),
        initial_visible_month=date(2021, 8, 15),
        start_date=date(2021,8,15),
        end_date=date(2021, 9, 2)

    ),
    
    dcc.Dropdown(
            id='date_select', clearable=False,
            options=[
                     {"label": "Sleep and Wake Up Time", "value": 1},
                     {"label": "Light, Deep and REM", "value": 2},
                     {"label": "Insomnia", "value": 3},
                     {"label": "Daytime Sleepiness", "value": 4},
                     {"label": "REM Sleep Disorder", "value": 5},
                     {"label": "Sleep Disturbances", "value": 6}],
            value=1
            ),
    
    
    dcc.Graph(id='graph'),
    html.Br(),

    html.Div(id='output_container_1',style={'margin-bottom':'50px', 'text-align':'center','font-weight':'bold',"fontSize": "2rem"}),
    html.Div(id='output_container_2',style={'margin-bottom':'50px', 'text-align':'center','font-weight':'bold',"fontSize": "2rem"})
])


import numpy as np
@app.callback(
    [Output('graph','figure'),
    Output('output_container_1','children'),
    Output('output_container_2','children')],
   [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
       Input("date_select", "value")])

def update_output(start_date,end_date,value):

    if start_date is not None and end_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
            
        start_date_day = str(start_date_object.day)
        start_date_month = str(start_date_object.month)
        end_date_day = str(end_date_object.day)
        end_date_month = str(end_date_object.month)
        
        if int(start_date_day)<10:
            start_date_day='0'+start_date_day
        if int(start_date_month)<10:
            start_date_month='0'+start_date_month
        if int(end_date_day)<10:
            end_date_day='0'+end_date_day
        if int(end_date_month)<10:
            end_date_month='0'+end_date_month
            
        start_date_box = str(start_date_object.year)+'-'+start_date_month+'-'+start_date_day
        end_date_box = str(end_date_object.year)+'-'+end_date_month+'-'+end_date_day

        
        activity_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box +'/'+ end_date_box + '.json', 
                                headers = {'Authorization':'Bearer  ' + access_token})
        
        data=activity_request.json()
        
        bedtime=[]
        bedtime_sum=0
        if 'sleep' in data:
            for i in range(len(activity_request.json()['sleep'])):
                #print(activity_request.json()['sleep'][i]['startTime'])
                bedtime_current=(int(activity_request.json()['sleep'][i]['startTime'].split("T")[1].split(":")[0])*3600 + int(activity_request.json()['sleep'][i]['startTime'].split("T")[1].split(":")[1])*60 + int(activity_request.json()['sleep'][i]['startTime'].split("T")[1].split(":")[2].split(".")[0]))
                bedtime.append(bedtime_current)
                bedtime_sum=bedtime_sum+bedtime_current
            bedtime_sum=statistics.median(bedtime)
        #print(bedtime_sum)
        wakeup=[]
        wakeup_sum=0
        minutestofall=0
        if 'sleep' in data:
            for i in range(len(activity_request.json()['sleep'])):
                #print(activity_request.json()['sleep'][i]['startTime'])
                wakeup_current=(int(activity_request.json()['sleep'][i]['endTime'].split("T")[1].split(":")[0])*3600 + int(activity_request.json()['sleep'][i]['endTime'].split("T")[1].split(":")[1])*60 + int(activity_request.json()['sleep'][i]['endTime'].split("T")[1].split(":")[2].split(".")[0]))
                wakeup.append(wakeup_current)
                wakeup_sum=wakeup_sum+wakeup_current
                minutestofall = minutestofall + activity_request.json()['sleep'][i]['minutesToFallAsleep']
                
            wakeup_sum=statistics.median(wakeup)
                
        print('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box +'/'+ end_date_box + '.json')
        print(minutestofall)

        
        container1 = "Avg. Bed Time = " + str(int(bedtime_sum/3600))+':'+str(int((bedtime_sum/3600-int(bedtime_sum/3600))*60)) + " AM," + " Wake Up Time = " + str(int(wakeup_sum/3600))+':'+str(int((wakeup_sum/3600-int(wakeup_sum/3600))*60)) + " AM"
        container2 = "Avg. time to fall asleep =  " + str(minutestofall) + " mins"
        
        if value == 1:
            fig=go.Figure()
            fig=go.Figure(data=go.Violin(x=wakeup,meanline_visible=True, name = "Wake Up Time"))
            fig.add_trace(go.Violin(x=bedtime,meanline_visible=True, name = "Go To Bed Time"))

            fig.update_layout(
                yaxis = dict(tickmode = 'array',
                             tickvals = [25, 25.5, 26, 26.5],
                             ticktext = ['Deep', 'Light', 'REM', 'Awake']),
                xaxis = dict(tickmode = 'array',
                             tickvals = [0,3600, 7200, 10800, 14400, 18000, 21600, 25200, 28800, 32400,36000,39600],
                             ticktext = ['Midnight','1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM','8AM','9AM','10AM','11AM']))
            container1 = "Avg. Bed Time = " + str(int(bedtime_sum/3600))+':'+str(int((bedtime_sum/3600-int(bedtime_sum/3600))*60)) + " AM," + " Wake Up Time = " + str(int(wakeup_sum/3600))+':'+str(int((wakeup_sum/3600-int(wakeup_sum/3600))*60)) + " AM"
            container2 = "Avg. time to fall asleep =  " + str(minutestofall) + " mins"
        if value == 2:
            fig=stages(data)
            container1= 'Between ' + start_date_string + ' And ' + end_date_string
            container2= ' '

        if value == 3:
            fig=insomnia(start_date_box,end_date_box)
            container1= ' '
            container2= ' ' 
            
        if value == 4:
            fig=daytime_sleepiness(start_date_box,end_date_box)
            container1= ' '
            container2= ' ' 
            
        if value == 5:
            fig=rem_disorder(start_date_box,end_date_box)
            container1= 'REM Sleep is not concerning'
            container2= ' ' 
            
        if value == 6:
            fig, condition=disturb(start_date_box,end_date_box)
            container1= 'Between ' + start_date_string + ' And ' + end_date_string
            container2= 'Sleep Disturbances are' + condition
            
        return fig, container1, container2


def stages(data):
    
    #calculating wake stage time, number of days with wake sleep and average wake sleep per sleep night
    wake_sum=0
    wake_counter=0
    for i in range(len(data['sleep'])):
        if 'wake' in (data['sleep'][i]['levels']['summary']):
            wake_sum=wake_sum+data['sleep'][0]['levels']['summary']['wake']['minutes']
            wake_counter=wake_counter+1
    wake_avg=wake_sum/wake_counter
    
    deep_sum=0
    deep_counter=0
    for i in range(len(data['sleep'])):
        if 'deep' in (data['sleep'][i]['levels']['summary']):
            deep_sum=deep_sum+data['sleep'][0]['levels']['summary']['deep']['minutes']
            deep_counter=deep_counter+1
    deep_avg=deep_sum/deep_counter
    
    light_sum=0
    light_counter=0
    for i in range(len(data['sleep'])):
        if 'light' in (data['sleep'][i]['levels']['summary']):
            light_sum=light_sum+data['sleep'][0]['levels']['summary']['light']['minutes']
            light_counter=light_counter+1
    light_avg=light_sum/light_counter
    
    rem_sum=0
    rem_counter=0
    for i in range(len(data['sleep'])):
        if 'rem' in (data['sleep'][i]['levels']['summary']):
            rem_sum=rem_sum+data['sleep'][0]['levels']['summary']['rem']['minutes']
            rem_counter=rem_counter+1
    rem_avg=rem_sum/rem_counter
    
    #creating dataframe to store different stages' average
    df=pd.DataFrame()
    df['Stages']='wake','light','deep','rem'
    df['Average in Minutes']=wake_avg,light_avg,deep_avg,rem_avg
    df['Number of days']=wake_counter,light_counter,deep_counter,rem_counter
    df['Total Days']=len(data['sleep'])
    
    #creating dataframe to store ideal stages' average
    dt=pd.DataFrame()
    dt['Stages']='wake','light','deep','rem'
    dt['Average in Minutes']=50,200,100,100
    
    #plotting first graph with real averages
    fig = px.bar(df, x="Average in Minutes", y="Stages", color='Stages', orientation='h',
                 color_discrete_sequence=["rgba(244,30,30,1)", "rgba(173,216,230,1)", "rgb(0,0,139,1)", "rgb(0,128,0,1)"],
                 height=400,
                 title='Sleep Stages')
    fig.update_layout(plot_bgcolor="rgba(58, 71, 80, 0.1)")
    
    #plotting second graph with ideal values
    fig.add_trace(go.Bar( x=dt["Average in Minutes"]-df["Average in Minutes"], y=dt["Stages"],orientation='h',
                        marker=dict(
            color='rgba(150, 215, 0, 0.5)',
            line=dict(color='rgba(192, 247, 0, 1.0)', width=1)
        ),name='Ideal'
                        ))
    fig.update_layout(plot_bgcolor="rgba(58, 71, 80, 0.1)")
    
    return fig


# In[ ]:


def insomnia(start_date_box,end_date_box):
    
    activity_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box + '/' + end_date_box+'.json', headers = {'Authorization':'Bearer  ' + access_token})
    insomnia=[]
    date=[]
    for i in range(len(activity_request.json()['sleep'])):
        insomnia.append(activity_request.json()['sleep'][i]['minutesAwake'])
        date.append(activity_request.json()['sleep'][i]['dateOfSleep'])
    sleep=pd.DataFrame()
    sleep['Date']=date
    sleep['Awake']=insomnia
    sleep

    yolo_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/activities/activityCalories/date/'+ end_date_box + '/' + start_date_box + '.json', 
                                    headers = {'Authorization':'Bearer  ' + access_token})

    BMR=pd.DataFrame.from_dict(yolo_request.json()['activities-activityCalories'])

    df = pd.merge(BMR, sleep, how='inner', left_on='dateTime', right_on='Date')

    df['value'] = df['value'].astype(int)
    df['Awake'] = df['Awake'].astype(int)
    df['value'] = (df['value'] - df['value'].min()) / (df['value'].max() - df['value'].min())
    df['Awake'] = (df['Awake'] - df['Awake'].min()) / (df['Awake'].max() - df['Awake'].min())
    for i in range(df.shape[0]):
        if (df.loc[i,'Awake']>0):
            df.at[i,'New_Score']=df.loc[i,'Awake']*5 + df.loc[i,'value']
        else:
            df.at[i,'New_Score']=df.loc[i,'Awake'] + df.loc[i,'value']

    fig=px.scatter(x=np.arange(df.shape[0]),y=df["New_Score"],trendline="lowess",trendline_color_override="black",labels={
                             "x": "Date",
                             "y": "Insomnia Score",})
    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Unlikely'
    fig.update_traces(marker=dict(color="green",size=12),showlegend=True)
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>= 2.5]),y=df[df["New_Score"] >= 2.5]['New_Score'],marker=dict(color='rgba(252,150,5,1)',size=12),mode="markers",name="Slight Probability"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>=4]),y=df[df["New_Score"] >= 4]['New_Score'],marker=dict(color='rgba(252,100,5,1)',size=12),mode="markers",name="Decent Probability"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>=5]),y=df[df["New_Score"] >= 5]['New_Score'],marker=dict(color='rgba(252,0,0,1)',size=12),mode="markers",name="Concerning"))
    fig.update_layout(
        yaxis = dict(tickmode = 'array',
                     tickvals = [1, 2, 3, 4,5],
                     ticktext = [' ', ' ', ' ', ' ',' ']),
        xaxis = dict(tickmode = 'array',
                     tickvals = [0,df.shape[0]-1],
                     ticktext = [sleep['Date'][sleep.shape[0]-1],sleep['Date'][0]]))
    return fig


# In[ ]:


def daytime_sleepiness(start_date_box,end_date_box):
    
    activity_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box + '/' + end_date_box+'.json', 
                                headers = {'Authorization':'Bearer  ' + access_token})
    rem=[]
    date=[]
    for i in range(len(activity_request.json()['sleep'])):
        if 'rem' in (activity_request.json()['sleep'][i]['levels']['summary']):
            rem.append(activity_request.json()['sleep'][i]['levels']['summary']['rem']['minutes'])
            date.append(activity_request.json()['sleep'][i]['dateOfSleep'])

    sleep=pd.DataFrame()
    sleep['Date']=date
    sleep['REM']=rem
    yolo_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/activities/minutesSedentary/date/'+ start_date_box + '/' + end_date_box + '.json', 
                                    headers = {'Authorization':'Bearer  ' + access_token})

    BMR=pd.DataFrame.from_dict(yolo_request.json()['activities-minutesSedentary'])

    df = pd.merge(BMR, sleep, how='inner', left_on='dateTime', right_on='Date')

    df['value'] = df['value'].astype(int)
    df['REM'] = df['REM'].astype(int)
    df['value'] = (df['value'] - df['value'].min()) / (df['value'].max() - df['value'].min())
    df['REM'] = (df['REM'] - df['REM'].min()) / (df['REM'].max() - df['REM'].min())

    for i in range(df.shape[0]):
        if (df.loc[i,'value']>0.7 and df.loc[i,'REM']<0.5):
            df.at[i,'New_Score']=df.loc[i,'value']*5 - df.loc[i,'REM']
        else:
            df.at[i,'New_Score']=df.loc[i,'value'] 

    fig=px.scatter(x=np.arange(df.shape[0]),y=df["New_Score"],trendline="lowess",trendline_color_override="black",labels={
                             "x": "Date",
                             "y": "Daytime Sleepiness Score",})
    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Unlikely'
    fig.update_traces(marker=dict(color="green",size=12),showlegend=True)
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>= 2.5]),y=df[df["New_Score"] >= 2.5]['New_Score'],marker=dict(color='rgba(252,150,5,1)',size=12),mode="markers",name="Slight Probability"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>=4]),y=df[df["New_Score"] >= 4]['New_Score'],marker=dict(color='rgba(252,100,5,1)',size=12),mode="markers",name="Decent Probability"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['New_Score']>=5]),y=df[df["New_Score"] >= 5]['New_Score'],marker=dict(color='rgba(252,0,0,1)',size=12),mode="markers",name="Concerning"))
    fig.update_layout(
        yaxis = dict(tickmode = 'array',
                     tickvals = [1, 2, 3, 4,5],
                     ticktext = [' ', ' ', ' ', ' ',' ']),
        xaxis = dict(tickmode = 'array',
                     tickvals = [0,df.shape[0]-1],
                     ticktext = [sleep['Date'][sleep.shape[0]-1],sleep['Date'][0]]))

    
    return fig


# In[ ]:


def rem_disorder(start_date_box,end_date_box):
    
    activity_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box + '/' + end_date_box+'.json', 
                                headers = {'Authorization':'Bearer  ' + access_token})
    rem=[]
    date=[]
    for i in range(len(activity_request.json()['sleep'])):
        if 'rem' in (activity_request.json()['sleep'][i]['levels']['summary']):
            rem.append(activity_request.json()['sleep'][i]['levels']['summary']['rem']['minutes'])
            date.append(activity_request.json()['sleep'][i]['dateOfSleep'])

    sleep=pd.DataFrame()
    sleep['Date']=date
    sleep['REM']=rem
    df=sleep
    fig=px.scatter(x=np.arange(df.shape[0]),y=df["REM"],trendline="lowess",trendline_color_override="black",labels={
                             "x": "Date",
                             "y": "REM Sleep Time",})
    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Healthy'
    fig.update_traces(marker=dict(color="green",size=12),showlegend=True)
    fig.add_trace(go.Scatter(x=np.array(df.index[df['REM']<= 70]),y=df[df["REM"] <= 70]['REM'],marker=dict(color='rgba(252,150,5,1)',size=12),mode="markers",name="Slighlty unhealthy"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['REM']<=50]),y=df[df["REM"] <=50]['REM'],marker=dict(color='rgba(252,100,5,1)',size=12),mode="markers",name="Unhealthy"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['REM']<=30]),y=df[df["REM"] <=30]['REM'],marker=dict(color='rgba(252,0,0,1)',size=12),mode="markers",name="Concerning"))
    fig.show()
    fig.update_layout(
                    xaxis = dict(tickmode = 'array',
                                 tickvals = [0,sleep.shape[0]-1],
                                 ticktext = [sleep['Date'][sleep.shape[0]-1],sleep['Date'][0]]))
    return fig


# In[ ]:


def disturb(start_date_box,end_date_box):
    activity_request = requests.get('https://api.fitbit.com/1.2/user/' + user_id + '/sleep/date/'+ start_date_box + '/' + end_date_box+'.json', 
                                headers = {'Authorization':'Bearer  ' + access_token})
    count=[]
    date=[]
    for i in range(len(activity_request.json()['sleep'])):
        if 'wake' in (activity_request.json()['sleep'][i]['levels']['summary']):
            count.append(activity_request.json()['sleep'][i]['levels']['summary']['wake']['count'])
            date.append(activity_request.json()['sleep'][i]['dateOfSleep'])
    
    sleep=pd.DataFrame()
    sleep['Date']=date
    sleep['count']=count
    df=sleep
    fig=px.scatter(x=np.arange(df.shape[0]),y=df["count"],trendline="lowess",trendline_color_override="black",labels={
                             "x": "Date",
                             "y": "Sleep Disturbances",})
    fig['data'][0]['showlegend']=True
    fig['data'][0]['name']='Healthy'
    fig.update_traces(marker=dict(color="green",size=12),showlegend=True)
    fig.add_trace(go.Scatter(x=np.array(df.index[df['count']> 14]),y=df[df["count"] >14]['count'],marker=dict(color='rgba(252,150,5,1)',size=12),mode="markers",name="Slighlty unhealthy"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['count']> 18]),y=df[df["count"] >18]['count'],marker=dict(color='rgba(252,100,5,1)',size=12),mode="markers",name="Unhealthy"))
    fig.add_trace(go.Scatter(x=np.array(df.index[df['count']> 20]),y=df[df["count"] >20]['count'],marker=dict(color='rgba(252,0,0,1)',size=12),mode="markers",name="Concerning"))
    fig.update_layout(
        yaxis = dict(tickmode = 'array',
                     tickvals = [8, 13, 17, 20, 24],
                     ticktext = ['1', '2', '3','4','5']),
        xaxis = dict(tickmode = 'array',
                     tickvals = [0,df.shape[0]-1],
                     ticktext = [sleep['Date'][sleep.shape[0]-1],sleep['Date'][0]]))
    count=np.array(count)
    count=count/5
    if(np.mean(count)>2.5):
        condition = " Concerning"
    else:
        condition = " Not concerning"
    return fig, condition

if __name__ == '__main__':
    app.run_server(debug=True)
