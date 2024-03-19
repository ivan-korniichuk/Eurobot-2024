#include <opencv2/opencv.hpp>
#include <opencv2/objdetect/aruco_detector.hpp>
#include <iostream>

int main() {
    cv::VideoCapture cap(1); // Open the default camera
    if (!cap.isOpened()) {
        std::cerr << "Error: Unable to open the camera." << std::endl;
        return -1;
    }

    //cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);

    while (true) {
        cv::Mat frame;

        cap >> frame; // Capture frame from camera
        if (frame.empty()) {
            std::cerr << "Error: Blank frame grabbed." << std::endl;
            break;
        }

        std::vector<int> markerIds;
        std::vector<std::vector<cv::Point2f>> markerCorners, rejectedCandidates;
        cv::aruco::DetectorParameters detectorParams = cv::aruco::DetectorParameters();
        cv::aruco::Dictionary dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_250);
        cv::aruco::ArucoDetector detector(dictionary, detectorParams);

        detector.detectMarkers(frame, markerCorners, markerIds, rejectedCandidates);

        if (!markerIds.empty()) {
            cv::aruco::drawDetectedMarkers(frame, markerCorners, markerIds);
        }

        cv::imshow("ArUco Marker Detection", frame);

        char key = cv::waitKey(1);
        if (key == 27) // Escape key
            break;
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
