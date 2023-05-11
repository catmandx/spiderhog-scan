from multiprocessing import Lock, Process, Queue, current_process
import time
import queue
from urllib.parse import urlparse # imported for using queue.Empty exception
import helpers
import requests
import download
from subprocess import run, check_output
from url_normalize import url_normalize
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


debug = False

def scan_site(sites_to_scan, sites_scanned, sites_no_results):
    global no_result
    session = requests.Session()
    session.headers.update({'User-Agent': 'YOUR_USER_AGENT'})
    
    while True:
        try:
            site = sites_to_scan.get_nowait() 
            print("Start site:", site)
            if debug: print("+++++++Scanning++++++++ ", site)
            index_text = session.get(site, verify=False).text

            js_files = []
            js_files.append(site)
            (prefix, app_js) = helpers.extract_app_js_from_index(index_text) # prefix: /assets, /static/js, /js | app_js : file name
            if not app_js:
                sites_no_results.put(site)
                continue
            
            js_files.append(str(prefix) + app_js)
            if 'app' in app_js: #vue? 
                js_files = js_files + helpers.extract_js_from_index_vue_like(index_text)

                if app_js:
                    app_js_text = session.get(url_normalize(site + prefix + app_js), verify=False).text
                    list_js2 = helpers.extract_js_from_app(app_js_text)
                    js_files= js_files + list_js2
                
            elif 'main' in app_js and 'chunk' in app_js: #webpackJsonplearn-reactjs
                js_files = js_files + helpers.extract_js_from_index_react_like_chunk(prefix, index_text)
                

            elif 'main' in app_js and 'chunk' not in app_js:
                (_prefix, runtime_js) = helpers.extract_runtime_js_from_index(index_text)
                if runtime_js:
                    runtime_js_text = session.get(url_normalize(site + _prefix + runtime_js), verify=False).text
                    list_js2 = helpers.extract_js_from_runtime(prefix, runtime_js_text)
                    js_files= js_files + list_js2
            elif 'index' in app_js: 
                app_js_text = session.get(url_normalize(site + prefix + app_js), verify=False).text
                js_files = js_files + helpers.extract_js_from_index_index_like(prefix, app_js_text) #/assets/, index
            
            if debug: print("List for ",site," before dedup:", js_files)
            js_files = list(dict.fromkeys(js_files))
            if debug: print("List for ",site," after dedup:", js_files)
            download.download_all_files(site, prefix, js_files, index_text)
            if debug: print("Downloaded all files for ", site, ". Running trufflehog:")
            p = check_output( '.\\trufflehog.exe --no-update --config=trufflehogconf.yaml filesystem ' + "raw/" + urlparse(site).netloc + "/js"  )
        
            if p:
                with open("results/"+urlparse(site).netloc+".txt", 'wb') as file:
                    # write all provided data to the file
                    file.write(p)
        except queue.Empty:
            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            sites_scanned.put(site + ' is done by ' + current_process().name)
            time.sleep(.5)
    return True


def main():
    number_of_processes = 8
    sites_to_scan = Queue()
    sites_scanned = Queue()
    sites_no_results = Queue()
    processes = []
    file1 = open('toscan.txt', 'r')
    Lines = file1.readlines()
    for line in Lines:
        sites_to_scan.put(line.strip())

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=scan_site, args=(sites_to_scan, sites_scanned, sites_no_results))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not sites_scanned.empty():
        print(sites_scanned.get())

    while not sites_no_results.empty():
        print(sites_no_results.get())
    return True


if __name__ == '__main__':
    main()