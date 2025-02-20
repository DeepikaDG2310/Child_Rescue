from gooey import Gooey, GooeyParser
import os
import numpy as np
import cv2
from glob import glob
import sys
from scenedetect import open_video, SceneManager, ContentDetector,save_images
from Katna.video import Video
from Katna.writer import KeyFrameDiskWriter


def create_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print(f"ERROR: creating directory with name {path}")

def save_frame(video_path, save_dir, gap):
    name = video_path.split("/")[-1].split(".")[0]
    save_path = os.path.join(save_dir, name,"extract")
    create_dir(save_path)

    cap = cv2.VideoCapture(video_path)
    idx = 0

    while True:
        ret, frame = cap.read()

        if ret == False:
            cap.release()
            break

        if idx == 0:
            cv2.imwrite(f"{save_path}/{(idx/30)}.png", frame)
        else:
            if idx % gap == 0:
                cv2.imwrite(f"{save_path}/{(idx/30)}.png", frame)

        idx += 1

def pyscenedetect(video_path, save_dir):
    name = video_path.split("/")[-1].split(".")[0]
    save_path = os.path.join(save_dir, name,"pyscene")
    create_dir(save_path)
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    scene_manager.detect_scenes(video)
    scenes = scene_manager.get_scene_list()
    save_images(scenes,video,output_dir=save_path)

def Keydetect(video_path, save_dir, a):
    name = video_path.split("/")[-1].split(".")[0]
    save_path = os.path.join(save_dir, name,"keyscene")
    create_dir(save_path)
    vd = Video()

    # number of images to be returned
    no_of_frames_to_returned = a

    # initialize diskwriter to save data at desired location
    diskwriter = KeyFrameDiskWriter(location=save_path)

    # extract keyframes and process data with diskwriter
    vd.extract_video_keyframes(
       no_of_frames=no_of_frames_to_returned, file_path=video_path,
       writer=diskwriter)


def do_stuff(args=None):
    print(f"The file you chose is {args.file_path}")
    print(f"The folder you chose is {args.directory_path}")
    print(args.filteroption)
    print(args.number)
    video_paths = glob(args.file_path + "/*")
    save_dir = args.directory_path
    if(args.filteroption[0] == 'Extraction'):
        if(int(args.number[0]) <= 0):
            a = 5
        else:
            a = int(args.number[0])
        a = a * 30
        for path in video_paths:
            save_frame(path, save_dir, gap=a)
    elif(args.filteroption[0] == 'Pyscene detection'):
        for path in video_paths:
            pyscenedetect(path, save_dir)
    elif(args.filteroption[0] == 'Keyframe detection'):
        for path in video_paths:
            a = 0
            if(int(args.number[0]) <= 0):
                a = 20
            else:
                a = int(args.number[0])
            Keydetect(path, save_dir, a)
    print("All done!")


@Gooey(program_name="Image Extracter",
    program_description="Extract and Detect Frames",
    default_size=(600, 500),)
def main():
    gp = GooeyParser()
    gp.add_argument(
        "-a",
        "--file_path",
        metavar="Input",
        help="Choose an input folder",
        widget="DirChooser",
    )

    gp.add_argument(
        "-b",
        "--directory_path",
        metavar="Output",
        help="Choose an output folder",
        widget="DirChooser",
    )

    gp.add_argument(
        '--filteroption', choices=['Extraction', 'Keyframe detection','Pyscene detection'],
        help='Type of service',
        widget='Listbox',
        required=True,
        nargs='*'
        # default='sku'
    )
    gp.add_argument(
        '--number',
        help='Extraction: How many second for each frame / Keyframe detection: How many frames to be detected',
        widget='IntegerField',
        nargs='*'
    )
    args = gp.parse_args()
    do_stuff(args)

if __name__ == '__main__':
    main()