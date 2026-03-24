#pragma once
#include <string>
#include <cstdlib>
#include <fstream>
#include <cstdio>

class FileValidator {
public:
    bool CheckFile(const std::string& filePath) {
        std::ifstream file(filePath);
        return file.good();
    }
    int GetDuration(const std::string& filePath) {
        std::string cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"" + filePath + "\" > dur.txt";
        std::system(cmd.c_str());
        std::ifstream f("dur.txt");
        double d = 0; f >> d; f.close();
        std::remove("dur.txt");
        return (int)d;
    }
};

class VideoEditor {
public:
    bool CutAndRotate(const std::string& inputPath, const std::string& outputPath, int startSec, int durationSec) {
        std::string filter = "scale=w=-1:h=720,crop=400:720,setsar=1";
        std::string cmd = "ffmpeg -y -hide_banner -ss " + std::to_string(startSec) +
            " -t " + std::to_string(durationSec) +
            " -i \"" + inputPath + "\" " +
            " -vf \"" + filter + "\" -c:v libx264 -preset ultrafast -crf 30 -c:a copy \"" + outputPath + "\"";
        return std::system(cmd.c_str()) == 0;
    }
};

class CoverExtractor {
public:
    bool CreateCover(const std::string& inputPath, const std::string& outputPath) {
        std::string cmd = "ffmpeg -y -hide_banner -ss 0 -i \"" + inputPath + "\" -vframes 1 -update 1 \"" + outputPath + "\"";
        return std::system(cmd.c_str()) == 0;
    }
};

class NetworkUploader {
public:
    bool Upload(const std::string& videoPath, const std::string& caption, const std::string& serverUrl) {
        std::string cmd = "chcp 65001 > nul & curl -s -X POST "
            "-F \"caption=" + caption + "\" " +
            "-F \"file=@" + videoPath + "\" " +
            "-F \"cover=@" + videoPath + "\" " + serverUrl;

        return std::system(cmd.c_str()) == 0;
    }
};