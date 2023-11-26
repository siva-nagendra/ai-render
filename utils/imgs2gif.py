from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import cv2
import imageio
import os

# functions
def clip_video(video, start_time, end_time):
    target_name = "clipped_" + str(video)
    ffmpeg_extract_subclip(video, start_time, end_time, targetname=target_name)
    return target_name

def video_to_gif(video, interval, duration, fps):
    vidcap = cv2.VideoCapture(video)
    num_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) # frames of video

    if interval != 0:
        num_frames_to_pick = duration / interval
    else:
        num_frames_to_pick = num_frames # pick all frames

    if num_frames_to_pick < num_frames:
        duration_pic = int(num_frames / num_frames_to_pick)
    else:
        duration_pic = 1

    success, image = vidcap.read() # read image from video
    images = []
    count = 1

    while success:
        if (count % duration_pic == 0):
            images.append(image)
        success, image = vidcap.read()
        count += 1
    images_to_gif(images, fps)

def images_to_gif(imgs, frame_rate, output_filename='output'):
    imageio.mimsave(output_filename+'.gif', imgs, fps=frame_rate)  # save images to gif

def load_images_from_folder(folder):
    images = []

    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images
