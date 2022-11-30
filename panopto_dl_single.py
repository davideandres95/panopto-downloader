#!/usr/bin/python
# Downloads a single Panopto video.
import requests
import json
import os
import youtube_dl
import sys
import urllib.parse

if(len(sys.argv) == 5):
	PANOPTO_BASE = sys.argv[1]
	vid_id = sys.argv[2]
	TOKEN = sys.argv[3]
	dest_filename = sys.argv[4]
elif(len(sys.argv) == 4):
	url = urllib.parse.urlparse(sys.argv[1])
	PANOPTO_BASE = url.scheme + "://" + url.netloc
	vid_id = urllib.parse.parse_qs(url.query)["id"][0]
	TOKEN = sys.argv[2]
	dest_filename = sys.argv[3]
else:
	print("Usage:	panopto_dl.py [base URL] [id] [ASPXAUTH token] [output file]\n",
		"or:	panopto_dl.py [video URL] [ASPXAUTH token] [output file]")
	exit()

s = requests.session() # cheeky global variable
s.cookies = requests.utils.cookiejar_from_dict({".ASPXAUTH": TOKEN})

# WHYYYY does panopto use at least 3 different types of API!?!?!?
def json_api(endpoint, params=dict(), post=False, paramtype="params"):
	if post:
		r = s.post(PANOPTO_BASE + endpoint, **{paramtype: params})
	else:
		r = s.get(PANOPTO_BASE + endpoint, **{paramtype: params})
	if not r.ok:
		print(r.text)
	return json.loads(r.text)

delivery_info = json_api("/Panopto/Pages/Viewer/DeliveryInfo.aspx", {
	"deliveryId": vid_id,
	"responseType": "json"
}, True, "data")
streams = delivery_info["Delivery"]["Streams"]
for i in range(len(streams)):
	print("Downloading:", dest_filename)
	ydl_opts = {
		"outtmpl": dest_filename,
		"quiet": True
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([streams[i]["StreamUrl"]])
