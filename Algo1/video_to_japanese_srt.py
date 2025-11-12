#!/usr/bin/env python3
"""
video_to_japanese_srt.py
Ekstrak audio dari video -> transcribe (Whisper) -> translate ke Jepang -> keluarkan SRT
Usage:
    python video_to_japanese_srt.py input_video.mp4 output_ja.srt
Optional:
    add --burn to produce out_with_subs.mp4 (requires ffmpeg)
"""

import sys
import os
import subprocess
import tempfile
import datetime
import argparse
from tqdm import tqdm

# whisper
import whisper
import srt

# translator
from googletrans import Translator

def extract_audio(video_path, out_wav_path, sample_rate=16000):
    # gunting audio mono 16k (lebih baik untuk ASR)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", str(sample_rate),
        "-f", "wav", out_wav_path
    ]
    print("Menjalankan ffmpeg untuk ekstrak audio...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Audio diekstrak ke:", out_wav_path)

def srt_timestamp(seconds):
    # srt expects datetime.timedelta
    return datetime.timedelta(seconds=float(seconds))

def translate_texts(texts, dest="ja"):
    translator = Translator()
    results = []
    print("Menerjemahkan segmen ke bahasa Jepang...")
    for t in tqdm(texts):
        # googletrans sometimes rate-limits; simple retry loop
        for attempt in range(3):
            try:
                trans = translator.translate(t, dest=dest)
                results.append(trans.text)
                break
            except Exception as e:
                if attempt == 2:
                    # fallback: keep original
                    results.append(t)
                else:
                    # small wait and retry
                    import time
                    time.sleep(1.0)
    return results

def transcribe_and_generate_srt(audio_path, model_name="small", translate_to_ja=True, srt_path="output_ja.srt"):
    print(f"Loading Whisper model '{model_name}' (ini bisa memakan RAM/GPU)...")
    model = whisper.load_model(model_name)

    print("Transcribing audio (Whisper)...")
    # task default is 'transcribe'; we want transcription in source language (auto-detect)
    result = model.transcribe(audio_path, verbose=False)  # result contains 'segments'
    segments = result.get("segments", [])

    if not segments:
        print("Tidak ada segmen yang dihasilkan. Pastikan audio valid.")
        return

    # kumpulkan teks asli per segmen
    orig_texts = [seg["text"].strip() for seg in segments]
    # optionally translate
    if translate_to_ja:
        translated = translate_texts(orig_texts, dest="ja")
    else:
        translated = orig_texts

    # compose SRT
    subs = []
    for i, seg in enumerate(segments, start=1):
        start = srt_timestamp(seg["start"])
        end = srt_timestamp(seg["end"])
        content = translated[i-1]
        # SRT isi sebaiknya batasi panjang baris per subtitle
        # kita juga bisa memecah long lines jadi 2 baris agar lebih nyaman dibaca:
        max_len = 42
        if len(content) > max_len:
            # break at nearest space
            words = content.split()
            line1 = ""
            line2 = ""
            for w in words:
                if len(line1) + len(w) + 1 <= max_len:
                    line1 = (line1 + " " + w).strip()
                else:
                    line2 = (line2 + " " + w).strip() if line2 else w
            content = line1 + ("\n" + line2 if line2 else "")
        subs.append(srt.Subtitle(index=i, start=start, end=end, content=content))

    srt_content = srt.compose(subs)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print("SRT disimpan di:", srt_path)
    return srt_path

def burn_subtitles_to_video(original_video, srt_path, out_video):
    # ffmpeg burn subtitles (but needs srt to be compatible; if non-ascii, ensure encoding ok)
    # We will use subtitles filter which supports UTF-8 if ffmpeg built with libass
    cmd = [
        "ffmpeg", "-y", "-i", original_video,
        "-vf", f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24'",
        "-c:a", "copy", out_video
    ]
    print("Membakar subtitle ke video (ffmpeg)...")
    subprocess.run(cmd, check=True)
    print("Video hasil dengan subtitle:", out_video)

def main():
    parser = argparse.ArgumentParser(description="Extract audio -> transcribe -> translate to Japanese -> output SRT")
    parser.add_argument("input_video", help="path to input video (mp4, mkv, etc.)")
    parser.add_argument("output_srt", help="path to output srt (e.g., output_ja.srt)")
    parser.add_argument("--model", default="small", help="Whisper model to use (tiny, base, small, medium, large)")
    parser.add_argument("--no-translate", action="store_true", help="jika diset, jangan terjemahkan (hanya transcribe)")
    parser.add_argument("--burn", action="store_true", help="burn subtitle ke video (menghasilkan out_with_subs.mp4)")
    args = parser.parse_args()

    if not os.path.exists(args.input_video):
        print("File input tidak ditemukan:", args.input_video)
        sys.exit(1)

    # gunakan temp file audio
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "extracted_audio.wav")
        try:
            extract_audio(args.input_video, audio_path, sample_rate=16000)
        except subprocess.CalledProcessError:
            print("Error saat mengekstrak audio. Pastikan ffmpeg terinstal dan file video valid.")
            sys.exit(1)

        try:
            srt_path = transcribe_and_generate_srt(
                audio_path,
                model_name=args.model,
                translate_to_ja=(not args.no_translate),
                srt_path=args.output_srt
            )
        except Exception as e:
            print("Error saat transcribe/translate:", e)
            sys.exit(1)

        if args.burn:
            out_video = os.path.splitext(os.path.basename(args.input_video))[0] + "_with_ja_subs.mp4"
            try:
                burn_subtitles_to_video(args.input_video, srt_path, out_video)
            except subprocess.CalledProcessError:
                print("Error saat burn subtitles. Cek apakah ffmpeg support libass/ass subtitles.")
                sys.exit(1)

if __name__ == "__main__":
    main()
