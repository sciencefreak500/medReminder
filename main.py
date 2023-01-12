import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

alarm_time = None
interval = None
future_times = None
am_pm = None
first_run = True

def set_alarm():
    global alarm_time
    global future_times
    global interval
    global am_pm
    hour = int(hour_var.get())
    minute = int(minute_var.get())
    am_pm = am_pm_var.get()
    if am_pm == "PM" and hour != 12:
        hour += 12
    elif am_pm == "AM" and hour == 12:
        hour = 0
    alarm_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    print('alarm time is: ', alarm_time.strftime("%m/%d/%Y %H:%M:%S"))
    interval = int(interval_entry.get())

    # write the alarm time to a file
    with open("alarm_config.json", "w") as f:
        # save datetime as a string, full month/day/year hour:minute:second
        alarm_dict = {
            "alarm_time": alarm_time.strftime("%m/%d/%Y %H:%M:%S"),
            "am_pm": am_pm, 
            "interval": interval
        }
        json.dump(alarm_dict, f)
    # start alarm clock
    future_times = get_next_times(alarm_time, int(interval))
    
    current_time = datetime.now()
    current_time = current_time.replace(second=0, microsecond=0)
    if alarm_time < current_time:
        messagebox.showinfo("Warning", "Alarm time is in the past, updating to next alarm time")
        alarm_time = find_next_alarm_time()
    alarm()
    

# get the next 24 alarm times based on the interval using timedelta
def get_next_times(alarm_time, interval):
    times = set()
    current_time = alarm_time
    current_time = current_time.replace(second=0, microsecond=0)
    times.add(current_time)
    for i in range(100):
        current_time += timedelta(minutes=interval)
        current_time = current_time.replace(second=0, microsecond=0)
        times.add(current_time)
    # return a list of the times sorted by time
    result = sorted(times)
    print('future times are: ', [time.strftime("%m/%d/%Y %H:%M:%S") for time in result])
    return result

def find_next_alarm_time():
    global future_times
    global alarm_time
    current_time = datetime.now()
    current_time = current_time.replace(second=0, microsecond=0)
    for time in future_times:
        check_first_run = time > current_time if first_run else time >= current_time
        if check_first_run:
            alarm_time = time
            break
    print('next alarm time is: ', alarm_time.strftime("%m/%d/%Y %H:%M:%S"))
    return alarm_time


# check if its alarm time, if not tkinter will wait 60 seconds and check again
def alarm():
    global alarm_time
    global interval
    global future_times
    global am_pm
    global first_run
    if alarm_time is None or interval is None:
        # read the alarm time from the file
        with open("alarm_config.json", "r") as f:
            alarm_dict = json.load(f)
            alarm_time = datetime.strptime(alarm_dict["alarm_time"], "%m/%d/%Y %H:%M:%S")
            alarm_time = alarm_time.replace(second=0, microsecond=0)
            am_pm = alarm_dict["am_pm"]
            interval = alarm_dict["interval"]
            future_times = get_next_times(alarm_time, interval)
            alarm_time = find_next_alarm_time()
    

    print('alarm time is: ', alarm_time.strftime("%m/%d/%Y %H:%M:%S"))
    print('interval is: ', interval)

    current_time = datetime.now()
    current_time = current_time.replace(second=0, microsecond=0)
    print('current time is: ', current_time)

    
    
    # check the time, if its not the alarm time, wait 60 seconds and check again
    if current_time == alarm_time:
        # os.system("start alarm.mp3")
        messagebox.showinfo("Alarm", "Wake up!")
        alarm_time = find_next_alarm_time()
        alarm_time = alarm_time.replace(second=0, microsecond=0)
        # write new time to config
        with open("alarm_config.json", "w") as f:
            # save datetime as a string, full month/day/year hour:minute:second
            alarm_dict = {
                "alarm_time": alarm_time.strftime("%m/%d/%Y %H:%M:%S"),
                "am_pm": am_pm, 
                "interval": interval
            }
            json.dump(alarm_dict, f)
        future_times = get_next_times(alarm_time, interval)
        alarm_time_label.config(text=alarm_time.strftime("%m/%d/%Y %H:%M:%S"))
    first_run = False
    root.after(1_000, alarm) # check per minute

root = tk.Tk()
root.title("Alarm Clock")
root.geometry("250x200")


start_time_label = tk.Label(root, text="Start Time (12-hour):")
start_time_label.grid(row=0, column=0, columnspan=2)

# Create hour drop-down menu
hour_var = tk.StringVar()
hour_var.set("12")  # Set the default value to 12
hour_dropdown = tk.OptionMenu(root, hour_var, *range(1, 13))
hour_dropdown.grid(row=1, column=0)

# Create minute drop-down menu
minute_var = tk.StringVar()
minute_var.set("00")  # Set the default value to 00
minute_dropdown = tk.OptionMenu(root, minute_var, *["{:02d}".format(i) for i in range(60)])
minute_dropdown.grid(row=1, column=1)

# Create AM/PM drop-down menu
am_pm_var = tk.StringVar()
am_pm_var.set("AM")  # Set the default value to AM
am_pm_dropdown = tk.OptionMenu(root, am_pm_var, "AM", "PM")
am_pm_dropdown.grid(row=1, column=2)

interval_label = tk.Label(root, text="Interval (hours):")
interval_label.grid(row=2, column=0)
interval_entry = tk.StringVar()
interval_entry.set("1")  # Set the default value to 1
interval_dropdown = tk.OptionMenu(root, interval_entry, *range(1, 13))
interval_dropdown.grid(row=2, column=1)

start_button = tk.Button(root, text="Start", command=set_alarm)
start_button.grid(row=3, column=0)

alarm_time_label = tk.Label(root, text="")
alarm_time_label.grid(row=4, column=0)

# read the alarm time from the file and set the alarm time default values to it
if os.path.exists("alarm_config.json"):
    with open("alarm_config.json", "r") as f:
        alarm_dict = json.load(f)
        alarm_time = datetime.strptime(alarm_dict["alarm_time"], "%m/%d/%Y %H:%M:%S")
        am_pm = alarm_dict["am_pm"]
        interval = alarm_dict["interval"]
        hour_var.set(alarm_time.strftime("%I"))
        minute_var.set(alarm_time.strftime("%M"))
        am_pm_var.set(am_pm)
        interval_entry.set(interval)
        alarm_time_label.config(text=alarm_time.strftime("%m/%d/%Y %H:%M:%S"))

root.mainloop()
