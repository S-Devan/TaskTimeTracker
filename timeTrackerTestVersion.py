from win32gui import GetForegroundWindow
import datetime
import psutil
import time
import win32process
import pyuac
import wmi
import pythoncom
from threading import Thread, Lock

class Shared_Data:
    def __init__(self):
        self.process_time = 0
        self.lock = Lock()

shared_data = Shared_Data()
stop_thread = False

def getPlaytime(process_name):
    global stop_thread
    #while not stop_thread:
    specific_app = process_name
    timestamp = 0

    print("Tracking Time...\n")
    while True: 
        if stop_thread:
            return
        current_app = psutil.Process(win32process.GetWindowThreadProcessId(GetForegroundWindow())[1]).name().replace(".exe", "")
        if current_app == specific_app:
            if timestamp == 0:
                timestamp = int(time.time())
            else:
                with shared_data.lock:
                    shared_data.process_time += int(time.time()) - timestamp
                timestamp = int(time.time())
        else:
            timestamp = 0
        time.sleep(1)

compute_thread = None
process_name = None

def initialize():
    global process_name

    print("Process List: ")
    pythoncom.CoInitialize()
    processes = wmi.WMI()
    for process in processes.Win32_process():
        print(f"{process.ProcessId:<10} {process.Name}")

    if not process_name:
        process_name = input("Enter the process name: ")

def main_loop():
    global stop_thread
    global compute_thread
    global process_name

    choice = input("\n1: Start Tracking\n2: Print Time Spent\n3: Switch App\nelse: Exit\ninput: \n")
    
    if choice == "1":
        if compute_thread and compute_thread.is_alive():
            print("Already tracking time!")
        else: 
            compute_thread = Thread(target=getPlaytime, args=(process_name,))
            compute_thread.start()
    
    elif choice == "2":
        with shared_data.lock:
            print(f"Time spent on {process_name}: {shared_data.process_time} seconds")
    
    elif choice == "3":
        if compute_thread and compute_thread.is_alive():
            stop_thread = True  # Step 3: Set the stop flag
            print("Stopping the current thread...")
            compute_thread.join()  # Wait for the thread to finish
            print("Thread stopped!")
        process_name = input("Enter the new process name: ")
        shared_data.process_time = 0
        stop_thread = False  # Step 4: Reset the stop flag before starting a new thread
        compute_thread = Thread(target=getPlaytime, args=(process_name,))
        print("New App Selected!")
        #compute_thread.start()
        
    
    else:
        with shared_data.lock:
            print(shared_data.process_time)
        path = r"C:/Users/sdeva/Documents/TimeTracker/TimeTracker.txt"
        
        # Read current time from file and update it
        with open(path, "r") as read_time_file:
            new_file_content = ""
            current_time = 0
            new_line = ""
            for line in read_time_file:
                stripped_line = line.strip()
                if not stripped_line.isdigit():
                    new_line = stripped_line
                    new_file_content += new_line + "\n"
                if stripped_line.isdigit():
                    current_time = int(stripped_line)
                    print(f"Current Time: {current_time}")
                    new_line = stripped_line.replace(str(current_time), str(shared_data.process_time + current_time))
                    print(f"New Line: {new_line}")
                    new_file_content += new_line + "\n"
                    print(f"New File Content: {new_file_content}")

        # Write updated time to file
        with open(path, "w") as write_time_file:
            write_time_file.write(new_file_content)
            write_time_file.write("\n" + str(datetime.timedelta(seconds=int(current_time + shared_data.process_time))) + "\n")
        
        time.sleep(10)
        if compute_thread:
            compute_thread.join()
        exit(0)
    return 1

if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        print("Re-launching as admin!")
        pyuac.runAsAdmin()
    else:
        initialize()
        while main_loop():
            pass
