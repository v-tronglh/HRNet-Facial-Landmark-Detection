import argparse
import csv
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('datadir')
    parser.add_argument('outdir')
    parser.add_argument('anno_file')
    args = parser.parse_args()

    datadir = Path(args.datadir)
    outdir = Path(args.outdir)
    anno_file = Path(args.anno_file)

    outdir.mkdir(parents=True, exist_ok=True)

    with open(anno_file, newline='') as f:
        annos = csv.reader(f)

        # Skip header
        next(annos)

        for row in tqdm(list(annos)):
            image_name, scale, center_w, center_h, *points = row
            im_file = datadir.joinpath(image_name)
            points = [round(float(p)) for p in points]  # type: ignore
            points = [[points[i], points[i + 1]] for i in range(0, len(points), 2)]  # type: ignore

            image = cv2.imread(str(im_file))
            image = cv2.circle(image, (round(float(center_w)), round(float(center_h))), 2, (0, 255, 0), thickness=2)

            for i, point in enumerate(points):
                image = cv2.circle(image, point, 2, (0, 255, 0), thickness=2)
                image = cv2.putText(image, str(i), point, cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 0, 255), thickness=1)

            out_im_file = outdir.joinpath('_'.join(image_name.split('/')))
            cv2.imwrite(str(out_im_file), image)
