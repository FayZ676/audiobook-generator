# Can we make the image smaller?
FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime

WORKDIR /app

# Set up system packages
RUN apt-get update && apt-get install wget ffmpeg

# Set up speech package
COPY speech ./speech
RUN cd speech && \
wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin
RUN pip install . && cd ..

# Set up generator package
COPY generator ./generator
RUN python -m spacy download en_core_web_trf
RUN pip install ./generator

CMD ["python", "-m", "generator"]
