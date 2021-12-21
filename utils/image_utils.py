import cv2
import numpy as np
import config
global lines
lines = []

drawing = False
x2,y2 = -1,-1

def draw_box(frame, det,width,height, canlistR,canlistY):
    
    # if (abs(det[2] - det[0]) > 0.04 * width) and (abs(det[3] - det[1]) > 0.04 * height):
    if det[4] in canlistR:
        color = (0, 0, 255)
    elif det[4] in canlistY:
        color = (0, 255, 255)  
    else:
        color = (0, 255, 0)

    draw_text(frame, 'Id={}'.format(det[4]), (det[0], det[1]-10), config.font, 0.3,(0,0,0),1,color)  
    if not config.no_bbox:
        cv2.rectangle(frame, (det[0], det[1]), (det[2], det[3]), color, 2)
    else:
        cv2.circle(frame, (int((det[0]+det[2])/2), det[3]) ,radius = 3, color = color,thickness = -1)

    return frame
    
def draw_on_map(frame,frameND, keyid ,pt, canlistR,canlistY,r,thk,thk1,id_show,ring_show):
    
    # if (abs(det[2] - det[0]) > 0.04 * width) and (abs(det[3] - det[1]) > 0.04 * height):
    if keyid in canlistR:
        color = (0, 0, 255)
        cv2.circle(frame, (pt[0], pt[1]) ,radius= r, color = color,thickness = -1)
        if id_show:
            draw_text(frame, 'Id={}'.format(keyid), (pt[0], pt[1]-10), config.font, 0.3,(0,0,0),1,color)
        if ring_show:
            cv2.circle(frame, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk)
            if config.no_bbox:
                cv2.circle(frameND, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk1)
    elif keyid in canlistY:
        color = (0, 255, 255)
        cv2.circle(frame, (pt[0], pt[1]) ,radius= r, color = color,thickness = -1)
        if id_show:
            draw_text(frame, 'Id={}'.format(keyid), (pt[0], pt[1]-10), config.font, 0.3,(0,0,0),1,color)
        if ring_show:
            cv2.circle(frame, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk)
            if config.no_bbox:
                cv2.circle(frameND, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk1)
    else:
        color = (0, 255, 0)
        cv2.circle(frame, (pt[0], pt[1]) ,radius= r, color = color,thickness = -1)
        if id_show:
            draw_text(frame, 'Id={}'.format(keyid), (pt[0], pt[1]-10), config.font, 0.3,(0,0,0),1,color)
        if ring_show:
            cv2.circle(frame, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk)
            if config.no_bbox:
                cv2.circle(frameND, (pt[0], pt[1]) ,radius= int(config.Nmeter), color = color,thickness = thk1)
    
    return frame,frameND

def draw_info(frame, T):
    draw_text(frame, 'Latency: {} ms'.format(round(T*1000,2)), (0,0), config.font, 0.6, (255,255,255), 2, (0,0,0))
    return frame

def draw_text(img, text,
          pos=(0, 0),
          font=cv2.FONT_HERSHEY_PLAIN,
          font_scale=3,
          text_color=(0, 255, 0),
          font_thickness=2,
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, int(y + text_h + font_scale - 1)), font, font_scale, text_color, font_thickness)
    return text_w, text_h

def draw_shape(event,x,y,flag,parm):
    global x2,y2,drawing, img, img2
    
    if len(lines) < 2:
        if event == cv2.EVENT_LBUTTONDOWN:
            print('Clicked: ', (x,y))
            lines.append((x, y))
            drawing = True
            img2 = img.copy()
            x2,y2 = x,y
            cv2.line(img,(x2,y2),(x,y),(0,0,255),1, cv2.LINE_AA)

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                # print('Moving: ',(x,y))
                a, b = x, y
                if a != x & b != y:
                    img = img2.copy()
                    cv2.line(img,(x2,y2),(x,y),(0,255,0),1, cv2.LINE_AA)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            print('Released: ',(x,y))
            lines.append((x, y))
            img = img2.copy()
            cv2.line(img,(x2,y2),(x,y),(0,0,255),1, cv2.LINE_AA)
    else:
        return

def get_first_frame(video_path):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    if success:
        print("yes")
        return image

def draw_lines(video_path):
    global img, img2
    img = get_first_frame(video_path)
    img2 = img.copy()
    cv2.namedWindow("Pedestron")
    cv2.setMouseCallback("Pedestron",draw_shape)
    
    # press the escape button to exit
    while True:
        cv2.imshow("Pedestron",img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()
  
    return lines

def define_ROI( video_path, height, width):
    """
    Define Region of Interest based on user input.
   """
    
    lines = draw_lines(video_path)
    print(lines)
    return [lines[0], lines[1]]

def mouse_handler(event, x, y, flags, data):
    global btn_down
    global ix
    global iy
    r = 1

    if event == cv2.EVENT_LBUTTONUP and btn_down:
        #if you release the button, finish the line
        btn_down = False
        data['points'].append((ix, iy)) #append the point
        cv2.circle(data['im'], (ix, iy) ,radius= r, color = (0, 0, 255),thickness = -1)
        cv2.imshow("Pedestron", data['im'])

    elif event == cv2.EVENT_LBUTTONDOWN :
        btn_down = True
        ix , iy = x , y

def get_points(video_path,w,h):
    # Set up data to send to mouse handler
    im = get_first_frame(video_path)
    im2 = im.copy()
    draw_text(im, 'Draw dots on perspective transformation', (10,10), config.font, 0.6, (255,255,255), 2)
    data = {}
    data['im'] = im
    data['points'] = []
    data['w'] = w
    data['h'] = h

    # Set the callback function for any mouse event
    cv2.imshow("Pedestron", im)
    cv2.setMouseCallback("Pedestron", mouse_handler, data)
    cv2.waitKey(0)
    points = data['points']
    im2 = draw_lanes(im2,points,w,h)
    cv2.imshow("Pedestron", im2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Convert array to np.array in shape n,2,2
    print('trans_points',points)
    return points

def draw_lanes(frame,linelist,W,H):
    linelist.append(linelist[0])
    if min(W,H)>160: 
        r = int(min(H,W)/160)
    else:
        r = 1
    cv2.circle(frame, linelist[0] ,radius= r, color = (255, 0, 0),thickness = -1)
   
    for i in range(len(linelist)-1):
        cv2.circle(frame, linelist[i+1] ,radius= r, color = (255, 0, 0),thickness = -1)
        cv2.line(frame,linelist[i],linelist[i+1],(255,0,0),1)
    return frame

def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color
    return image

def frame_mask_creator(frameMap,frameReal):
    mask = cv2.inRange(frameMap, config.mapColor, config.mapColor)
    frameReal[mask==0] = frameMap[mask==0]
    return frameReal

def adjust_frame(dets,frameM,frameO):
    mask = np.zeros((config.Height,config.Width),dtype=np.uint8)
    for det in dets:
        det = det.astype(np.int32)
        mask[det[1]:det[3],det[0]:det[2]] = 255
        # external_poly = np.array( [[[det[0],det[1]],[det[2],det[1]],[det[2],det[3]],[det[0],det[3]]]] )
        # cv2.fillPoly( mask ,external_poly, (255,255,255) )
    frameM[mask!=0] = frameO[mask!=0]
    return frameM, mask

def draw_text_Map(framemap,w):
    scale = ((w/3)-2.8882352941178704)/ 237.0235294117647
    draw_text(framemap, "Bird's Eye View", (0,0), 
                                        config.font, round(scale,1) , (255,255,255), 3, (0,0,0))

def draw_lower_bar(c,framemap,w,h1,h2):
    scale = ((w*0.7)-4.88823529411808)/ 501.0235294117648
    text_h = 21.02352941176471*scale + 2.8882352941176626
    y_c = int(h1+h2+ ((h1+h2)*0.1 - text_h)/2)
    x_c = int(w*0.15)
    draw_text(framemap, "Social Distance Violations - {}".format(c), (x_c,y_c), 
                                        config.font, round(scale,1) , (0,0,255), 3, (255,255,255))