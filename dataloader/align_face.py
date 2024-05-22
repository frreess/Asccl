import cv2
import glob
import numpy as np
import os
import face_alignment
import torch

from PIL import Image, ImageFilter
from scipy import ndimage
from scipy.ndimage import gaussian_filter1d
from skimage import io
from torchvision import transforms, utils
from tqdm import tqdm
import ffmpeg
from tqdm import tqdm
import concurrent.futures
from multiprocessing import Pool

# Align faces
def align_frames(fa, img_dir, save_dir, num, expand_ratio=0.1):
    os.makedirs(save_dir, exist_ok=True)
    img_list = sorted(os.listdir(img_dir))
    lms = []

    for idx, img_name in tqdm(enumerate(img_list)):
        name = str(int(img_name.split(".")[0])-1).zfill(6)
        try:
            img_path = os.path.join(img_dir, img_name)
            img = cv2.resize(cv2.imread(img_path), (224, 224))
            preds = fa.get_landmarks(img) 
            preds = np.array(preds)[0]
            x_min, y_min, w, h = cv2.boundingRect(preds.astype(np.int32))
            x_cop = int(x_min - expand_ratio * w)
            y_crop = int(y_min - expand_ratio * h)
            w_crop = int(w * (1 + 2 * expand_ratio))
            h_cop = int(h * (1 + 2 * expand_ratio))
            crop_bbox = [x_cop, y_crop, x_cop + w_crop, y_crop + h_cop]
            img = cv2.resize((img[crop_bbox[1]:crop_bbox[3],crop_bbox[0]:crop_bbox[2],:]), (512, 512))
            cv2.imwrite(f"{save_dir}/{name}.jpg", img)
            lms.append(preds)
        except Exception as e:
            print(f"error {e}")
            with open("ttt.txt", "a") as file:
                file.write(img_path+"\n")


    
if __name__ == "__main__":
    
        
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=True, device='cuda')
    root = "path/to/MEAD"
    emotion_list = ["angry", "contempt", "disgusted", "fear", "happy", "neutral", "sad", "surprised"]

    vid_list = sorted(os.listdir(root))
    for vid in vid_list:
        for emotion in emotion_list:
            emotion_path = os.path.join(root, vid, "img", emotion)
            path_sub = sorted(os.listdir(emotion_path))
            for idx, sub in enumerate(path_sub):
                emotion_sub_path = os.path.join(emotion_path, sub)
                save_path = emotion_sub_path.replace("img", "align_img")
                align_frames(fa, emotion_sub_path, save_path, None)
