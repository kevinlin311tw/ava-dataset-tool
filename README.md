# ava-dataset-tool

## AVA Dataset
The [AVA Dataset](https://research.google.com/ava/) is a newly exciting dataset for action detection and localization.

I will put a few tools here that may be useful for future development. 

## Prerequisites
1. FFMPEG
2. OpenCV

## Download
Following [CVDF's latest instruction](https://github.com/cvdfoundation/ava-dataset), we are able to download the `AVA v2.1` train/val videos with their urls.

    $ cd ava-dataset-tool/video/trainval
    $ ./download.sh

Download the test videos with their urls.

    $ cd ava-dataset-tool/video/test
    $ ./download.sh

## Download annotations
The trainval annotations can be downloaded by

    $ cd ava-dataset-tool
    $ wget https://s3.amazonaws.com/ava-dataset/annotations/ava_v2.1.zip
    $ unzip ava_v2.1.zip

## Training data visualization
Data preprocessing is important for network training. Previously I tried OpenCV, but it is challenging to extract the exact keyframe maybe due to different codec settings. Currently we extract the video clips and the keyframes using ffmpeg. We visualize the bboxes for each keyframe in a new folder `preproc`. Note that this script extracts keyframes, bboxes, and the 3-second video clips from training set. 

    $ cd ava-dataset-tool
    $ python3 extract_keyframe.py

If you would like to extract video clips and keyframes from the validation set or test set, you may need slightly adjust the corresponding path in `extract_keyframe.py`.

<p align="center">
<img src="https://github.com/kevinlin311tw/ava-dataset-tool/blob/master/sample_bbox.jpg", width="400">
</p>

Stay tuned..

