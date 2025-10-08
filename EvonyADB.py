import os
import subprocess
import cv2
import pytesseract
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from ppadb.client import Client as AdbClient
from PyQt5.QtWidgets import QMessageBox
import sys
import shutil  # for file operations like copy and move

def show_styled_message(parent, msg_type, title, message):
    """Show a message box with consistent dark theme styling"""
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(message)
    
    # Apply dark theme styling to match main application
    msgBox.setStyleSheet("""
        QMessageBox {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            border: 2px solid #008080;
            border-radius: 8px;
        }
        QMessageBox QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            text-align: center;
            font-size: 10pt;
            font-weight: bold;
            border-radius: 8px;
            min-width: 80px;
            min-height: 30px;
            padding: 5px;
        }
        QMessageBox QPushButton:hover {
            background-color: #45a049;
        }
        QMessageBox QPushButton:pressed {
            background-color: #3d8b40;
        }
        QMessageBox QLabel {
            color: #ffffff;
            font-size: 10pt;
            margin: 10px;
        }
    """)
    
    # Set appropriate icon based on message type
    if msg_type.lower() == 'warning':
        msgBox.setIcon(QMessageBox.Warning)
    elif msg_type.lower() == 'error':
        msgBox.setIcon(QMessageBox.Critical)
    elif msg_type.lower() == 'information':
        msgBox.setIcon(QMessageBox.Information)
    elif msg_type.lower() == 'question':
        msgBox.setIcon(QMessageBox.Question)
    
    return msgBox.exec_()

class EvonyADB():
    objClient = None  # Global class variable
    objScreenshot = None    # current screenshot
    objOldScreenshot = None  # previous screenshot for comparison
    objManageImage = None  # Instance of ManageImage class

    strEmulatorName = None
    strScreenshotFilename = None
    strOldScreenshotFilename = None
    strEvonyPackageName = "com.topgamesinc.evony" # executable name on android platform
    strDeviceID = None  # will contain the selected device for connection:  serial number for USB, port for BlueStack

    def __init__(self, objManageImage):
        
        if __debug__:
            print(f"EvonyADB initialized with emulator name: {self.strEmulatorName}")

        self.objManageImage = objManageImage  # Assign the passed ManageImage instance

        # Restart ADB server to ensure it's running
        subprocess.run(['adb', 'kill-server'], check=True)
        subprocess.run(['adb', 'start-server'], check=True)
        # Open the adb server connection
        try:
            EvonyADB.objClient = AdbClient(host='localhost', port=5037)
            if __debug__:
                print("Connected to ADB Server")
        except Exception as excError:
            print(f"Error connecting to AdbClient: {excError}")
            show_styled_message(None, "error", "ADB Connection Error", "Unable to connect to the ADB server. Please ensure ADB is installed and running.")

        config_dir = os.path.dirname(os.path.abspath(__file__))
        self.strScreenshotFilename = os.path.join(config_dir, "screenshot.png")
        self.strOldScreenshotFilename = os.path.join(config_dir, "old.screenshot.png")
        
        # Check if screenshot.png exists, if not create an empty file
        if not os.path.exists(self.strScreenshotFilename):
            if __debug__:
                print(f"Creating new screenshot file at {self.strScreenshotFilename}")
            with open(self.strScreenshotFilename, 'wb') as file:
                pass

    def CheckDeviceConnection(self):
        """Check if ADB server is running and the BlueStacks 5 device is running and accessible via ADB"""
        try:
            if not self.strDeviceID:
                if __debug__:
                    print("No device ID specified")
                return False
            
            # First check if ADB server is running
            try:
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    if __debug__:
                        print("ADB server is not running or not responding")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                if __debug__:
                    print(f"ADB command failed: {e}")
                return False
            
            # Check if ADB client connection is still valid
            if not EvonyADB.objClient:
                if __debug__:
                    print("ADB client not initialized")
                return False
                
            # Get list of connected devices
            try:
                devices = EvonyADB.objClient.devices()
            except Exception as e:
                if __debug__:
                    print(f"Failed to get device list from ADB client: {e}")
                # Try to reconnect ADB client
                try:
                    EvonyADB.objClient = AdbClient(host='localhost', port=5037)
                    devices = EvonyADB.objClient.devices()
                except Exception as reconnect_error:
                    if __debug__:
                        print(f"Failed to reconnect ADB client: {reconnect_error}")
                    return False
            
            # Convert port to emulator serial format
            # BlueStacks uses port-1 for ADB (e.g., 5555 becomes emulator-5554)
            intSelectedPort = int(self.strDeviceID)
            intMatchingPort = self.FindInstanceByPort(intSelectedPort)
            
            if intMatchingPort:
                strExpectedSerial = f"emulator-{intMatchingPort}"
                if __debug__:
                    print(f"Looking for emulator serial: {strExpectedSerial} (from port {self.strDeviceID})")
                
                # Check if our converted device serial is in the list of connected devices
                for device in devices:
                    if device.serial == strExpectedSerial:
                        if __debug__:
                            print(f"BlueStacks device {strExpectedSerial} is running and connected")
                        return True
                        
                if __debug__:
                    print(f"BlueStacks device {strExpectedSerial} is not running or not connected")
                    print(f"Available devices: {[device.serial for device in devices]}")
                return False
            else:
                if __debug__:
                    print(f"No matching BlueStacks instance found for port {self.strDeviceID}")
                return False
            
        except Exception as e:
            if __debug__:
                print(f"Error checking device connection: {e}")
            return False

    def GetBluestacksAdbPort(self):
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        for strLine in result.stdout.splitlines():
            if strLine.startswith('emulator-'):
                strSerial = strLine.split('\t')[0]
                try:
                    self.strEmulatorName = strSerial
                    return int((strSerial.split('-')[1]))
                except (IndexError, ValueError):
                    continue
        return None

    def FindInstanceByPort(self, intSelectedPort):
        intPort = self.GetBluestacksAdbPort()
        if intPort in [intSelectedPort, intSelectedPort - 1]:
            if __debug__:
                print(f"Found BlueStacks instance where selected port is: {intSelectedPort} and adb port: {intPort}")
            return intPort
        return None

    def GetScreenshot(self):
        # first move screenshot.png to old.screenshot.png
        try:
            if self.objScreenshot:
                self.objOldScreenshot = self.objScreenshot.copy()

                if __debug__:
                   print(f"Moving current screenshot to old screenshot: {self.strScreenshotFilename}")    
                
                shutil.copyfile(self.strScreenshotFilename, self.strScreenshotFilename)
            else:
                if __debug__:
                    print("No existing screenshot to move to old screenshot")
                # delete old screenshot if it exists
                if os.path.exists(self.strOldScreenshotFilename):
                    os.remove(self.strOldScreenshotFilename)
        except Exception as e:
            if __debug__:
                    print(f"Error moving screenshot to old screenshot: {e}")

        # now capture new screenshot
        captureCommand = ["adb", "-s", self.strEmulatorName, "shell", "screencap", "-p"]
        try:
            result = subprocess.run(captureCommand, capture_output=True, check=True)
            data = result.stdout.replace(b'\r\n', b'\n')
            
            with open(self.strScreenshotFilename, "wb") as fileScreenshot:
                fileScreenshot.write(data)
            self.objScreenshot = cv2.imread(self.strScreenshotFilename)
            if __debug__:
                print(f"Screenshot saved to {self.strScreenshotFilename}")
            
            if __debug__:
                print(f"Screenshot dimensions: {self.objScreenshot.shape[1]}x{self.objScreenshot.shape[0]}") # (width, height, channels)
                print("Screenshot captured successfully")
                # Display the screenshot using matplotlib (disabled to prevent Figure 1 dialog)
                # plt.imshow(cv2.cvtColor(self.objScreenshot, cv2.COLOR_BGR2RGB))
                # plt.axis('on')
                # plt.show()

        except subprocess.CalledProcessError as e:
            if self.objScreenshot is None or self.objScreenshot.size == 0:
                print("Error: Screenshot is empty or could not be read: {e}")
                return False
        
        return True
        

    def CheckAndStartApp(self):
        if __debug__:
            print("CheckAndStartApp")
        # Check if the app is running (assuming adb_path is a safe path to adb)
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq HD-Player.exe'],
                capture_output=True, text=True, check=True
            )
        except Exception as e:
            if __debug__:
                print(f"Error checking BlueStacks process: {e}")
            show_styled_message(None, "warning", "Warning", "Please start Bluestacks and start Evony")
            return False

        if __debug__:
            print("HD-Player.exe is running")
        # If multiple bluestacks instances are found, determine which matches the selected port
        intSelectedPort = int(self.strDeviceID)
        
        intMatchingPort = self.FindInstanceByPort(intSelectedPort)
        self.strEmulatorName = f"emulator-{str(intMatchingPort)}"
        
        if __debug__:
            if intMatchingPort:
                print(f"BlueStacks instance for port {intSelectedPort} has serial: {intMatchingPort}")
            else:
                print(f"No BlueStacks instance found for port {intSelectedPort}")
        # Bluestacks instance found
        check_command = [
            "adb",
            "-s",
            self.strEmulatorName,
            "shell",
            "ps",
        ]
        try:
            # Check if the app is running
            result = subprocess.run(check_command, capture_output=True, check=True)
            output = result.stdout.decode()
        except Exception as e:
            print(f"Error during check if Evony is running with the selected port id: {e}")
        # Now filter for your package name in Python
        if self.strEvonyPackageName in output:
            if __debug__:
                print(f"{self.strEvonyPackageName} is running")
        else:
            if __debug__:
                print(f"{self.strEvonyPackageName} is not running")
            # If the app is not running, start it
            # Start the app using the monkey command
            start_command = ["adb", "-s", self.strEmulatorName, "shell", "monkey", "-p", self.strEvonyPackageName, "-c", "android.intent.category.LAUNCHER", "1"]
            try:
                subprocess.run(start_command, check=True)
                print(f"{self.strEvonyPackageName} started successfully")
            except subprocess.CalledProcessError:
                print(f"Error starting {self.strEvonyPackageName}")
                return False
        
        #assume app is now running, ready for screen capture
        # Capture the screenshot to local file, adb only allows saving to the emulator
        if self.GetScreenshot() == True:
            return True

        if __debug__:
            print("Error capturing screenshot")

        return False

    def ClickLocation(self, strDeviceID, strLocation):
        if __debug__:
            print(f"ClickLocation called with DeviceID: {strDeviceID}, Location: {strLocation}")
        tupXMLData = self.objManageImage.GetXMLData(strLocation, self.objScreenshot)
        (boolFound, x1, y1, x2, y2, click_and_drag) = tupXMLData

        if boolFound:
            if not click_and_drag:
                # For a simple click, we just need the coordinates, and add 10 to x and y to ensure the click is within the button area
                x1 += 10
                y1 += 10
                click_command = ["adb", "-s", strDeviceID, "shell", "input", "tap", str(x1), str(y1)]
                subprocess.run(click_command)
            else:
                # executing a SWIPE
                drag_command = ["adb", "-s", strDeviceID, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2)]
                subprocess.run(drag_command)
                    
        return True