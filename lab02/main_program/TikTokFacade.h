#pragma once
#include "Subsystems.h"
#include <string>

class TikTokFacade {
private:
    FileValidator validator;
    VideoEditor editor;
    NetworkUploader uploader;
    std::string serverUrl = "http://100.69.137.26:8000/api/upload";

public:
    bool ProcessAndUpload(const std::string& inputPath, int segmentDur, const std::string& caption) {
        if (!validator.CheckFile(inputPath)) return false;

        int totalSeconds = validator.GetDuration(inputPath);
        bool allOk = true;

        int partNumber = 1;
        for (int start = 0; start < totalSeconds; start += segmentDur) {
            std::string partVideo = "part_" + std::to_string(partNumber) + ".mp4";
            std::string currentCaption = caption + " (Part " + std::to_string(partNumber) + ")";

            if (editor.CutAndRotate(inputPath, partVideo, start, segmentDur)) {

                if (!uploader.Upload(partVideo, currentCaption, serverUrl)) {
                    allOk = false;
                }
                std::remove(partVideo.c_str());
            }
            else {
                allOk = false;
            }
            partNumber++;
        }
        return allOk;
    }
};