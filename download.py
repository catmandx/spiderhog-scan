# SuperFastPython.com
# download all files from a website sequentially
from os import makedirs
from os.path import basename
from os.path import join
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
import requests
from url_normalize import url_normalize
 
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# load a file from a URL, returns content of downloaded file
def download_url(urlpath):
    return requests.get(urlpath, verify=False).text
    # print(urlpath)
    # # open a connection to the server
    # with urlopen(urlpath) as connection:
    #     # read the contents of the url as bytes and return it
    #     return connection.read()
 
# decode downloaded html and extract all <a href=""> links
# def get_urls_from_html(content):
#     # decode the provided content as ascii text
#     html = content.decode('utf-8')
#     # parse the document as best we can
#     soup = BeautifulSoup(html, 'html.parser')
#     # find all all of the <a href=""> tags in the document
#     atags = soup.find_all('a')
#     # get all href values (links) or None if not present (unlikely)
#     return [t.get('href', None) for t in atags]
 
# save provided content to the local path
def save_file(path, data):
    # open the local file for writing
    with open(path, 'wb') as file:
        # write all provided data to the file
        # file.writelines(data)
        file.write(str.encode(data))
 
# download one file to a local directory
def download_url_to_file(url, link, path, index_text):
    # skip bad urls or bad filenames
    if link is None or link == '../' or 'vendors' in link:
        return (link, None)
    # check for no file extension
    if link == url: #index.html
        absurl = url
        filename = 'index.html'
    elif not (link[-4] == '.' or link[-3] == '.' ):
        print (link)
        return (link, None)
    else:
        # convert relative link to absolute link
        absurl = url_normalize(urljoin(url, link))
        # get the filename
        filename = basename(absurl)
    # download the content of the file
    data = download_url(absurl)
    if data == index_text and link != url:
        return (link, None)
    # construct the output path
    outpath = join(path, filename)
    # save to file
    save_file(outpath, data)
    # return results
    return (link, outpath)
 
# download all files on the provided webpage to the provided path
def download_all_files(url, prefix, links, index_text):
    # download the html webpage
    #data = download_url(url)
    # create a local directory to save files
    path = "raw/" + urlparse(url).netloc + "/js"
    makedirs(path, exist_ok=True)
    # parse html and retrieve all href urls listed
    #links = get_urls_from_html(data)
    
    # report progress
    print(f'Found {len(links)} links in {url}')
    # create the pool of worker threads
    with ThreadPoolExecutor(max_workers=20) as exe:
        # dispatch all download tasks to worker threads
        futures = [exe.submit(download_url_to_file, url, link, path, index_text) for link in links]
        # report results as they become available
        for future in as_completed(futures):
            # retrieve result
            link, outpath = future.result()
            # check for a link that was skipped
            # if outpath is None:
            #     print(f'>skipped {link}')
            # else:
            #     print(f'Downloaded {link} to {outpath}')
 
# url of html page that lists all files to download
# URL = 'https://www.quaddicted.com/files/idgames2/quakec/bots/'
# local directory to save all files on the html page
# PATH = 'tmp'
# download all files on the html webpage
#download_all_files(URL, PATH, links)