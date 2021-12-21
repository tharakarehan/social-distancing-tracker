import cv2
from utils.image_utils import get_first_frame
import numpy as np
import config


def distcord(p1,p2):
    dist = (p1[0]-p2[0])**2+(p1[1]-p2[1])**2
    return dist**0.5

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect


def transform_frame(video_path,w,h,trans_points,Square):
    im = get_first_frame(video_path)
    trans_points = np.array(trans_points[:-1])
    src_pts = order_points(trans_points)
    (tl, tr, br, bl) = src_pts
    
    if Square == True:
        sqlen = max(distcord(tl,tr),distcord(tl,bl))
        target_pts = np.array(((0+w,0+h),(w+sqlen,h),(w+sqlen,h+sqlen),(w+0,h+sqlen)), dtype = "float32")
    else:
        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        target_pts = np.array([
            [0+w, 0+h],
            [w+maxWidth - 1, 0+h],
            [w+maxWidth - 1, h+maxHeight - 1],
            [w+0, h+maxHeight - 1]], dtype = "float32")
        # compute the perspective transform matrix and then apply it

    M = cv2.getPerspectiveTransform(src_pts,target_pts)
    original_corners = [(0,0),(w,0),(w,h),(0,h)]

    list_X_min,list_Y_min = [],[]

    for pt in original_corners:
        x1,y1,z = np.matmul(M,np.array([pt[0],pt[1],1]))
        X,Y = x1/z,y1/z
        list_X_min.append(X)
        list_Y_min.append(Y)

    MinX = min(min(list_X_min),0)
    MinY = min(min(list_Y_min),0)

    T = np.array([[1, 0, -MinX],[0, 1, -MinY],[0, 0, 1]])
    M_translated = np.dot(T,M)

    list_X_max,list_Y_max = [],[]

    for pt in original_corners:
        x1,y1,z = np.matmul(M_translated,np.array([pt[0],pt[1],1]))
        X,Y = x1/z,y1/z
        list_X_max.append(X)
        list_Y_max.append(Y)

    MaxX = max(list_X_max)
    MaxY = max(list_Y_max)

    MinX = int(min(list_X_max))
    MinY = int(min(list_Y_max))

    # print('X',MaxX)
    # print('Y',MaxY)
    warped = cv2.warpPerspective(im, M_translated, (int(np.ceil(MaxX)), int(np.ceil(MaxY))))
    warpedcropped = warped[MinY:,MinX:,:]
    cv2.imshow("Pedestron", warpedcropped)
    # cv2.imshow("Pedestron", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return M_translated, MinX, MinY, warped, warpedcropped


def transform_point(pt):
    x,y,z = np.matmul(config.Hm,np.array([pt[0],pt[1],1]))
    X,Y = x/z,y/z
    return (X,Y)
   