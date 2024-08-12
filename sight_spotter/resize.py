import os
import requests
import io
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
file_name = "temp.jpg"
full_path = current_dir+"/"+file_name
headers = {'User-Agent': 'bot'}


def bytes_size_im(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        image_bytes = io.BytesIO(response.content)
        img = Image.open(image_bytes)
        img.save(current_dir + "/" + file_name)
        img_size = os.path.getsize(current_dir+"/"+file_name)
        img.close()
        return img_size
    else:
        print("err")


def check_size_im(url):
    size = bytes_size_im(url)
    if size >= 1000000:
        compress_img()
    files = {'photo': open(full_path, 'rb')}
    return files


def compress_img(new_size_ratio=0.7, quality=90, width=None, height=None):
    with Image.open(full_path) as img:
        # print the original image shape
        print("[*] Image shape:", img.size)
        # get the original image size in bytes
        image_size = os.path.getsize(full_path)
        if new_size_ratio < 1.0:
            # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
            img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.Resampling.LANCZOS)
            # print new image shape
            print("[+] New Image shape:", img.size)
        elif width and height:
            # if width and height are set, resize with them instead
            img = img.resize((width, height), Image.ANTIALIAS)
        try:
            # save the image with the corresponding quality and optimize set to True
            img.save(full_path, quality=quality, optimize=True)
        except OSError:
            # convert the image to RGB mode first
            img = img.convert("RGB")
            # save the image with the corresponding quality and optimize set to True
            img.save(full_path, quality=quality, optimize=True)
        print("[+] New file saved:", full_path)
        # get the new image size in bytes
        new_image_size = os.path.getsize(full_path)
        # calculate the saving bytes
        saving_diff = new_image_size - image_size
        # print the saving percentage
        print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")
