import time
import cv2
from numba.core import config
import numpy as np
import argparse
from utils import image_utils
from utils import distcalc
from utils.model_utils import pedestrianDetector
from utils.transformations import transform_frame,transform_point,distcord
from sort import Sort
import os
import config

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run SORT')
    parser.add_argument('-i','--input_file', type=str, help='input videos file path name')
    parser.add_argument('-m','--model_path', type=str, required=True, help='path to the model')
    parser.add_argument('-t', '--threshold', type=float, default=0.7, help='threshold for detections')
    parser.add_argument('-o','--output_file', type=str, help='output video file path name')
    parser.add_argument('-c','--camera', type=int, default=99, help='camera stream index')
    parser.add_argument('--save', action='store_true',help='whether to save the video')
    parser.add_argument('--find_homography', action='store_true',help='if the transformation matrix is not available')
    parser.add_argument('--no_bbox', action='store_true',help='circles will be drawn instead of bounding boxes')
    parser.add_argument('--slow', action='store_true',help='reduce the fps of the video if too high')
    args = parser.parse_args()

    # initialize the video stream, pointer to output video file, and frame dimensions
    cam = args.camera
    if cam != 99:
        vs = cv2.VideoCapture(cam)
        inputFile = cam
    else:
        inputFile = args.input_file
        vs = cv2.VideoCapture(inputFile)

    fps = int(vs.get(cv2.CAP_PROP_FPS))
    total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    (W, H) = (int(vs.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    config.Width,config.Height = W,H

    print("Original FPS:", fps)
    Tr = args.threshold
    tracker = Sort()
    
    model = pedestrianDetector(args.model_path, H, W, Tr)
    model.load()
    linePt1,linePt2 = image_utils.define_ROI(inputFile, H, W)

    if args.find_homography:
        src_pts = image_utils.get_points(inputFile, W, H)
    else:
        src_pts = config.pts

    config.Hm, config.minX, config.minY, warped, warpedcropped = transform_frame(inputFile,W,H,src_pts,False)
    config.InvHm = np.linalg.pinv(config.Hm)
    config.Nmeter = distcord(transform_point(linePt1),transform_point(linePt2))
    config.warpedHeight ,config.warpedWidth, _ = warped.shape
    config.warpedHeight = int(config.warpedHeight*1.2)
    config.no_bbox = args.no_bbox
    framemap1 = image_utils.create_blank(config.warpedWidth,config.warpedHeight,config.mapColor)
    framemap1= framemap1[config.minY:,config.minX:,:]
    print('original_Width',config.Width)
    print('map_Width',framemap1.shape[1])
    framemap1Width = framemap1.shape[1]
    maxWidth = max(config.Width,framemap1.shape[1])
    print('max_Width',maxWidth)
    original_h = int(config.Height*maxWidth/config.Width)
    map_h = int(framemap1.shape[0]*maxWidth/framemap1.shape[1])
    
    if cam != 99:
        vs.release()
        vs = cv2.VideoCapture(cam)
        
    if args.save:
        print('Save')
        result = cv2.VideoWriter(args.output_file,  
                                cv2.VideoWriter_fourcc('M','J','P','G'), 
                                fps, (maxWidth,original_h+map_h+int((original_h+map_h)*0.1)))
    countF = 0
    while True:
        t1 = time.time()
        (grabbed, frame) = vs.read()
        countF+=1
        if not grabbed:
            break
        if args.slow and countF%2==1:
            continue
        detections = model.predict(frame)
        trackers = tracker.update(detections, frame)

        countVilR, canlistR, canlistY, dictbdye = distcalc.filterbydis(trackers)
        # print(countVilR)
        framemap = image_utils.create_blank(config.warpedWidth,config.warpedHeight,config.mapColor)
        framemapND = framemap.copy()
        for key, value in dictbdye.items():
            framemap,framemapND = image_utils.draw_on_map(framemap,framemapND,key ,value, canlistR,canlistY,7,3,3,config.id_show,config.ring_show)

        if config.no_bbox:
            Invframemap = cv2.warpPerspective(framemapND,config.InvHm, (config.Width, config.Height))

        framemap = framemap[config.minY:,config.minX:,:]
        image_utils.draw_text_Map(framemap,framemap1Width)

        if config.no_bbox:
            frameOrg = frame.copy()
            frame = image_utils.frame_mask_creator(Invframemap,frame)
            frame,maskx = image_utils.adjust_frame(trackers,frame,frameOrg)


        for d in trackers:
            d = d.astype(np.int32)
            # print(d)
            frame = image_utils.draw_box(frame, d, W, H, canlistR, canlistY)
        T = time.time()-t1
        
        frame = image_utils.draw_info(frame,T)
        if maxWidth == framemap1.shape[1]:
            frame = cv2.resize(frame,(maxWidth,original_h))
        else:
            framemap = cv2.resize(framemap,(maxWidth,map_h))
        framef = image_utils.create_blank(maxWidth, original_h+map_h+int((original_h+map_h)*0.1), (255,255,255))
        framef[:original_h,:,:] = frame
        framef[original_h:original_h+map_h,:,:] = framemap
        # image_utils.draw_text(framef, "Social Distance Violations - {}".format(countVilR), 
        #                 (85,framef.shape[0]-int((original_h+map_h)*0.1)+35), 
        #                                 config.font, 2, (0,0,255), 5, (255,255,255))
        
        image_utils.draw_lower_bar(countVilR,framef,maxWidth,original_h,map_h)

        if args.save:
            result.write(framef)
           
        cv2.imshow("Social Distance Tracker", framef)
        if fps < 20:
            cv2.waitKey(5)
            
        # cv2.waitKey(1)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            break
        

    if args.save:
        result.release()
    vs.release()
    
    
