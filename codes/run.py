import whisperx
import gc
import json
import os
import pandas as pd
import argparse
import warnings
import torch

print(torch.__version__)
print(torch.cuda.is_available())
warnings.filterwarnings("ignore")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Transcribe and process audio files.')
parser.add_argument('--input_dir', type=str, required=True, help='Directory containing audio files to process.')
parser.add_argument('--output_dir', type=str, required=True, help='Directory to store the results.')
parser.add_argument('--language', type=str, required=True, help='Language code for transcription.')
args = parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir
language = args.language

device = "cuda"
output_format = "all"
batch_size = 16  # reduce if low on GPU mem
compute_type = "float16"  # change to "int8" if low on GPU mem (may reduce accuracy)
HF_TOKEN = "#"

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_dir + '/raw', exist_ok=True)

# List all audio files in the input directory
audio_files = [f for f in os.listdir(input_dir) if f.endswith('.wav') or f.endswith('.flac')]

model = whisperx.load_model("large-v2", device, compute_type=compute_type, language=language)

print(model)

# Process each audio file
for audio_file in audio_files:
    # Full path to the audio file
    full_audio_path = os.path.join(input_dir, audio_file)

    # Load and process the audio file as before
    audio = whisperx.load_audio(full_audio_path)
    
    result = model.transcribe(audio, batch_size=batch_size, language=language)

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    diarize_model = whisperx.DiarizationPipeline(use_auth_token=HF_TOKEN, device=device)
    diarize_segments = diarize_model(audio, min_speakers=1, max_speakers=4)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    ## SAVING RESULTS
    file_id = audio_file.split('/')[-1].split('.')[0]

    with open(f"{output_dir}/raw/{file_id}.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"########## Processed file ID - {file_id} ##########")
