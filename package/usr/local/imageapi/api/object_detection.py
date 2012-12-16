from os import path
import sys
import cv
import Image

XML_FACE_PATH = path.join(path.dirname(__file__), 'haarcascade_frontalface_default.xml')
XML_EYES_PATH = path.join(path.dirname(__file__), 'haarcascade_eye.xml')

def detect_face(cv_image):
    
    # create grayscale version
    grayscale = cv.CreateImage(cv.GetSize(cv_image), 8, 1)
    cv.CvtColor(cv_image, grayscale, cv.CV_RGB2GRAY)
    
    #equalize histogram
    cv.EqualizeHist(grayscale, grayscale)
    
    # create storage
    storage = cv.CreateMemStorage(128)
    cascade = cv.Load(XML_FACE_PATH)
    
    # detect objects
    faces = cv.HaarDetectObjects(image=grayscale, 
                                 cascade=cascade, 
                                 storage=storage, 
                                 scale_factor=1.3, # 1.1
                                 min_neighbors=3,  # 1
                                 flags=cv.CV_HAAR_DO_CANNY_PRUNING)

    # return image positions
    return faces


def detect_face_from_pil_image(pil_image):
    cv_img = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_img, pil_image.rotate(180).tostring()[::-1])
    return detect_face(cv_img)


def detect_eyes(cv_image):    
    # create grayscale version
    grayscale = cv.CreateImage(cv.GetSize(cv_image), 8, 1)
    cv.CvtColor(cv_image, grayscale, cv.CV_RGB2GRAY)
    
    #equalize histogram
    cv.EqualizeHist(grayscale, grayscale)
    
    # create storage
    storage = cv.CreateMemStorage(128)
    cascade = cv.Load(XML_EYES_PATH)
    
    # detect objects
    objects = cv.HaarDetectObjects(image=grayscale, 
                                   cascade=cascade, 
                                   storage=storage, 
                                   scale_factor=1.1, # 1.1
                                   min_neighbors=1,  # 1
                                   flags=cv.CV_HAAR_DO_CANNY_PRUNING)
    
    # return objects positions
    return objects


def detect_eyes_from_pil_image(pil_image):
    cv_img = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_img, pil_image.rotate(180).tostring()[::-1])
    return detect_eyes(cv_img)
















def detect_face_and_eyes_from_pil_image(pil_image):
    cv_img = cv.CreateImageHeader(pil_image.size, cv.IPL_DEPTH_8U, 3)
    cv.SetData(cv_img, pil_image.rotate(180).tostring()[::-1])
    return detect_faces_and_eyes(cv_img)






def detect_faces_and_eyes(image):
    
    
    image_scale = 1
    haar_scale = 1.3
    min_neighbors = 3
    haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING
    
    eyes_haar_scale = 1.1
    eyes_min_neighbors = 1
    eyes_haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING
    
    
    eyeCascade = cv.Load(XML_EYES_PATH)
    faceCascade = cv.Load(XML_FACE_PATH)
    
    # Allocate the temporary images
    gray = cv.CreateImage((image.width, image.height), 8, 1)
    smallImage = cv.CreateImage((cv.Round(image.width / image_scale),cv.Round (image.height / image_scale)), 8 ,1)
    #eyeregion = cv.CreateImage((cv.Round(image.width / image_scale),cv.Round (image.height / image_scale)), 8 ,1)
    #cv.ShowImage("smallImage",smallImage)
    
    # Convert color input image to grayscale
    cv.CvtColor(image, gray, cv.CV_BGR2GRAY)
    
    # Scale input image for faster processing
    cv.Resize(gray, smallImage, cv.CV_INTER_LINEAR)
    
    # Equalize the histogram
    cv.EqualizeHist(smallImage, smallImage)
    
    # Detect the faces
    faces = cv.HaarDetectObjects(smallImage, faceCascade, cv.CreateMemStorage(0),
    haar_scale, min_neighbors, haar_flags)
    #, max_size)
    
    
    
    """
    # create the wanted images
    eig = cv.CreateImage(cv.GetSize(gray), 32, 1)
    temp = cv.CreateImage(cv.GetSize(gray), 32, 1)
    
    # the default parameters
    quality = 0.01
    min_distance = 1
    MAX_COUNT = 1000
    
    # search the good points
    features = cv.GoodFeaturesToTrack(gray, eig, temp, MAX_COUNT, 
                                      quality, min_distance, None, 3, 0, 0.04)
    
    
    
    for (x,y) in features:
        print "Good feature a: ", x, y
        objects.append(((x,y, 3, 3), 1))
        
    """
    
    
    
    
    
    
    
    objects = []
    
    
    # If faces are found
    for ((x, y, w, h), n) in faces:
        pt1 = (int(x * image_scale), int(y * image_scale))
        pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
        
        a=pt1[0]
        b=pt1[1]
        c=pt2[0]-pt1[0]
        d=pt2[1]-pt1[1]
            
        #objects.append(((a, b, c, d), n))
        
        face_cordinates = {
                           "position": ((a, b, c, d), n),
                           "eyes": [],
                           }
        
        #face_region = cv.GetSubRect(image,(a,b,c,d))
        cv.SetImageROI(image, (a,b,c,int(d*0.6))) # remove mouth
    
        eyes = cv.HaarDetectObjects(image, eyeCascade, cv.CreateMemStorage(0),
                eyes_haar_scale, eyes_min_neighbors,
                eyes_haar_flags)
        
        # For each eye found
        for eye in eyes:
            
            
            ept1 = (eye[0][0],eye[0][1])
            ept2 = ((eye[0][0]+eye[0][2]),(eye[0][1]+eye[0][3]))
            
            ea = ept1[0]
            eb = ept1[1]
            ec = (ept2[0]-ept1[0])
            ed = (ept2[1]-ept1[1])
            
            #objects.append(((ea+a, eb+b, ec, ed), eye[1]))
            face_cordinates["eyes"].append(((ea+a, eb+b, ec, ed), eye[1]))
            
            print (ea, eb, ec, ed)
        
        objects.append(face_cordinates)
        
    #print "###", objects
    return objects

