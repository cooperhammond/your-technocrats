import time
import os
import subprocess
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from fastai.vision import *


CHROME_DRIVER_LOC = r'C:\Users\C23Cooper.Hammond\Documents\dev\bin\chromedriver.exe'


class ContentGrabber:

    def __init__(self, classes, queries, destination, blocks=4):
        self.classes = classes
        self.queries = queries
        self.destination = Path(destination)
        self.blocks = blocks

        self.wsl_folder = subprocess.check_output('wslpath "%s"' % self.destination, shell=True).decode('utf-8').strip("\n")

        root_url = 'https://www.google.com/search?tbm=isch&'
        self.image_url_queries = []
        for query in queries:
            url = root_url + urlencode({'q': query})
            self.image_url_queries.append(url)

    def grab_images(self):
        self.grab_urls()        
        
        ## DOWNLOAD IMAGES ##
        for c in self.classes:
            print(c)
            class_data_dest = Path(self.wsl_folder + "/" + c)
            class_data_dest.mkdir(parents=True, exist_ok=True)
            download_images(self.wsl_folder + ('/%s.csv' % c), class_data_dest)

        for c in self.classes:
            print(c)
            verify_images(Path(self.wsl_folder + "/" + c), delete=True, max_size=1000)

    def grab_urls(self):
        get_image_urls_script = \
            "urls=Array.from(document.querySelectorAll('.rg_i')).map(el=> el.hasAttribute('data-src')?el.getAttribute('data-src'):el.getAttribute('data-iurl'));" + \
            "\n" + "window.open('data:text/csv;charset=utf-8,' + escape(urls.join('\\n')));"

        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'download.default_directory' : str(self.destination)})

        os.system('cmd.exe /c "%s" &' % CHROME_DRIVER_LOC) # spawns chromedrive instance

        driver = webdriver.Chrome(port=9515, options=options)

        for url in self.image_url_queries:
            driver.get(url)
            for i in range(0, self.blocks):
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                time.sleep(2)
            driver.execute_script(get_image_urls_script)

        time.sleep(2)
        driver.quit()

        ## RENAME URL FILES ##
        for index, c in enumerate(self.classes):
            filename = 'download'
            if index > 0:
                filename += ' (%s)' % index
            os.rename(self.wsl_folder + '/%s' % filename, 
                      self.wsl_folder + '/%s.csv' % c)
            index += 1


def main():
    downloads_folder = r'C:\Users\C23Cooper.Hammond\Documents\dev\Learning\fast.ai\pizza-pundit\data'

    classes = [
        'hamburger',
        'sandwich',
        'pizza'
    ]
    queries = [
        '"hamburger" -sandwich',
        '"sandwich" -hamburger',
        '"pizza"'
    ]

    g = ContentGrabber(classes, queries, downloads_folder)
    g.grab_images()
    

if __name__ == "__main__":
    main()