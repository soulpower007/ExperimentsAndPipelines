import pandas as pd
import os
import json


def get_adaptive_threshold(num_words, base_threshold=0.9):
    if num_words >= 10 or num_words <= 1:
        return base_threshold
    else:
        return 100 * min(base_threshold, (num_words - 1) / num_words)


def get_turn_level_results(file_path, speaker_occurrence_threshold=0.9, word_separator=" "):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = data['segments']
    raw_tsv_result = []

    #for x in segments:
    #     raw_tsv_result.append({"start": x['start'], "end": x['end'], "speaker": x['speaker'], "transcript": x['text'].strip()})

    previous_speaker = None  # Initialize a variable to hold the speaker from the previous segment

    for x in segments:
        if 'speaker' in x:
            previous_speaker = x['speaker']  # Update the previous speaker
        elif previous_speaker is None:
            previous_speaker = "SPEAKER_00"  # Assign a default value if the speaker is not found in the first segment
        raw_tsv_result.append({
            "start": x['start'],
            "end": x['end'],
            "speaker": previous_speaker,  # Use the previous speaker if 'speaker' is not present in the current segment
            "transcript": x['text'].strip()
        })


    #segments = data['segments']
    result = []

    for segment in segments:
        total_words = len(segment['words'])
        adaptive_threshold = get_adaptive_threshold(total_words, speaker_occurrence_threshold)

        # Count occurrences of each speaker
        speaker_counts = {}
        for word in segment['words']:
            speaker = word.get('speaker')
            if speaker:
                speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

        # Find the speaker with the highest occurrence
        total_words = len(segment['words'])
        dominant_speaker = None
        for speaker, count in speaker_counts.items():
            if count / total_words >= adaptive_threshold:
                dominant_speaker = speaker
                break

        if dominant_speaker:
            # If a dominant speaker is found, assign the entire segment to this speaker
            result.append({
                "start": segment['start'],
                "end": segment['end'],
                "speaker": dominant_speaker,
                "transcript": segment['text']
            })
        else:
            # If no dominant speaker, break down by individual words
            current_speaker = None
            current_start = None
            current_end = None
            transcript = ""
            for word in segment['words']:
                speaker = word.get('speaker')
                if speaker and speaker != current_speaker:
                    if current_speaker is not None:
                        result.append({
                            "start": current_start,
                            "end": current_end,
                            "speaker": current_speaker,
                            "transcript": transcript.strip()
                        })
                    current_speaker = speaker
                    current_start = word.get('start', current_end)  # Use end of last word if start is missing
                    transcript = word['word']
                else:
                    # Append word to the current speaker's transcript
                    transcript += word_separator + word['word']
                current_end = word.get('end', current_end)  # Update end time

            # Append the last speaker's segment
            if current_speaker is not None:
                result.append({
                    "start": current_start,
                    "end": current_end,
                    "speaker": current_speaker,
                    "transcript": transcript.strip()
                })

    for i in range(len(result)):
        result[i]['transcript'] = result[i]['transcript'].strip()

    return result, raw_tsv_result


def combine_speaker_turns(segments, turn_level_threshold=1.0, word_separator=" "):
    combined_results = []
    current_segment = None

    for segment in segments:
        if current_segment and segment['speaker'] == current_segment['speaker']:
            if segment['start'] - current_segment['end'] <= turn_level_threshold:
                # Combine with the current segment
                current_segment['end'] = segment['end']
                current_segment['transcript'] += word_separator + segment['transcript']
            else:
                # Append the current segment and start a new one
                combined_results.append(current_segment)
                current_segment = segment
        else:
            # Append the current segment (if exists) and start a new one
            if current_segment:
                combined_results.append(current_segment)
            current_segment = segment

    # Append the last segment
    if current_segment:
        combined_results.append(current_segment)

    return combined_results


def main(output_path, directory_path=None, file_paths=None, speaker_occurrence_threshold=0.9, turn_level_threshold=1.0, word_separator=" "):
    if directory_path is None and file_paths is None:
        print("directory_path and file_paths both cannot be none!")
        return
    if directory_path is not None and file_paths is not None:
        print("directory_path and file_paths both cannot be assigned a value!")
        return
    if directory_path:
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist!")
            return
        file_paths = [f"{directory_path}/{x}" for x in os.listdir(directory_path) if os.path.isfile(f"{directory_path}/{x}") and x.endswith('.json')]
    elif file_paths:
        if not isinstance(file_paths, list):
            print(f"file_paths must be a list and not {type(file_paths)}!")
            return
        if file_paths == []:
            print(f"file_paths cannot be empty list!")
            return
        file_paths_not_found = [x for x in file_paths if not os.path.isfile(x)]
        if len(file_paths_not_found) > 0:
            print(f"{len(file_paths_not_found)} out of {len(file_paths)} not found! Post processing remaining {len(file_paths) - len(file_paths_not_found)} files ...")
        file_paths = [x for x in file_paths if os.path.isfile(x)]

    os.makedirs(output_path, exist_ok=True)
    os.makedirs(f"{output_path}/raw_tsv", exist_ok=True)
    os.makedirs(f"{output_path}/segmented_tsv", exist_ok=True)
    os.makedirs(f"{output_path}/processed_tsv", exist_ok=True)

    for i in range(len(file_paths)):
        try:
          raw_json = file_paths[i]
          file_id = raw_json.split('/')[-1].split('.')[0]
          #print(f"{file_id}", end=" ")
          #print(file_id)
          turn_level_results, raw_tsv_result = get_turn_level_results(file_path=raw_json,
                                                      speaker_occurrence_threshold=speaker_occurrence_threshold,
                                                      word_separator=word_separator)

          df = pd.DataFrame(raw_tsv_result)
          df.to_csv(f"{output_path}/raw_tsv/{file_id}.tsv", sep='\t', index=False)

          df = pd.DataFrame(turn_level_results)
          df.to_csv(f"{output_path}/segmented_tsv/{file_id}.tsv", sep='\t', index=False)

          combined_spk_turn_results = combine_speaker_turns(turn_level_results,
                                                            turn_level_threshold=turn_level_threshold,
                                                            word_separator=word_separator)

          df = pd.DataFrame(combined_spk_turn_results)
          df.to_csv(f"{output_path}/processed_tsv/{file_id}.tsv", sep='\t', index=False)

          if i % 100 == 0:
              print(f"Post-processed {i} out of {len(file_paths)} {file_id}")
        except:
            print(f"Ignoring file id {file_id}")

#output_path = "/scratch/sb9179/datasets/callhome_jap/segstore/train_pip_op/"
#directory_path = "/scratch/sb9179/datasets/callhome_jap/segstore/train_pip_op/raw
output_path = "/scratch/projects/pichenylab/sb9179/Rall/missing/missing_files/outputs/"
directory_path = "/scratch/projects/pichenylab/sb9179/Rall/missing/missing_files/outputs/raw/"

#file_paths = []
file_paths = None
speaker_occurrence_threshold = 0.9
turn_level_threshold = 1.0
word_separator = ""

main(output_path, directory_path, file_paths, speaker_occurrence_threshold, turn_level_threshold, word_separator)


