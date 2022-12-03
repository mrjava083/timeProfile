import pytz, io
from requests import session
from datetime import datetime
from json import loads, dumps
from Crypto.Cipher.AES import new
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode, b64encode
from PIL import Image, ImageDraw, ImageFont

class Crypto:
	def __init__(self, auth):
	    self.key = bytearray(self.secret(auth), "utf-8")
	    self.iv = bytearray.fromhex('00' * 16)

	def secret(self, e):
		t, n, s = e[0:8], e[16:24]+e[0:8]+e[24:32]+e[8:16], 0
		while s < len(n):
			t = chr((ord(n[s][0]) - ord('0') + 5) % 10 + ord('0')) if n[s] >= '0' and n[s] <= '9' else chr((ord(n[s][0]) - ord('a') + 9) % 26 + ord('a'))
			n, s = self.replaceCharAt(n, s, t), s+1
		return n

	replaceCharAt = lambda self, e, t, i: e[0:t] + i + e[t + len(i):]
	encryption = lambda self, text: (
	    b64encode(new(self.key, 2, self.iv).encrypt(pad(text.encode(), 16))).decode())
	decryption = lambda self, text: (
	    unpad(new(self.key, 2, self.iv).decrypt(b64decode(text.encode())), 16).decode())

class Tools(object):
    def clock_image(self, text: str) -> bytes:
        image = Image.open('resource/image.png')
        font = ImageFont.truetype(font='resource/digital.ttf', size=450)
        draw = ImageDraw.Draw(image)

        width, height = image.size
        textsize = font.getbbox(text)

        draw.text(((width - textsize[2]) / 2 - 3, (height - textsize[3]) / 2 - 3), text=text, font=font, fill=(0, 0, 0))
        draw.text(((width - textsize[2]) / 2 + 3, (height - textsize[3]) / 2 - 3), text=text, font=font, fill=(0, 0, 0))
        draw.text(((width - textsize[2]) / 2 - 3, (height - textsize[3]) / 2 + 3), text=text, font=font, fill=(0, 0, 0))
        draw.text(((width - textsize[2]) / 2 + 3, (height - textsize[3]) / 2 + 3), text=text, font=font, fill=(0, 0, 0))

        draw.text(((width - textsize[2]) / 2, (height - textsize[3]) / 2), text=text, font=font, fill=(255, 255, 255))

        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    def get_time(self) -> str:
        return datetime.now(pytz.timezone('Asia/tehran')).strftime('%H:%M')

class Bot(Tools):
    def __init__(self, auth: str) -> None:
        self.auth = auth
        self.enc = Crypto(auth)
        self.url = 'https://shadmessenger60.iranlms.ir/'
        self.client = {
        "app_name"    : "Main",
        "app_version" : "3.2.2",
        "platform"    : "Web",
        "package"     : "web.shad.ir",
        "lang_code"   : "fa"
    }

    def post(self, url: str, **kwargs) -> str:
        while True:
            with session() as Session:
                with Session.post(url, **kwargs) as res:
                    if res.status_code != 200: continue
                    res = res.json()
                    return res.get('data_enc')

    def upload(self, url: str, **kwargs) -> dict:
        while True:
            with session() as Session:
                with Session.post(url, **kwargs) as res:
                    if res.status_code != 200: continue
                    return res.json()

    def requestSendFile(self, file: bytes) -> dict:
        data = {"api_version":"5", "auth": self.auth, "data_enc":self.enc.encryption(dumps({"method":"requestSendFile", "input":{"file_name":"clock.png","mime":"png","size":str(len(file))}, "client":self.client}))}
        return loads(self.enc.decryption(self.post(self.url, json=data))).get('data')

    def uploadFile(self, file: bytes) -> dict:
        FileR = self.requestSendFile(file)
        hash_send , file_id , url = FileR["access_hash_send"], FileR["id"] , FileR["upload_url"]

        header = {
            "auth":self.auth,
            "Host":url.replace("https://","").replace("/UploadFile.ashx",""),
            "chunk-size":str(len(file)),
            "file-id":str(file_id),
            "access-hash-send":hash_send,
            "content-length":str(len(file)),
            "part-number":"1",
            "total-part":"1"}

        self.upload(url, data=file, headers=header)
        return file_id

    def uploadAvatar(self, chat_id: str, file: bytes) -> dict:
        mt = str(self.uploadFile(file))
        data = {"api_version":"5", "auth": self.auth, "data_enc":self.enc.encryption(dumps({"method":"uploadAvatar", "input":{"object_guid":chat_id,"thumbnail_file_id":mt,"main_file_id":mt}, "client":self.client}))}
        return loads(self.enc.decryption(self.post(self.url, json=data))).get('data')

    def getAvatars(self, chat_id: str) -> dict:
        data = {"api_version":"5", "auth": self.auth, "data_enc":self.enc.encryption(dumps({"method":"getAvatars", "input":{"object_guid":chat_id}, "client":self.client}))}
        return loads(self.enc.decryption(self.post(self.url, json=data))).get('data')

    def deleteAvatar(self, chat_id: str, avatar_id: str) -> dict:
        data = {"api_version":"5", "auth": self.auth, "data_enc":self.enc.encryption(dumps({"method":"deleteAvatar", "input":{"object_guid":chat_id,"avatar_id":avatar_id}, "client":self.client}))}
        return loads(self.enc.decryption(self.post(self.url, json=data))).get('data')