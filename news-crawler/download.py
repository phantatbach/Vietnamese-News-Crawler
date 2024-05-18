import os
import xml.etree.ElementTree as ET
import random 
from p_tqdm import p_map
import requests

sitemap_folder = 'sitemaps/thanhnien_v2'
os.makedirs(sitemap_folder, exist_ok=True)

tree = ET.parse('sitemaps/sitemap.xml')
root = tree.getroot()

proxies = open("available_proxies.txt", "r").read().strip().split("\n")
sitemaps = []
for sitemap in root:
    sitemaps.append(sitemap[0].text)
print(len(sitemaps))
input_proxies = random.choices(proxies, k=len(sitemaps))
print(len(input_proxies))
def download(sitemap, proxy):
    r = requests.get(sitemap, proxies={"http": f"http://{proxy}"})
    open(f'{sitemap_folder}/{sitemap.split("/")[-1]}', 'wb').write(r.content)

p_map(download, sitemaps, input_proxies, num_cpus=10)