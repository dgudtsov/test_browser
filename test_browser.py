'''

@author: Denis
'''
import csv
import time
from selenium import webdriver

import json
import re

log_file = None

### Constants

# path where chromedriver is installed 
chromedriver = '/home/denis/soft/webdriver/chromedriver'

# source file with url list
file_url_list = './file_url_list_test.txt'

# output file with csv
results_csv = './csv.csv'

# log file with chromedriver network performance if defined
#log_file = 'log.log'

### end constants

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from selenium.webdriver.ChromeOptions import *
#from selenium.webdriver.Chrome import *

d = DesiredCapabilities.CHROME
d['loggingPrefs'] = { 'performance':'ALL' }

DATA_LENGTH_REGEX = r"encodedDataLength\":(.*?),"

#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from selenium.webdriver.ChromeOptions import *
#from selenium.webdriver.Chrome import *

#profile = webdriver.ChromeOptions()
#profile.set_capability("", False)

#capabilities = DesiredCapabilities.CHROME()
#capabilities.setCapability(CapabilityType.ForSeleniumServer.ENSURING_CLEAN_SESSION, true)
# dc.setCapability(CapabilityType.SUPPORTS_APPLICATION_CACHE, false);


driver = webdriver.Chrome(chromedriver,desired_capabilities=d)  # Optional argument, if not specified will search path.


url_list=list()
with open(file_url_list, 'r') as f1:
    for line in f1:
        url_list.append(line.rstrip('\n'))
    f1.closed


with open(results_csv, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';')
#                            quotechar='', quoting=csv.QUOTE_MINIMAL)
    
    csvwriter.writerow(['url','navigationStart','responseStart','domComplete','backendPerformance','frontendPerformance','full','time_before_screen','time_after_screen','bytes_recv'])

    for url in url_list:
    
        print "Navigating: %s" % url
    
        start_time = time.time()
        
        driver.get(url)
        
        performance = driver.get_log('performance')
 
        total_bytes = []

        try:
            for entry in performance:
                entry = str(entry)
                if "Network.dataReceived" in entry:
                    r = re.search(DATA_LENGTH_REGEX, entry)
                    total_bytes.append(int(r.group(1)))
        except Exception:
            print "Error!"
        
        if total_bytes is not None:
            bytes_recv = sum(total_bytes)
            mbytes_recv = round((float(bytes_recv / 1024) / 1024), 2)
        
#        pp = pprint.PrettyPrinter(indent=4)
#        pp.pprint(driver.get_log('performance'))
        
        perf_time1 = performance[0]['timestamp']
        perf_time2 = performance[-1]['timestamp']
        
#        print perf_time2 - perf_time1
        
        print "Page size, mb: %s" % mbytes_recv 
        
#        if __debug__:
        if log_file is not None:
            with open(log_file,'wb') as logf:
                logf.write( json.dumps(performance, indent=1) )
        
        navigationStart = driver.execute_script("return window.performance.timing.navigationStart")    
        responseStart = driver.execute_script("return window.performance.timing.responseStart")
        domComplete = driver.execute_script("return window.performance.timing.domComplete")
        
        
        #driver.manage().timeouts().implicitlyWait()
        time1 = (time.time() - start_time)
        
#        print("--- %s seconds ---" % time1)
        
        driver.get_screenshot_as_file('/tmp/1.png')
        
        time2 = (time.time() - start_time)
        
#        print("--- %s seconds ---" % time2)
        
        backendPerformance = responseStart - navigationStart
        frontendPerformance = domComplete - responseStart
        
        full = domComplete - navigationStart
        
    #    print "Back End: %s" % backendPerformance
    #    print "Front End: %s" % frontendPerformance
        
        print "Full time page load, ms: %s" % full
        
        csvwriter.writerow([url, str(navigationStart), str(responseStart), str(domComplete), str(backendPerformance), str(frontendPerformance), str(full), str(time1), str(time2), str(bytes_recv) ])
#        print ';'.join([url, str(navigationStart), str(responseStart), str(domComplete), str(backendPerformance), str(frontendPerformance), str(full), str(time1), str(time2) ])
    #    print i+";"+navigationStart+";"+responseStart+";"+domComplete+";"+backendPerformance+";"+";"+frontendPerformance+";"
        
        # time.sleep(5) # Let the user actually see something!
        #time.sleep(5) # Let the user actually see something!

driver.quit()
