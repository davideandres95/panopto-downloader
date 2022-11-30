import os
import requests
import youtube_dl

"""
Change the following values to yours one
"""
PANOPTO_BASE = "https://tum.cloud.panopto.eu/"
TOKEN = ""
DEST_FOLDER = "/home/ddeandres/panopto"
PANOPTO_FOLDER = "Optical Communi 950543395 (W20/21)"
#PANOPTO_FOLDER = "OCS VL Session 1"
DOWNLOAD_FOLDER = "downloads"

s = requests.session()
s.cookies = requests.utils.cookiejar_from_dict({".ASPXAUTH": TOKEN})

def json_api(endpoint, params=None, is_post=False, param_type="params"):
    if params is None:
        params = dict()
    if is_post:
        r = s.post(PANOPTO_BASE + endpoint, **{param_type: params})
    else:
        r = s.get(PANOPTO_BASE + endpoint, **{param_type: params})
    if not r.ok:
        print(r.text)
    return r.json()


def name_normalize(name):
    return name.replace("/", "-")


def dl_session(session):
    # Generate destination directory path
    dest_dir = os.path.join(
        DEST_FOLDER,
        DOWNLOAD_FOLDER,
        name_normalize(session["FolderName"]),
        name_normalize(session["SessionName"])
    )

    # Prepare directories
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Get destination file name
    delivery_info = json_api("/Panopto/Pages/Viewer/DeliveryInfo.aspx", {
        "deliveryId": session["DeliveryID"],
        "responseType": "json"
    }, True, "data")
    filename = "{}.mp4".format(delivery_info["Delivery"]["SessionName"])
    dest_filename = os.path.join(dest_dir, filename)

    # Skip if file exist
    if os.path.exists(dest_filename):
        print("File '{}' already exist, skipping.".format(dest_filename))
        return

    # Download file
    print("Downloading:", dest_filename)
    video_url = session['IosVideoUrl']
    with youtube_dl.YoutubeDL({"outtmpl": dest_filename, "quiet": False}) as ydl:
        ydl.download([video_url])


def dl_folder(folder):
    params = {"queryParameters": {"folderID": folder["Id"]}}
    sessions = json_api("/Panopto/Services/Data.svc/GetSessions", params, True, "json")["d"]["Results"]
    for session in sessions:
        dl_session(session)

    # Download nested folders
    folders = json_api("/Panopto/Api/Folders", {"parentId": folder["Id"], "folderSet": 1})
    for folder in folders:
        dl_folder(folder)

folders = json_api("/Panopto/Api/Folders", {"parentId": "null", "folderSet": 1})
for folder in folders:
    if folder["Name"].startswith(PANOPTO_FOLDER):
        dl_folder(folder)
