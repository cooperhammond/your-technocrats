import time
import os
import subprocess
from urllib.parse import urlencode

from fastai.vision import *
from selenium import webdriver


CHROME_DRIVER_LOC = r'C:\Users\C23Cooper.Hammond\Documents\dev\bin\chromedriver.exe'


class ContentGrabber:

    def __init__(self, classes, queries, destination):
        self.classes = classes
        self.queries = queries
        self.destination = Path(destination)

        root_url = 'https://www.google.com/search?tbm=isch&'
        self.image_url_queries = []
        for query in queries:
            url = root_url + urlencode({'q': query})
            self.image_url_queries.append(url)

    def grab_images(self):
        get_image_urls_script = "urls=Array.from(document.querySelectorAll('.rg_i')).map(el=> el.hasAttribute('data-src')?el.getAttribute('data-src'):el.getAttribute('data-iurl'));" + \
                                "\n" + "window.open('data:text/csv;charset=utf-8,' + escape(urls.join('\\n')));"

        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'download.default_directory' : str(self.destination)})

        ## GRAB URLS ##
        os.system('cmd.exe /c "%s" &' % CHROME_DRIVER_LOC) # spawns chromedrive instance

        driver = webdriver.Chrome(port=9515, options=options)

        for url in self.image_url_queries:
            driver.get(url)
            driver.execute_script(get_image_urls_script)

        time.sleep(2)
        driver.quit()

        ## RENAME URL FILES ##
        wsl_downloads_folder = subprocess.check_output('wslpath "%s"' % self.destination, shell=True).decode('utf-8').strip("\n")
        for index, c in enumerate(self.classes):
            filename = 'download'
            if index > 0:
                filename += ' (%s)' % index
            os.rename(wsl_downloads_folder + '/%s' % filename, 
                      wsl_downloads_folder + '/%s.csv' % c)
            index += 1
        
        ## DOWNLOAD IMAGES ##
        for c in self.classes:
            print(c)
            class_data_dest = Path(wsl_downloads_folder + "/" + c)
            class_data_dest.mkdir(parents=True, exist_ok=True)
            download_images(wsl_downloads_folder + ('/%s.csv' % c), class_data_dest)

        for c in self.classes:
            print(c)
            verify_images(Path(wsl_downloads_folder + "/" + c), delete=True, max_size=1000)


def main():
    downloads_folder = r'C:\Users\C23Cooper.Hammond\Documents\dev\Learning\fast.ai\pizza-pundit\data'

    classes = [
        'hamburger',
        'sandwich',
        'pizza'
    ]
    queries = [
        'hamburger',
        'sandwich',
        'pizza'
    ]

    g = ContentGrabber(classes, queries, downloads_folder)
    g.grab_images()
    

if __name__ == "__main__":
    main()