## First proper working version

from win32gui import GetForegroundWindow
import datetime
import psutil
import time
import win32process
import pyuac
from threading import Thread, Lock

class Shared_Data:
    def __init__(self):
        self.process_time = 0
        self.lock = Lock()


shared_data = Shared_Data()

def getPlaytime():
    specific_app = "Code"  # Change this to the target app [Code is just for testing]
    #process_time = 0
    timestamp = 0

    print("Tracking Time...\n")
    while True:
        current_app = psutil.Process(win32process.GetWindowThreadProcessId(GetForegroundWindow())[1]).name().replace(".exe", "")
        if current_app == specific_app:
            if timestamp == 0:
                timestamp = int(time.time())
            else:
                shared_data.process_time += int(time.time()) - timestamp
                timestamp = int(time.time())
            #print(f"Time spent on {specific_app}: {process_time} seconds")
        else:
            timestamp = 0
        time.sleep(1)

compute_thread = Thread(target=getPlaytime)

def main():
    choice = input("\n1: Start Tracking\n2.Print Time Spent\nelse: Exit\ninput: \n")
    
    if choice == "1":
        if compute_thread.is_alive():
            print("Already tracking time!")
        else: 
            compute_thread.start()
    
    elif choice == "2":
        print(f"Time spent on Code: {shared_data.process_time} seconds")
    
    else:
        print(shared_data.process_time)
        path = r"C:/Users/sdeva/OneDrive/Documents/Tracked Time/VSCode-TestTimeTracking.txt"
        
        # Read current time from file and update it
        read_time_file = open(path, "r")
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
                new_line = stripped_line.replace(str(current_time), str(shared_data.process_time+current_time))
                print(f"New Line: {new_line}")
                new_file_content += new_line +"\n"
                print(f"New File Content: {new_file_content}")
        read_time_file.close()

        # Write updated time to file
        write_time_file = open(path, "w")
        write_time_file.write(new_file_content)
        write_time_file.write("\n" + str(datetime.timedelta(seconds=int(current_time+shared_data.process_time))) + "\n")
        write_time_file.close()
        
        time.sleep(10)
        compute_thread.join()
        exit(0)
    return 1

if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        print("Re-launching as admin!")
        pyuac.runAsAdmin()
    else:
        while main():
            if not compute_thread.is_alive():
                break