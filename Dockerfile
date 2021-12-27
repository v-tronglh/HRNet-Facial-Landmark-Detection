FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-devel

RUN apt-get clean
RUN apt-get update --fix-missing && apt-get install -y g++ ffmpeg libsm6 libxext6
RUN apt install tmux -y
RUN apt install git -y
RUN apt install vim -y

RUN conda install -c conda-forge -y yacs=0.1.6 tqdm=4.62.0 pre-commit=2.13.0 tensorboardX=2.4 notebook=6.4.4 isort=5.9.3 mypy=0.910 flake8=3.9.2 scipy=1.5.3

RUN pip install opencv-python==4.5.3.56
RUN pip install hdf5storage==0.1.18
