FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-devel

RUN apt update && apt-get install -y g++ ffmpeg libsm6 libxext6
RUN apt install tmux -y
RUN apt install git -y

RUN conda install -c conda-forge -y yacs=0.1.6
RUN conda install -c conda-forge -y tqdm=4.62.0
RUN conda install -c conda-forge -y pre-commit=2.13.0
RUN conda install -c conda-forge -y tensorboardX=2.4
RUN conda install -c conda-forge -y notebook=6.4.4
RUN conda install -c conda-forge -y isort=5.9.3
RUN conda install -c conda-forge -y mypy=0.910
RUN conda install -c conda-forge -y flake8=3.9.2
RUN conda install -c conda-forge -y scipy=1.5.3

RUN pip install torch-tb-profiler==0.2.1
RUN pip install opencv-python==4.5.3.56
RUN pip install hdf5storage==0.1.18
