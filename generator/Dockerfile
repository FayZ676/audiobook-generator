FROM pytorch/pytorch:2.7.0-cuda11.8-cudnn9-runtime

WORKDIR /app

# Set up speech package
COPY speech ./speech
RUN cd speech && \
wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin
RUN pip install -e . && cd ..

# Set up generator package
COPY generator ./generator
RUN python -m spacy download en_core_web_trf
RUN pip install -e ./generator

CMD ["python", "-m", "generator"]
