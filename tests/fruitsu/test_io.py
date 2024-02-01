from fruitsu.io import HTTPFile
from rich import print


def test_https():
    # url = 'http://swcdn.apple.com/content/downloads/11/62/002-66265-A_HKQGKQG1Z4/orfaxf4k2gvqeatuhx6agnr5nlti3rwq93/InstallAssistant.pkg'
    url = "http://swcdn.apple.com/content/downloads/26/37/001-68446/r1dbqtmf3mtpikjnd04cq31p4jk91dceh8/InstallESDDmg.pkg"
    fh = HTTPFile(url)
    print(fh)
    hdr = fh.read(16)
    print(f"hdr: {hdr.hex()}")
