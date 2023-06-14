#include <opencv2/opencv.hpp>

int main(int argc, char* argv[])
{   
    /*
    cv::VideoCapture cap(0);
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 320);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 240);
    
    if (!cap.isOpened())
    {
        std::cout << "Cannot open camera" << std::endl;
        return -1;
    }
    */
    if (argc < 3)
    {
        std::cerr << "Invalid number of arguments." << std::endl;
        return 1;
    }
    int port = std::stoi(argv[1]);
    std::string handle = argv[2];
    while (true)
    {   
        //cv::Mat frame;
        //bool ret = cap.read(frame);
        try
        {
            cv::Mat frame;
            cv::VideoCapture cap("http://127.0.0.1:" + std::to_string(port) + handle);

            cap.read(frame);
            cap.release();
            
            cv::Size newSize(320, 240);
            cv::resize(frame, frame, newSize);
            
            cv::Mat gray;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
    
            int k = 40;
            cv::Mat avg_kernel = cv::Mat::ones(k, k, CV_32F) / (k * k);
            cv::Mat blurred;
            cv::filter2D(gray, blurred, -1, avg_kernel);
    
            cv::Mat diff;
            cv::subtract(gray, blurred, diff);
            int threshold = 7;
            cv::Mat bi_diff = (cv::abs(diff) <= threshold) / 255;
            bi_diff.convertTo(bi_diff, CV_8U);
            bi_diff *= 255;
    
            cv::SimpleBlobDetector::Params params;
            params.filterByColor = false;
            params.minThreshold = 100;
            params.maxThreshold = 120;
            params.filterByArea = true;
            params.minArea = 500/4;
            params.maxArea = 2500/4;
            params.filterByCircularity = false;
            params.minCircularity = 0.05;
            params.maxCircularity = 1.0;
            params.filterByConvexity = true;
            params.minConvexity = 0.25;
            params.maxConvexity = 1.0;
            params.filterByInertia = true;
            params.minInertiaRatio = 0.25;
            params.maxInertiaRatio = 1.0;
    
            cv::Ptr<cv::SimpleBlobDetector> detector = cv::SimpleBlobDetector::create(params);
            std::vector<cv::KeyPoint> keypoints;
            detector->detect(bi_diff, keypoints);
            
            std::cout << keypoints.size() << std::endl;
            //cv::Mat im_with_keypoints;
            //cv::drawKeypoints(gray, keypoints, im_with_keypoints, cv::Scalar(0, 0, 255), cv::DrawMatchesFlags::DRAW_RICH_KEYPOINTS);
    
            //cv::imshow("frame", im_with_keypoints);
            
            // Press 'q' to quit
            if (cv::waitKey(1) == 'q')
            {
                break;
            }
        } catch (const cv::Exception& e) {
        } catch (const std::exception& e) {
        }
    }

    cv::destroyAllWindows();

    return 0;
}