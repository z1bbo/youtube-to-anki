"""
This module contains the main function for converting YouTube videos to Anki decks.
"""

from typing import Dict, Iterable

import click
import cv2
from pydub import AudioSegment

from youtube_to_anki.anki import make_package as _make_package
from youtube_to_anki.utils import process_audio_chunk, take_screenshots, process_transcript_chunk
from youtube_to_anki.youtube import retrieve_audio, retrieve_video, retrieve_info, retrieve_transcript


def make_package(
    transcript: Iterable[Dict], audio: AudioSegment, video: cv2.VideoCapture, deck_name: str, filepath: str, buffer_ms: int
):
    """
    Creates an Anki package from audio and transcript.
    """
    transcript_chunks = tuple(process_transcript_chunk(chunk) for chunk in transcript)
    screenshots = take_screenshots(video, transcript_chunks)
    audio_chunks = tuple(
        process_audio_chunk(audio, chunk, buffer_ms) for chunk in transcript_chunks
    )
    _make_package(audio_chunks, screenshots, transcript_chunks, deck_name, hash(deck_name), filepath)


# pylint: disable=no-value-for-parameter
@click.command()
@click.option(
    "--out",
    default=None,
    help="Where to export the deck. Defaults to '<deck_name>.apgk'.",
)
@click.option(
    "--transcript-language",
    "-L",
    default="en",
    help="Which transcript language to use. Defaults to 'en'.",
)
@click.option(
    "--buffer-ms",
    "-B",
    default=100,
    help="Audio buffer (ms) before and after subtitle timing, to prevent cutoff. Defaults to 100.",
)
@click.option(
    "--resolution",
    "-R",
    default=360,
    help="Video resolution (p). Defaults to 360.",
)
@click.argument("video-id")
def main(
    video_id: str,
    transcript_language: str,
    buffer_ms: int,
    resolution: int,
    out: str,
):
    """
    Converts a YouTube video into an Anki deck.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    transcript = retrieve_transcript(video_id, transcript_language)
    video = retrieve_video(url, resolution)
    audio = retrieve_audio(url)
    deck_name = retrieve_info(video_id)
    out = out or f"{deck_name}.apkg"
    make_package(transcript, audio, video, deck_name, out, buffer_ms)


if __name__ == "__main__":
    main()
