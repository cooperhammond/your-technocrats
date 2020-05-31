import time
import os
import subprocess
import platform
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from fastai.vision import *


CHROME_DRIVER_LOC = r'C:\Users\C23Cooper.Hammond\Documents\dev\bin\chromedriver.exe'
IMAGE_URLS_SCRIPT = \
    "urls=Array.from(document.querySelectorAll('.rg_i')).map(el=> el.hasAttribute('data-src')?el.getAttribute('data-src'):el.getAttribute('data-iurl'));" + \
    "\n" + "window.open('data:text/csv;charset=utf-8,' + escape(urls.join('\\n')));"
ON_WSL = "microsoft" in platform.uname()[3].lower()


class ImageAggregator:

    def __init__(self, classes, query_sets, destination, blocks=4):
        self.classes = classes
        self.sys_destination = Path(destination)
        self.python_dest = self.sys_destination
        self.blocks = blocks

        if ON_WSL:
            self.python_dest = Path(
                subprocess.check_output(
                    'wslpath "%s"' % self.sys_destination, 
                    shell=True
                        ).decode('utf-8').strip("\n"))

        gimages_url = 'https://www.google.com/search?tbm=isch&'
        self.image_url_sets = []
        for query_set in query_sets:
            url_set = []
            for query in query_set:
                url = gimages_url + urlencode({'q': query})
                url_set.append(url)
            self.image_url_sets.append(url_set)

    def grab_urls(self):
        # automatically download files to the specified folder
        opts = webdriver.ChromeOptions()
        opts.add_experimental_option('prefs', {
            'download.default_directory' : str(self.sys_destination)
        })
        driver = webdriver.Chrome

        if ON_WSL:
            # spawns chromedriver instance on WSL
            os.system('cmd.exe /c "%s" &' % CHROME_DRIVER_LOC)
            # default port (always used) for chromedriver is 9515
            driver = webdriver.Chrome(port=9515, options=opts)
        else:
            driver = webdriver.Chrome(CHROME_DRIVER_LOC, options=opts)


        for index, url_set in enumerate(self.image_url_sets):

            for url in url_set:
                # open up url
                driver.get(url)
                
                # this loop will scroll down the page and force more images to load.
                # usually can grab ~350 images compared to the 80 grabbed from not scrolling
                for i in range(0, self.blocks):
                    html = driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    time.sleep(2)

                # download image urls
                driver.execute_script(IMAGE_URLS_SCRIPT)

                # following snippet will rename the downloaded urls from "download" to 
                # <corresponding-class>.csv
                current_filename = self.python_dest/'download'
                target_filename = self.python_dest/(self.classes[index] + '.csv')
                # if a target class has already downloaded a url set, append
                # the urls to the last file
                if os.path.exists(target_filename):
                    while not os.path.exists(current_filename):
                        time.sleep(0.1)
                    file_in = open(current_filename, 'r')
                    file_out = open(target_filename, 'a')
                    for line in file_in:
                        file_out.write(line)
                    file_out.close()
                    os.remove(current_filename)
                else:
                    while not os.path.exists(str(current_filename)):
                        print("this")
                        time.sleep(0.1)
                    os.rename(current_filename, target_filename)

        time.sleep(2)
        driver.quit()

    def grab_images(self):
        for c in self.classes:
            print(c)
            image_dest = Path(self.python_dest/c)
            image_dest.mkdir(parents=True, exist_ok=True)
            download_images(self.python_dest/(c + '.csv'), image_dest)
            verify_images(Path(self.python_dest/c), delete=True, max_size=1000)

    def do_it(self):
        self.grab_urls()
        self.grab_images()


def main():
    downloads_folder = r'C:\Users\C23Cooper.Hammond\Documents\dev\Learning\fast.ai\pizza-pundit\data'

    classes = [
        'elon-musk',
        'tony-stark',
    ]
    query_sets = [
        ['elon musk', 'elon musk face'],
        ['tony stark', 'robert downey jr'],
    ]

    g = ImageAggregator(classes, query_sets, downloads_folder)
    g.do_it()
    

if __name__ == "__main__":
    main()