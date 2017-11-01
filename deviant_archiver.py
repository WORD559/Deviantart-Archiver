from HTMLParser import HTMLParser
import requests, json, string

class Deviant(HTMLParser):
    data = []
    downloads = []
    pull = False
    mode = 0
    s = requests.session()
    def handle_starttag(self,tag,attrs):
        if self.mode == 1:
            if tag == "script":
                self.pull = True
        if self.mode == 2:
            if tag == "a":
                try:
                    d_attrs = dict(attrs)
                    if "download" in d_attrs["class"]:
                        print "Got download link!"
                        self.downloads.append(d_attrs["href"])
                except:
                    pass

    def handle_data(self,data):
        if self.mode == 1:
            if self.pull:
                if "window.__external_data" in data:
                    self.data.append(data)
                self.pull = False

    def load_page(self,url,corrections="tag",cutoff_length=20):
        self.data = []
        self.mode = 1
        self.feed(self.s.get(url).content)
        self.mode = 0
        self.reset()
        self.datas = self.data[0].split(";")
        datas = self.datas
        #print datas
        if corrections == "tag":
            self.data = datas[1][cutoff_length:]+";"+datas[2]
        elif corrections == "favourites":
            self.data = datas[1][datas[1].index("{"):]
        self.data = json.loads(self.data)
        
    def translate_meta_to_page(self,meta):
        ID = meta["id"]
        user = meta["author"]["username"]
        title = meta["alt"][:-(4+len(user))]
        normalised = title
        for char in string.punctuation:
            normalised = ((normalised.replace(char,"")).replace("  "," "))
        normalised = normalised.replace(" ","-")
        return "https://www.deviantart.com/art/"+normalised+"-"+str(ID)

    def download(self,meta):
        try:
            page = self.translate_meta_to_page(meta)
        except KeyError:
            return meta["src"]
        self.downloads = []
        self.mode = 2
        self.feed(self.s.get(page).content)
        self.mode = 0
        self.reset()
        if len(self.downloads) == 1:
            down = self.downloads[0]
            return self.s.get(down).url
        elif len(self.downloads) == 0:
            return meta["src"]
        else:
            return self.downloads
        
