"""Script to process AVA dataset."""
from __future__ import print_function

import argparse
import os
import subprocess
import sys
import csv
import cv2
import code

parser = argparse.ArgumentParser()
parser.add_argument("--video_dir", default="./video/", help="Videos path.")
parser.add_argument("--annot_file", default="ava_train_v2.0.csv",
                    help="Anotation file path.")
parser.add_argument("--actionlist_file",
                    default="./ava_action_list_v2.0.csv",
                    help="Action list file path.")
parser.add_argument("--output_dir", default="./preproc", help="Output path.")

FLAGS = parser.parse_args()

videodir = FLAGS.video_dir
annotfile = FLAGS.annot_file
actionlistfile = FLAGS.actionlist_file
outdir = FLAGS.output_dir

outdir_clips = os.path.join(outdir, "clips")
outdir_keyframes = os.path.join(outdir, "keyframes")
outdir_bboxs = os.path.join(outdir, "bboxs")

clip_length = 3 # seconds
clip_time_padding = 1.0 # seconds


def load_action_name(annotations):
    csvfile = open(annotations,'r')
    reader = list(csv.reader(csvfile))
    dic = {}
    for i in range(len(reader)-1):
        temp = (reader[i+1][1],reader[i+1][2])
        dic[i+1] = temp

    return dic

def load_labels(annotations):
    csvfile = open(annotations,'r')
    reader = list(csv.reader(csvfile))
    dic = {}
    for i in range(len(reader)):

        if (reader[i][0],reader[i][1]) in dic:
            dic[(reader[i][0],reader[i][1])].append(i)
        else:
            templist = []
            templist.append(i)
            dic[(reader[i][0],reader[i][1])] = templist

    return reader, dic

def hou_min_sec(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60))
    return "%d:%d:%d" % (hours, minutes, seconds)

def _supermakedirs(path, mode):
    if not path or os.path.exists(path):
        return []
    (head, _) = os.path.split(path)
    res = _supermakedirs(head, mode)
    os.mkdir(path)
    os.chmod(path, mode)
    res += [path]
    return res

def mkdir_p(path):
    try:
        _supermakedirs(path, 0o775) # Supporting Python 2 & 3
    except OSError: # Python >2.5
        pass

def get_keyframe(videofile, video_id, time_id, outdir_keyframes):
    outdir_folder = os.path.join(outdir_keyframes, video_id)
    mkdir_p(outdir_folder)
    outpath = os.path.join(outdir_folder, '%d.jpg' % (int(time_id)))
    ffmpeg_command = 'rm %(outpath)s; \
                      ffmpeg -ss %(timestamp)f -i %(videopath)s \
                      -frames:v 1 %(outpath)s' % {
                          'timestamp': float(time_id),
                          'videopath': videofile,
                          'outpath': outpath}

    subprocess.call(ffmpeg_command, shell=True)
    return outpath

def visual_bbox(anno_data, action_name, keyfname, video_id, time_id, bbox_ids):
    frame = cv2.imread(keyfname)
    frame_height, frame_width, channels = frame.shape

    outdir_folder = os.path.join(outdir_bboxs, video_id)
    mkdir_p(outdir_folder)
    outpath = os.path.join(outdir_folder, '%d_bbox.jpg' % (int(time_id)))

    draw_dic = {}
    for idx in bbox_ids:
        bbox = anno_data[idx][2:6]
        action_string = action_name[int(anno_data[idx][-1])]
        cv2.rectangle(frame, (int(float(bbox[0])*frame_width),int(float(bbox[1])*frame_height)), 
                (int(float(bbox[2])*frame_width),int(float(bbox[3])*frame_height)), [0,0,255], 1)

        x1 = int(float(bbox[0])*frame_width)
        y1 = int(float(bbox[1])*frame_height)

        if (x1,y1) in draw_dic:
            draw_dic[(x1,y1)] +=1
        else:
            draw_dic[(x1,y1)] = 1

        pt_to_draw = (x1,y1+20*draw_dic[(x1,y1)])
            
        cv2.putText(frame, action_string[0], pt_to_draw, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=[0,255,255], thickness=1)
        draw_dic[pt_to_draw] = True
    cv2.imwrite(outpath, frame) 

def get_clips(videofile, video_id, video_extension, time_id):

    outdir_folder = os.path.join(outdir_clips, video_id)
    mkdir_p(outdir_folder)

    # ffmpeg -i a.mp4 -force_key_frames 00:00:09,00:00:12 out.mp4
    # ffmpeg -ss 00:00:09 -i out.mp4 -t 00:00:03 -vcodec copy -acodec \copy \
    # -y final.mp4 """

    clip_start = time_id - clip_time_padding - float(clip_length) / 2
    if clip_start < 0:
        clip_start = 0
    clip_end = time_id + float(clip_length) / 2

    outpath_clip = os.path.join(outdir_folder, '%d.%s' % (int(time_id), video_extension))
    #outpath_clip_tmp = outpath + '_tmp.%s' % video_extension

    ffmpeg_command = 'rm %(outpath)s;  \
                      ffmpeg -ss %(start_timestamp)s -i \
                      %(videopath)s -g 1 -force_key_frames 0 \
                      -t %(clip_length)d %(outpath)s' % {
                          'start_timestamp': hou_min_sec(clip_start * 1000),
                          # 'end_timestamp': hou_min_sec(clip_end * 1000),
                          'clip_length': clip_length + clip_time_padding,
                          'videopath': videofile,
                          'outpath': outpath_clip}

    subprocess.call(ffmpeg_command, shell=True)



anno_data, table = load_labels(annotfile)
action_name = load_action_name(actionlistfile) 

# iterate each frame in a video
for key in sorted(table):
    video_id = key[0]
    time_id = float(key[1])    
    bbox_ids = table[key]

    videofile_noext = os.path.join(videodir, video_id)
    videofile = subprocess.check_output('ls %s*' % videofile_noext, shell=True)
    videofile = videofile.split()[0]

    if sys.version > '3.0':
        videofile = videofile.decode('utf-8')
    video_extension = videofile.split('.')[-1]

    # OPEN VIDEO FOR INFORMATION IF NECESSARY
    vcap = cv2.VideoCapture(videofile) # 0=camera
    if vcap.isOpened():
        # get vcap property
        if cv2.__version__ < '3.0':
            vidwidth = vcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)   # float
            vidheight = vcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT) # float
        else:
            vidwidth = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
            vidheight = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
        # or
        # vidwidth = vcap.get(3)  # float
        # vidheight = vcap.get(4) # float
    else:
        exit(1)

    # Extract keyframe via ffmpeg
    keyfname = get_keyframe(videofile, video_id, time_id, outdir_keyframes)

    # Bbox visualization
    visual_bbox(anno_data, action_name, keyfname, video_id, time_id, bbox_ids)

    # Extract clips via ffmpeg
    get_clips(videofile, video_id, video_extension, time_id)
