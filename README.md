# ava-dataset-tool

## AVA Dataset
The [AVA Dataset](https://research.google.com/ava/) is a newly exciting dataset for action detection and localization.

However, I just couldn't find the official toolkits for download, data preprocessing, and evaluation with standard baselines. I will put a few tools here that may be useful for future development. 

## Prerequisites
1. FFMPEG
2. OpenCV

## Download
Following [CVDF's instruction](https://github.com/cvdfoundation/ava-dataset), we are able to download the videos with their urls.

    $ cd ava-dataset-tool/video
    $ wget https://s3.amazonaws.com/ava-dataset/annotations/ava_file_names_trainval.txt
    $ ./download.sh

## Download annotations
The trainval annotations can be downloaded by

    $ cd ava-dataset-tool
    $ wget https://s3.amazonaws.com/ava-dataset/annotations/ava_trainval.zip
    $ unzip ava_trainval.zip

## Groundtruth visualization
Data preprocessing is so important for network training. Previously I tried OpenCV, but it is challenging to extract the exact keyframe maybe due to different codec settings. Currently we extract the video segments and the keyframes using ffmpeg. We also visualize the bboxes for each keyframe in folder `preproc`. Note that we only process each clip once, which is faster than other repos.

    $ cd ava-dataset-tool
    $ python3 extract_keyframe.py

The results look o.k., but we need futher check if the keyframes are exactly the ones Google selected for annotating the bboxes.

<p align="center">
<img src="https://github.com/kevinlin311tw/ava-dataset-tool/blob/master/sample_bbox.jpg", width="400">
</p>

Stay tuned..

