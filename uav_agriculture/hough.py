import cv2
import numpy as np

image = cv2.imread("13472.jpg")
cv2.imshow("image", image)

dic = {}
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 10, 50, apertureSize = 3)
# cv2.imshow("edges", edges)
lines1 = cv2.HoughLines(edges, 1, np.pi/180, 125)

def slopeNeg(l):
    return -l[0], l[1]

slopes = []
for lines in lines1: 
    for rho,theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        m = float(y2 - y1) / float(x2 - x1)
        slopes += [m]
        cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)

slopes.sort()
filtered_slopes = [[slopes[0], 1]]
for slope in slopes:
    if abs(slope - filtered_slopes[-1][0]) > 0.3:
        filtered_slopes += [[slope, 1]]
    else:
        filtered_slopes[-1][1] += 1
print(map(slopeNeg, filtered_slopes))
cv2.imshow("image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
