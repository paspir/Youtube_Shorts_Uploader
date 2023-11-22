import subprocess

def get_chromedriver_path():
    result = subprocess.run(['where', 'chromedriver.exe'], capture_output=True, text=True, shell=True)
    return result.stdout.strip()

chrome_driver_path = get_chromedriver_path()
print("ChromeDriver path:", chrome_driver_path)