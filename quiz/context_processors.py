import random
from copy import deepcopy

#to pass background color everytime a page is called
class Background:
    available=["light", "light"] #"warning", "info", "light", "dark", "success", "danger"
    used=[]

    @staticmethod
    def sandClock():
        bg=""
        if len(Background.available) < 1:

            bg=Background.used.pop()
            Background.available.append(bg)
            temp=deepcopy(Background.used)
            Background.used=deepcopy(Background.available)
            Background.available=deepcopy(temp)

        bg=random.choice(Background.available)
        Background.available.remove(bg)
        Background.used.append(bg)

        return bg

class Sidebar:
    available=["warning", "light", "danger", "dark",]
    used=[]

    @staticmethod
    def sandClock():
        bg=""
        if len(Sidebar.available) < 1:

            bg=Sidebar.used.pop()
            Sidebar.available.append(bg)
            temp=deepcopy(Sidebar.used)
            Sidebar.used=deepcopy(Sidebar.available)
            Sidebar.available=deepcopy(temp)

        bg=random.choice(Sidebar.available)
        Sidebar.available.remove(bg)
        Sidebar.used.append(bg)

        return bg


def getSD():

    sd=Sidebar.sandClock()

    if sd=="warning":
        lnk="danger"

    elif sd=="danger":
        lnk="warning"

    elif sd=="light":
        lnk="dark"

    elif sd=="dark":
        lnk="light"


    return sd, lnk
def getBG(req):

    bg=Background.sandClock()

    tx="dark"

    if bg=="dark":
        tx="white"

    (sd, lnk)=getSD()

    while sd==bg:
        (sd, lnk) = getSD()

    return{"bg_color":bg, "tx_color":tx, "sidebar_color":sd, "sidebar_link":lnk}