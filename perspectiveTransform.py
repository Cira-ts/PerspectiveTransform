import cv2
import numpy as np
import math

# წერტილები, რომლის მიხედვითაც უნდა მოხდეს ფოტოს ტრანსფორმაცია
points = [
    [430, 85],
    [1586, 88],
    [95, 1190],
    [1969, 1144]
]

# წერტილები, რომელთა შორისაც მანძილი აინტერესებს მომხმარებელს
user_points = []

# საწყისი ფოტოს ზომები
og_height = 0
og_width = 0


running = True

resize_ratio = 1.0

img_resized_display = None


def getpoints(event, x, y, flags, param):
    global user_points, og_height, og_width, running, img_resized_display

    # რომელ წერტილებსაც დააწვება მომხმარებელი, მოინიშნება ლურჯად.
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img_resized_display, (x, y), 2, (255, 0, 0), -1)

        # საწყისი კოორდინატების გამოთვლა და შენახვა
        original_x = int(x / resize_ratio)
        original_y = int(y / resize_ratio)


        user_points.append([original_x, original_y])

        # რეალური მანძილის გამოთვლის ფუნქციის გამოძახება თუ ორი წერტილი მოინიშნა
        if len(user_points) == 2:
            getDistance()
            user_points = []  # წერტილების გასუფთავება, რომ შემდეგი წყვილი წერტილები შევინახოთ

        cv2.imshow('image', img_resized_display)


def getDistance():
    global user_points, og_width

    # ტრანსფორმირებული ფოტო
    output = perspectiveTransform()

    # მატრიცის საშუალებით მომხმარებლის მონიშნული წერტილების ახალი კოორდინატების გაგება
    points1 = np.float32(points[:4])
    points2 = np.float32([[0, 0], [og_width, 0], [0, output.shape[0]], [og_width, output.shape[0]]])
    matrix = cv2.getPerspectiveTransform(points1, points2)
    user_points_np = np.float32(user_points)
    transformed_points = cv2.perspectiveTransform(user_points_np.reshape(-1, 1, 2), matrix)


    real_width = 0.38

    # მეტრის და პიქსელის შეფარდების გამოთვლა
    meterPixel = real_width / output.shape[1]

    # წერტილებს შორის პიქსელური მანძილის გამოთვლა
    dist = math.sqrt((transformed_points[1][0][0] - transformed_points[0][0][0]) ** 2 +
                                 (transformed_points[1][0][1] - transformed_points[0][0][1]) ** 2)

    # მეტრი/პიქსელის და პიქსელური მანძილის დახმარებით რეალური მანძილის გამოთვლა
    realDist = dist * meterPixel

    rounded_dist = round(realDist, 3)

    print("Real distance:", rounded_dist, "meters")


def perspectiveTransform():
    global points, user_points, img, og_height, og_width

    # რეალური ფარდობა იმ ოთხკუთხედის გვერდებს შორის, რომლის მიხედვითაც ხდება ტრანსფორმაცია. შემდეგ ვითვლით ტრანსფორმირებული ფოტოს გვერდების ზომებს
    ratio = 38 / 36
    output_height = int(ratio * og_width)


    points1 = np.float32(points[:4])
    points2 = np.float32([[0, 0], [og_width, 0], [0, output_height], [og_width, output_height]])

    # ტრანსფორმაციის მატრიცა
    matrix = cv2.getPerspectiveTransform(points1, points2)

    # ტრანსფორმირებული ფოტოს მიღება და შენახვა
    output = cv2.warpPerspective(img, matrix, (og_width, output_height))
    save_path = 'output/transformed_image.jpg'
    cv2.imwrite(save_path, output)

    return output


# ფოტო რომლის ტრანსფორმაციაც მოხდება
img = cv2.imread('input/img.jfif')
og_height, og_width = img.shape[:2]

# ფოტოს გამოჩენა ეკრანზე შეცვლილი ზომით
max_display_width = 1000
max_display_height = 800
resize_ratio = min(max_display_width / og_width, max_display_height / og_height)
img_resized_display = cv2.resize(img.copy(), None, fx=resize_ratio, fy=resize_ratio, interpolation=cv2.INTER_AREA)

cv2.imshow('image', img_resized_display)
cv2.setMouseCallback('image', getpoints)

print("Click two points on the image. Press 'q' to quit.")


while running:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
