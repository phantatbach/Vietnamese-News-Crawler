import requests

from p_tqdm import p_map

# sitemap_folder = 'sitemaps/thanhnien_v2'
# os.makedirs(sitemap_folder, exist_ok=True)

# tree = ET.parse('sitemaps/sitemap.xml')
# root = tree.getroot()

# sitemaps = []
# for sitemap in root:
#     sitemaps.append(sitemap[0].text)
    # ! wget -P {sitemap_folder} {sitemap[0].text}

# read proxies
proxies = open("proxies.txt", "r").read().strip().split("\n")

def get(url, proxy): 
	""" 
	Sends a GET request to the given url using given proxy server. 
	The proxy server is used without SSL, so the URL should be HTTP. 
 
	Args: 
		url - string: HTTP URL to send the GET request with proxy 
		proxy - string: proxy server in the form of {ip}:{port} to use while sending the request 
	Returns: 
		Response of the server if the request sent successfully. Returns `None` otherwise. 
 
	""" 
	print()
	try: 
		r = requests.get(url, proxies={"http": f"http://{proxy}"}) 
		if r.status_code < 400: # client-side and server-side error codes are above 400 
			return r 
		else: 
			print(r.status_code) 
	except Exception as e: 
		print(e) 
 
	return None

def check_proxy(proxy): 
	""" 
	Checks the proxy server by sending a GET request to httpbin. 
	Returns False if there is an error from the `get` function 
	""" 
 
	return get("http://httpbin.org/ip", proxy) is not None 
 
# available_proxies = list(filter(check_proxy, proxies))
checks = p_map(check_proxy, proxies, num_cpus=8)

available_proxies = []
for i, check in enumerate(checks):
    if check:
        available_proxies.append(proxies[i])
	
with open("available_proxies.txt", "w") as f:
    f.write("\n".join(available_proxies))
print(f"Available proxies: {len(available_proxies)}")