# Training Logs
# Goal: Ingest all Garmin training activities to date into tabular format
#       Create daily, weekly, monthly, and yearly training log files to be exported as csv
#       Generate summary statistics and plot useful trends (By week, month, year, activity type)

import math
from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

from numpy.polynomial.polynomial import polyfit
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

# function: doLogin
# Creates a garmin client object and logs into garmin connect
# Returns the client object

def doLogin(email, pswd):
    try:
        client = Garmin("johnnylo245@gmail.com", "Pleasesnow24")
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client init: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client init")
        quit()

    try:
        client.login()
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client login: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client login")
        quit()

    return client

# function: getHrZoneDuration(activityId)
# Gets the time in heart rate zones for a specific activity
# Returns a dictionary with the times in seconds {z1:?, z2:?, z3:?, z4:?, z5:?}

def getHrZoneDuration(activityId, client):
    try:
        hr_timezones = client.get_activity_hr_in_timezones(activityId)
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client get activity hr timezones: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client get activity hr timezones")
        quit()

    returnVal = {
        'z1': hr_timezones[0]['secsInZone'],
        'z2': hr_timezones[1]['secsInZone'],
        'z3': hr_timezones[2]['secsInZone'],
        'z4': hr_timezones[3]['secsInZone'],
        'z5': hr_timezones[4]['secsInZone'],
    }

    return returnVal

# function: parseActivityRating(text)
# Parse the rating substring out of activity description and return it

def parseActivityRating(text):
    if isinstance(text, str):
        matches = re.findall(':[A-Z]',text)
        if matches == []:
            return ""
        else:
            return matches[0][-1]
    else:
        return ""

# function: getTotals
# Get activity data for this week and calculate totals
# Totals: time, distance, vert, Time in Zones, Percent of time in zones,
def getTotals(activities, days):
    #activities = getActivities(email, pswd, 5000)
    if days == "all":
        timeFilter = 0
    else:
        days = 1000*60*60*24 * days
        timeFilter = math.floor(datetime.today().timestamp() * 1000) - days

    filterActivities = activities[activities["Start_Time_Milli"] > timeFilter]

    totals = {
        "Time_Hours": filterActivities["Duration_Hours"].sum(),
        "Distance_Miles": filterActivities["Distance_Miles"].sum(),
        "Vertical_FT": filterActivities["Vertical_Gain_Feet"].sum(),
        "Z0_Percent": (((filterActivities["Duration_Hours"]).sum() -
                      ((filterActivities["HR_Z1"]).sum() +
                      (filterActivities["HR_Z2"]).sum() +
                      (filterActivities["HR_Z3"]).sum() +
                      (filterActivities["HR_Z4"]).sum() +
                      (filterActivities["HR_Z5"]).sum()))/(filterActivities["Duration_Hours"]).sum())*100,
        "Z1_Percent": (((filterActivities["HR_Z1"])).sum()/(filterActivities["Duration_Hours"].sum()))*100,
        "Z2_Percent": (((filterActivities["HR_Z2"])).sum()/(filterActivities["Duration_Hours"].sum()))*100,
        "Z3_Percent": (((filterActivities["HR_Z3"])).sum()/(filterActivities["Duration_Hours"].sum()))*100,
        "Z4_Percent": (((filterActivities["HR_Z4"])).sum()/(filterActivities["Duration_Hours"].sum()))*100,
        "Z5_Percent": (((filterActivities["HR_Z5"])).sum()/(filterActivities["Duration_Hours"].sum()))*100
    }

    return totals

# funtion: getActivities
# Logs into garmin and fetches all available activity data
# Formats activity data into a pandas dataframe, which is returned

def getActivities(email, pswd, howmany, client):
    #client = doLogin(email, pswd)

    table = {
        'activity_ID':[],
        'Start_Time_Local':[],
        'Start_Time_Milli':[],
        'Type':[],
        'Distance_Miles':[],
        'Duration_Hours':[],
        'Moving_Duration_Hours':[],
        'Elapsed_Duration_Hours':[],
        'Vertical_Gain_Feet':[],
        'Vertical_Loss_Feet':[],
        'Average_HR':[],
        'Max_HR':[],
        'HR_Z1':[],
        'HR_Z2':[],
        'HR_Z3':[],
        'HR_Z4':[],
        'HR_Z5':[],
        'Rating':[],
        'Notes':[]
    }

    try:
        activities = client.get_activities(0,howmany-1) # 0=start, 1=limit
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client get activities: %s" % err)
        quit()
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client get activities")
        quit()

    for activity in activities:
        table['activity_ID'].append(activity['activityId'])
        table['Start_Time_Local'].append(activity['startTimeLocal'])
        table['Start_Time_Milli'].append(activity['beginTimestamp'])
        table['Type'].append(activity['activityType']['typeKey'])
        table['Distance_Miles'].append(activity['distance']*0.000621371 if activity['distance'] is not None else 0 )
        table['Duration_Hours'].append(activity['duration']/3600 if activity['duration'] is not None else 0)
        table['Moving_Duration_Hours'].append(activity['movingDuration']/3600 if activity['movingDuration'] is not None else 0)
        table['Elapsed_Duration_Hours'].append(activity['elapsedDuration']/3600000 if activity['elapsedDuration']is not None else 0)
        table['Vertical_Gain_Feet'].append(activity['elevationGain']*3.28084 if activity['elevationGain'] is not None else 0)
        table['Vertical_Loss_Feet'].append(activity['elevationLoss']*3.28084 if activity['elevationLoss'] is not None else 0)
        table['Average_HR'].append(activity['averageHR'])
        table['Max_HR'].append(activity['maxHR'])
        table['HR_Z1'].append(0)
        table['HR_Z2'].append(0)
        table['HR_Z3'].append(0)
        table['HR_Z4'].append(0)
        table['HR_Z5'].append(0)
        table['Rating'].append(parseActivityRating(activity['description']))
        table['Notes'].append(activity['description'])

    df = pd.DataFrame(table)
    #print(df.head())
    return df

# Add heart rate zone timing to the table of activities
# I split this out of getActivities to filter the activity data before
# making one request per activity...
def appendHrTimes(table, client):
    #client = doLogin(email, pswd)
    for index, row in table.iterrows():
        zones = getHrZoneDuration(row['activity_ID'], client)
        table.loc[index, 'HR_Z1'] = zones['z1']/3600 # Reporting in hours
        table.loc[index, 'HR_Z2'] = zones['z2']/3600
        table.loc[index, 'HR_Z3'] = zones['z3']/3600
        table.loc[index, 'HR_Z4'] = zones['z4']/3600
        table.loc[index, 'HR_Z5'] = zones['z5']/3600
    #print(table.head())
    return table

def getActivitiesByPeriod(period, weeklies="daily", hr=True):
    if isinstance(period, str):
        if period == "thisweek":
            timeFilter = math.floor(datetime.combine(date.today() - timedelta(days=date.today().weekday()), datetime.min.time()).timestamp() *1000)
        elif period == "thismonth":
            timeFilter = math.floor(datetime.combine(date.today().replace(day=1), datetime.min.time()).timestamp() *1000)
        elif period == "threemonths":
            days = 1000*60*60*24 * 90
            timeFilter = math.floor(datetime.today().timestamp() * 1000) - days
        elif period == "sixmonths":
            days = 1000*60*60*24 * 180
            timeFilter = math.floor(datetime.today().timestamp() * 1000) - days
        elif period == "oneyear":
            days = 1000*60*60*24 * 365
            timeFilter = math.floor(datetime.today().timestamp() * 1000) - days
    else:
        days = 1000*60*60*24 * int(period)
        timeFilter = math.floor(datetime.today().timestamp() * 1000) - days

    email = 'johnnylo245@gmail.com'
    pswd = 'Pleasesnow24'
    client = doLogin(email, pswd)
    activities = getActivities(email, pswd, 5000, client)
    activities = activities[activities['Start_Time_Milli'] > timeFilter]

    if hr:
        activities = appendHrTimes(activities, client)

    activities['DayofWeek'] = activities.apply (lambda row: numberToDay(datetime.fromtimestamp(int(row.Start_Time_Milli)/1000.0).weekday()), axis=1)
    activities['Week'] = activities.apply (lambda row: datetime.fromtimestamp(int(row.Start_Time_Milli)/1000.0).isocalendar()[1], axis=1)
    activities['Month'] = activities.apply (lambda row: datetime.fromtimestamp(int(row.Start_Time_Milli)/1000.0).month, axis=1)
    activities['Year'] = activities.apply (lambda row: datetime.fromtimestamp(int(row.Start_Time_Milli)/1000.0).year, axis=1)
    activities['Day'] = activities.apply (lambda row: datetime.fromtimestamp(int(row.Start_Time_Milli)/1000.0).day, axis=1)


    if weeklies == "weekly":
        activities = buildWeeklies(activities)
    return activities

def writeActivitiesCsv(table, filename):
    table.to_csv(filename, sep=',')

def numberToDay(numb):
    if numb == 0:
        return "Monday"
    elif numb == 1:
        return "Tuesday"
    elif numb == 2:
        return "Wednesday"
    elif numb == 3:
        return "Thursday"
    elif numb == 4:
        return "Friday"
    elif numb == 5:
        return "Saturday"
    elif numb == 6:
        return "Sunday"

def buildWeeklies(table):
    # Create weekly table summing as needed
    weekly = table.groupby(['Year', 'Month', 'Week']).agg({
        "Distance_Miles":sum,
        "Duration_Hours":sum,
        "Vertical_Gain_Feet":sum,
        #"HR_Z1":sum,
        #"HR_Z2":sum,
        #"HR_Z3":sum,
        #"HR_Z4":sum,
        #"HR_Z5":sum,
        "Start_Time_Milli":min
    })
    weekly = weekly.sort_values(by=['Year', 'Month', 'Week'], ascending=False)
    #print(weekly.head())
    return weekly
