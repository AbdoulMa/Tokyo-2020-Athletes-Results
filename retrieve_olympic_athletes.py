#!/usr/bin/env python3

import os
import re
import sys
import tarfile
import zipfile
from argparse import ArgumentParser
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

import pandas as pd

import csv
import psutil

IFRAME_CSS_SELECTOR = '.iframe-container>iframe'

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)

def check_exists_by_link_text(browser, linkText):
    try:
        sleep(1)
        browser.find_element_by_link_text(linkText)
    except NoSuchElementException:
        return False
    return True

def clickButton(browser, button):
    browser.execute_script("arguments[0].click()", button)


def check_gecko_driver():
    script_dir = os.path.dirname(os.path.abspath("__file__"))
    bin_dir = os.path.join(script_dir, 'bin')

    if sys.platform.startswith('linux'):
        platform = 'linux'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform == 'darwin':
        platform = 'mac'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-macos.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform.startswith('win'):
        platform = 'win'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-win64.zip'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver.exe')
        var_separator = ';'
    else:
        raise RuntimeError('Could not determine your OS')

    if not os.path.isdir(bin_dir):
        os.mkdir(bin_dir)

    if not os.path.isdir(local_platform_path):
        os.mkdir(local_platform_path)

    if not os.path.isfile(local_driver_path):
        print('Downloading gecko driver...', file=sys.stderr)
        data_resp = requests.get(url, stream=True)
        file_name = url.split('/')[-1]
        tgt_file = os.path.join(local_platform_path, file_name)
        with open(tgt_file, 'wb') as f:
            for chunk in data_resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(tgt_file, 'r') as f_zip:
                f_zip.extractall(local_platform_path)
        else:
            with tarfile.open(tgt_file, 'r') as f_gz:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(f_gz, local_platform_path)

        if not os.access(local_driver_path, os.X_OK):
            os.chmod(local_driver_path, 0o744)

        os.remove(tgt_file)

    if 'PATH' not in os.environ:
        os.environ['PATH'] = local_platform_path
    elif local_driver_path not in os.environ['PATH']:
        os.environ['PATH'] = local_platform_path + var_separator + os.environ['PATH']


def retrieve_athlete_informations(athlete_row) :
    row_blocks = athlete_row.select("td")
    name_block = row_blocks[0]
    name_block = name_block.select_one("a")
    athlete_name = name_block.select("span")[1].text
    athlete_country = row_blocks[1].select_one("a").text.split(";")[0].replace("\n","")
    athlete_sport = row_blocks[2].select_one("a").text.split(";")[0].replace("\n","")
    athlete_link = name_block["href"].replace("../../..","https://olympics.com/tokyo-2020/olympic-games")
    athlete_dico  = {}
    athlete_dico["name"] = athlete_name
    athlete_dico["country"] = athlete_country
    athlete_dico["discipline"] = athlete_sport
    athlete_dico["link"] = athlete_link
    return athlete_dico

if __name__ == '__main__':

    check_gecko_driver()

    # Firefox Options and Profils
    ff_options = FirefoxOptions()
    ff_options.add_argument('--headless')
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    firefox_profile.set_preference('dom.disable_beforeunload', True)
    firefox_profile.set_preference('browser.tabs.warnOnClose', False)
    firefox_profile.set_preference('media.volume_scale', '0.0')
    driver = webdriver.Firefox(options=ff_options, firefox_profile=firefox_profile)
    driver.get('https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/athletes.htm')
    sleep(1)
    try:
        driver.find_element_by_xpath("//button[text()='Oui']").click()
    except Exception as e:
        print(e)

    athletes_rows = []
    page = BeautifulSoup(driver.page_source, "html.parser")
    athletes_table = page.select_one("#entries-table tbody")
    athletes_rows.extend(athletes_table.select("tr"))

    i = 2
    while check_exists_by_link_text(driver, "Next") and i < 584:  # next page button

        try:
            driver.find_element_by_xpath("//a[text()='MAYBE LATER']").click()
        except Exception as e:
            print(e)
            pass
        nextButton = driver.find_element_by_link_text('Next')
        clickButton(driver, nextButton)
        sleep(1)
        print("** Scraping Page : "+str(i)+ " **\n")
        page = BeautifulSoup(driver.page_source, "html.parser")
        athletes_table = page.select_one("#entries-table tbody")
        athletes_rows.extend(athletes_table.select("tr"))
        i = i + 1
    driver.close()
    driver.quit()
    me = os.getpid()
    kill_proc_tree(me, including_parent=False)

    athletes_records = []
    for athlete_row in athletes_rows :
        try :
            athletes_records.append(retrieve_athlete_informations(athlete_row))
        except Exception as e:
            print(e)
            pass

    keys = athletes_records[0].keys()
    with open('athletes.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(athletes_records)
