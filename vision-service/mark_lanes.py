import cv2
import sys

pts = []
img_copy = None
img = None

def draw_polygon(event, x, y, flags, param):
    global pts, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append([x, y])
        cv2.circle(img_copy, (x, y), 5, (0, 255, 0), -1)
        if len(pts) > 1:
            cv2.line(img_copy, tuple(pts[-2]), tuple(pts[-1]), (0, 255, 0), 2)
        if len(pts) == 4:
            cv2.line(img_copy, tuple(pts[-1]), tuple(pts[0]), (0, 255, 0), 2)
            print("\nCoordinates for this lane:")
            print("np.array([")
            print(f"    [{pts[0][0]}, {pts[0][1]}],")
            print(f"    [{pts[1][0]}, {pts[1][1]}],")
            print(f"    [{pts[2][0]}, {pts[2][1]}],")
            print(f"    [{pts[3][0]}, {pts[3][1]}]")
            print("], dtype=np.int32)")
            print("\nPress 'c' to clear and do another lane, or 'q' to quit.")
        cv2.imshow("Mark Lanes", img_copy)

if len(sys.argv) < 2:
    print("Usage: python mark_lanes.py <path_to_video>")
    sys.exit(1)

cap = cv2.VideoCapture(sys.argv[1])
ret, img = cap.read()
if not ret:
    print("Failed to read video.")
    sys.exit(1)

img_copy = img.copy()

cv2.namedWindow("Mark Lanes")
cv2.setMouseCallback("Mark Lanes", draw_polygon)

print("========================================")
print("1. Click 4 points to define a lane polygon.")
print("   Order: Far-Left, Far-Right, Near-Right, Near-Left.")
print("2. The coordinates will print to the console.")
print("3. Press 'c' to clear points and restart.")
print("4. Press 'q' to quit.")
print("========================================\n")

while True:
    cv2.imshow("Mark Lanes", img_copy)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        pts = []
        img_copy = img.copy()
        print("\nCleared. Click 4 points again.")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
