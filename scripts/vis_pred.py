import argparse
import csv
from pathlib import Path

import cv2
import torch
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('out_dir')
    parser.add_argument('prediction')
    parser.add_argument('anno_file')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    preds = torch.load(args.prediction, map_location='cpu')

    with open(args.anno_file, newline='') as f:
        annos = csv.reader(f)
        rows = list(annos)
        rows = rows[1:]

        for row, pred in tqdm(zip(rows, preds)):
            image_name = row[0]
            im_file = data_dir.joinpath(image_name)
            points = pred.round().to(torch.int32)
            image = cv2.imread(str(im_file))

            for i, point in enumerate(points):
                image = cv2.circle(image, (point[0].item(), point[1].item()), 2, (0, 255, 0), thickness=2)
                image = cv2.putText(image, str(i), (point[0].item(), point[1].item()), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 255),
                                    thickness=1)

            out_im_file = out_dir.joinpath('_'.join(image_name.split('/')))
            cv2.imwrite(str(out_im_file), image)
