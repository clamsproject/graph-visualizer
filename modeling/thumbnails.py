from mmif import Mmif
from mmif.vocabulary.document_types import DocumentTypes
import cv2
import random


def get_vid_path(mmif):
    vid_paths = mmif.get_documents_locations(DocumentTypes.VideoDocument)
    if len(vid_paths) == 0: 
        return None
    vid_path = vid_paths[0]
    return vid_path


def get_thumbnail(mmif):
    try:
        vid_path = get_vid_path(mmif)
        cap = cv2.VideoCapture(vid_path)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        candidate_frames = random.randrange(0, total_frames, 1)

        cap.set(cv2.CAP_PROP_POS_FRAMES, candidate_frames)
        success, image = cap.read()
        if success:
            cv2.imwrite("random_frame.jpg", image)
    except Exception as e:
        print(e)
        return None

    

if __name__ == "__main__":
    with open("/home/hayden/clams/archive/local_out/whisper1.mmif", "r") as f:
        ex_mmif = Mmif(f.read())
    print(get_thumbnail(ex_mmif))