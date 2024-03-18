#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include "aruco.hpp"

using namespace cv;
using namespace std;

int main() {
    // Define camera parameters
    Mat camera_matrix = (Mat_<double>(3, 3) << 5000, 0, 970,
        0, 5000, 550,
        0, 0, 1);
    Mat dist_coeffs = (Mat_<double>(1, 5) << -3.4, -0.2, 0.015, 0, 0.05);

    const int F = 2;
    Size width_height = Size(300 * F, 200 * F);
    Point offset = Point(75 * F, 50 * F);

    // Initialize VideoCapture object
    VideoCapture cap(1);
    if (!cap.isOpened()) {
        cout << "Error: Unable to open camera" << endl;
        return -1;
    }

    Mat frame;
    while (true) {
        cap.read(frame);
        if (!frame.empty()) {
            ImageProcessor image_processor(frame, width_height, offset, camera_matrix, dist_coeffs);
            if (!image_processor.perspective_transform.empty()) {
                break;
            }
        }
    }

    cout << "Calibrated" << endl;

    // Initialize visualiser and data_analiser objects
    // Visualiser visualiser(...);
    // DataAnaliser data_analiser(...);

    while (true) {
        cap.read(frame);
        auto times_1 = chrono::steady_clock::now();
        // Mat img = image_processor.get_transformed_img(frame);
        // This one takes 0.1 sec but adapts to camera changes
        Mat img = image_processor.adapt_and_calibrate_img(frame);
        auto times_2 = chrono::steady_clock::now();
        // vector<Point> plants = image_processor.get_plants(img);
        // Uncomment above line if implemented in C++
        auto times_3 = chrono::steady_clock::now();
        auto time1 = chrono::duration_cast<chrono::milliseconds>(times_2 - times_1).count();
        auto time2 = chrono::duration_cast<chrono::milliseconds>(times_3 - times_2).count();
        // data_analiser.update(plants);
        // Uncomment above line if implemented in C++
        // vector<Point> clustered_plants = data_analiser.cluster_plants();
        // Uncomment above line if implemented in C++
        cout << "Model time: " << time2 << "    Img time: " << time1 << endl;
        // visualiser.update(img, clustered_plants);
        // Uncomment above line if implemented in C++
        imshow("frame", img);
        if (waitKey(1) == 'q') {
            break;
        }
    }

    return 0;
}
