from core.utils import *
from core.asr_backend.demucs_vl import demucs_audio
from core.asr_backend.audio_preprocess import process_transcription, convert_video_to_audio, split_audio, save_results, normalize_audio_volume
from core._1_ytdlp import find_video_files
from core.utils.models import *

@check_file_exists(_2_CLEANED_CHUNKS)
def transcribe():
    runtime = load_key("whisper.runtime")
    rprint(f"[bold cyan]=== ASR pipeline started | runtime={runtime} ===[/bold cyan]")

    # 1. video to audio
    video_file = find_video_files()
    rprint(f"[cyan][1/6] Input video:[/cyan] {video_file}")
    convert_video_to_audio(video_file)
    rprint(f"[green][1/6] Audio prepared:[/green] {_RAW_AUDIO_FILE}")

    # 2. Demucs vocal separation:
    if load_key("demucs"):
        rprint("[cyan][2/6] Demucs enabled, starting vocal separation...[/cyan]")
        demucs_audio()
        vocal_audio = normalize_audio_volume(_VOCAL_AUDIO_FILE, _VOCAL_AUDIO_FILE, format="mp3")
        rprint(f"[green][2/6] Vocal track ready:[/green] {vocal_audio}")
    else:
        rprint("[yellow][2/6] Demucs disabled, using raw audio directly.[/yellow]")
        vocal_audio = _RAW_AUDIO_FILE

    # 3. Extract audio
    rprint("[cyan][3/6] Splitting audio into transcription segments...[/cyan]")
    segments = split_audio(_RAW_AUDIO_FILE)
    rprint(f"[green][3/6] Audio split into {len(segments)} segment(s):[/green] {segments}")
    
    # 4. Transcribe audio by clips
    all_results = []
    if runtime == "local":
        from core.asr_backend.whisperX_local import transcribe_audio as ts
        rprint("[cyan][4/6] Transcribing audio with local WhisperX model...[/cyan]")
    elif runtime == "cloud":
        from core.asr_backend.whisperX_302 import transcribe_audio_302 as ts
        rprint("[cyan][4/6] Transcribing audio with 302 API...[/cyan]")
    elif runtime == "elevenlabs":
        from core.asr_backend.elevenlabs_asr import transcribe_audio_elevenlabs as ts
        rprint("[cyan][4/6] Transcribing audio with ElevenLabs API...[/cyan]")

    for index, (start, end) in enumerate(segments, start=1):
        rprint(f"[cyan][4/6] Segment {index}/{len(segments)}: {start:.2f}s -> {end:.2f}s[/cyan]")
        result = ts(_RAW_AUDIO_FILE, vocal_audio, start, end)
        all_results.append(result)
        rprint(f"[green][4/6] Segment {index}/{len(segments)} completed.[/green]")
    
    # 5. Combine results
    rprint("[cyan][5/6] Combining transcription results...[/cyan]")
    combined_result = {'segments': []}
    for result in all_results:
        combined_result['segments'].extend(result['segments'])
    rprint(f"[green][5/6] Combined segment count:[/green] {len(combined_result['segments'])}")
    
    # 6. Process df
    rprint("[cyan][6/6] Converting transcription results to table and saving...[/cyan]")
    df = process_transcription(combined_result)
    save_results(df)
    rprint(f"[bold green]=== ASR pipeline completed | rows={len(df)} ===[/bold green]")
        
if __name__ == "__main__":
    transcribe()