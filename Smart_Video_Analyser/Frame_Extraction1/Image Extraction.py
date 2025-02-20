from gooey import Gooey, GooeyParser
import os
import numpy as np
import cv2
from glob import glob
import sys
from scenedetect import open_video, SceneManager, ContentDetector,save_images
from Katna.video import Video
from Katna.writer import KeyFrameDiskWriter
from skimage.metrics import structural_similarity as ssim
from concurrent.futures import ProcessPoolExecutor


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

def HVS_Hist(video_path, output_folder, threshold=0.5, frame_skip=10): 
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    video = cv2.VideoCapture(video_path)
    ret, prev_frame = video.read()
    
    if not ret:
        print("Error: Unable to read the video.")
        return
    
    frame_count = 0
    key_frame_count = 0

    prev_hist = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
    prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Process every nth frame
        if frame_count % frame_skip == 0:
            hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)

            if similarity < threshold:
                cv2.imwrite(f"{output_folder}/key_frame_{key_frame_count:04d}.jpg", frame)
                key_frame_count += 1
                prev_hist = hist  # Update previous histogram

        frame_count += 1
    
    video.release()

def calculate_histogram(frame):
    # Convert frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Calculate histogram and normalize it
    hist = cv2.calcHist([hsv_frame], [0, 1], None, [16, 16], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist

def compare_histograms(hist1, hist2, threshold=0.3):
    # Compare histograms using correlation
    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return correlation < threshold

def shot_boundary_detection_color(video_path, output_folder, threshold=30, similarity_threshold=0.5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video = cv2.VideoCapture(video_path)
    ret, prev_frame = video.read()
    if not ret:
        print("Failed to read video.")
        return []

    shot_boundaries = []
    frame_count = 0
    last_saved_hist = None

    while True:
        ret, curr_frame = video.read()
        if not ret:
            break

        # Compute the absolute difference between frames
        frame_diff = cv2.absdiff(curr_frame, prev_frame)
        mean_diff = np.mean(frame_diff)

        if mean_diff > threshold:
            shot_boundaries.append(frame_count)
            #print(f"Shot boundary detected at frame: {frame_count}")

            # Calculate histogram for current frame
            curr_hist = calculate_histogram(curr_frame)

            # Check if current histogram is similar to the last saved histogram
            if last_saved_hist is not None:
                if compare_histograms(curr_hist, last_saved_hist, threshold=similarity_threshold):
                    #print(f"Frame {frame_count} is similar to last saved frame; skipping save.")
                    continue
                else:
                    frame_filename = os.path.join(output_folder, f"shot_boundary_frame_{frame_count:04d}.jpg")
                    cv2.imwrite(frame_filename, curr_frame)
                    last_saved_hist = curr_hist  # Update last saved histogram
                    #print(f"Saved frame: {frame_filename}")
            else:
                # Save the first detected shot boundary frame
                frame_filename = os.path.join(output_folder, f"shot_boundary_frame_{frame_count:04d}.jpg")
                cv2.imwrite(frame_filename, curr_frame)
                last_saved_hist = curr_hist  # Update last saved histogram
                #print(f"Saved frame: {frame_filename}")

        # Update previous frame
        prev_frame = curr_frame
        frame_count += 1

    video.release()

def extract_frames(video_path, frame_skip=5):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    for frame_num in range(0, total_frames, frame_skip):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            break
        yield frame_num, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    cap.release()

def compare_frames_batch(keyframe, frames_batch, threshold):
    return [ssim(keyframe, frame, data_range=255) > threshold for frame in frames_batch]

def save_keyframe(output_dir, i, frame_num, frame):
    output_path = os.path.join(output_dir, f'keyframe_{i:04d}_frame_{frame_num:06d}.jpg')
    cv2.imwrite(output_path, frame)

def extract_keyframes(video_path, output_dir, similarity_threshold=0.7, frame_skip=5, batch_size=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frames = extract_frames(video_path, frame_skip)
    keyframes = []
    current_keyframe = None
    frames_batch = []
    frame_nums_batch = []

    with ProcessPoolExecutor() as executor:
        for frame_num, frame in frames:
            if current_keyframe is None:
                current_keyframe = frame
                keyframes.append((frame_num, frame))
                save_keyframe(output_dir, len(keyframes) - 1, frame_num, cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))
                continue

            frames_batch.append(frame)
            frame_nums_batch.append(frame_num)

            if len(frames_batch) == batch_size:
                results = executor.submit(compare_frames_batch, current_keyframe, frames_batch, similarity_threshold).result()
                
                for i, is_similar in enumerate(results):
                    if not is_similar:
                        new_keyframe = frames_batch[i]
                        keyframes.append((frame_nums_batch[i], new_keyframe))
                        save_keyframe(output_dir, len(keyframes) - 1, frame_nums_batch[i], cv2.cvtColor(new_keyframe, cv2.COLOR_GRAY2BGR))
                        current_keyframe = new_keyframe

                frames_batch = []
                frame_nums_batch = []

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
    elif(args.filteroption[0] == 'HVS Histogram'):
        for path in video_paths:
            t = 0.6
            if (int(args.number[0]) <= 0):
                a = 0.6
            else:
                a = int(args.number[0])
                
            HVS_Hist(path, save_dir,t,a)
    elif(args.filteroption[0] == 'Shot Boundary detection'):
        for path in video_paths:
            save_path = os.path.join(save_dir, 'SBD',"extract")
            t = 35
            s_t = 0.5
            if (int(args.number[0]) <= 0):
                a = 0.6
            else:
                a = int(args.number[0])
                
            shot_boundary_detection_color(path,save_path,t,s_t)
    
    elif(args.filteroption[0] == 'SSIM'):
        for path in video_paths:
            save_path = os.path.join(save_dir, 'SSIM',"extract")
            t = 35
            s_t = 0.5
            if (int(args.number[0]) <= 0):
                a = 0.6
            else:
                a = int(args.number[0])
                
            extract_keyframes(path,save_path)

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
        '--filteroption', choices=['Extraction', 'Keyframe detection','Pyscene detection','HVS Histogram','Shot Boundary detection','SSIM'],
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