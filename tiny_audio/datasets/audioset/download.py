from pathlib import Path
import subprocess
import shutil

from ffmpeg import FFmpeg, FFmpegError


def download_yt_audio_clip(
    ytid: str, start: float, end: float, save_path: Path, timeout: int = 60, sample_rate: int = 16000
) -> int:
    """Download a YouTube audio clip and extract a segment from it.

    Args:
        ytid (str): YouTube video ID.
        start (float): Start time of the segment.
        end (float): End time of the segment.
        save_path (Path): Path to save the audio clip.
        timeout (int, optional): Timeout for the subprocesses. Defaults to 60.
        sample_rate (int, optional): Sample rate of the audio clip. Defaults to 16000.

    Returns:
        int: Return code of the subprocesses.

    """

    dst_path = save_path / f"{ytid}.wav"
    tmp_path = save_path / f"{ytid}_tmp.wav"

    # Download full audio clip
    try:
        subprocess.run(
            [
                "youtube-dl",
                f"https://youtube.com/watch?v={ytid}",
                "--quiet",
                "--extract-audio",
                "--audio-format",
                "wav",
                "--output",
                f"{save_path}/{ytid}.%(ext)s",
            ],
            check=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as err:
        return err.returncode
    except subprocess.TimeoutExpired as err:
        return 1

    # Extract the audio clip
    try:
        cmd = (
            FFmpeg()
            .input(dst_path)
            .output(
                tmp_path,
                ss=start,
                to=end,
                ar=sample_rate,
            )
        )
        cmd.execute()
    except FFmpegError as err:
        return 2
    except subprocess.TimeoutExpired as err:
        return 1

    # Move the extracted audio clip
    shutil.move(tmp_path, dst_path)

    return 0
