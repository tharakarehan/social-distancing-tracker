import cv2
# mapColor = (204,229,255)
# mapColor = (192,192,192) #silver
# mapColor = (211,211,211) #light gray
font = cv2.FONT_HERSHEY_SIMPLEX
mapColor = (128,128,128) #dark gray
id_show = False
ring_show = True
# pts = [(335, 187), (346, 187), (353, 316), (339, 316), (335, 187)]
pts = [(599, 362), (749, 359), (769, 493), (595, 498), (599, 362)]
Nmeter = 0
Hm = None
InvHm = None
Width = 0
Height = 0
minX = 0
minY = 0 
warpedWidth = 0
warpedHeight = 0
no_bbox = False

