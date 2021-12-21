from utils.transformations import distcord,transform_point
import config

def distanceCen(d1, d2):
    x1, y1 = (d1[2] + d1[0]) / 2, (d1[1] + d1[3]) / 2
    x2, y2 = (d2[2]+d2[0])/2, (d2[1]+d2[3])/2
    x_d = (x2 - x1)
    y_d = (y2 - y1)
    dis = ((x_d)**2 + (y_d)**2)**0.5
    return dis

def distanceFeet(d1, d2):
    global dictPts
    x1, y1 = (d1[2] + d1[0]) / 2, d1[3]
    x2, y2 = (d2[2]+d2[0])/2, d2[3]
    x1, y1 = transform_point((x1,y1))
    x2, y2 = transform_point((x2,y2))
    if d1[4] not in dictPts.keys():
        dictPts[d1[4]] = (int(x1), int(y1))
    if d2[4] not in dictPts.keys():
        dictPts[d2[4]] = (int(x2), int(y2))
    dis = distcord((x1,y1),(x2,y2))
    return dis

def filterbydis(trackers):
    global dictPts 
    dictPts = {}
    ListFrame = checkInFrame(trackers)
    candidatesR = []
    candidatesY = []
    countR = 0
    for idx, d1 in enumerate(trackers):
        for d2 in trackers[idx:]:
            if d1[4] != d2[4] and distanceFeet(d1, d2) < config.Nmeter:
                if d1[4] not in ListFrame:
                    candidatesR.append(d1[4])
                if d2[4] not in ListFrame:
                    candidatesR.append(d2[4])
                if (d1[4] not in ListFrame) and (d2[4] not in ListFrame):
                    countR+=1
            elif d1[4] != d2[4] and distanceFeet(d1, d2) < 2*config.Nmeter:
                if (d1[4] not in candidatesR) and (d1[4] not in ListFrame) :
                    candidatesY.append(d1[4])
                if (d2[4] not in candidatesR) and (d2[4] not in ListFrame):
                    candidatesY.append(d2[4])

    return  countR, list(set(candidatesR)), list(set(candidatesY)), dictPts

                
def checkInFrame(trackers):
    ListiF = []
    for det in trackers:
        cx = (det[0]+det[2])/2
        cy = (det[1]+det[3])/2
        if not ((0 < cx) and (cx < config.Width) and (0 < cy) and (cy < config.Height)):
            ListiF.append(det[4])
    return ListiF