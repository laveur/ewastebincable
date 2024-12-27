import argparse
import logging
import os
import shlex
import subprocess

from dataclasses import dataclass

WHITELISTED_EXTENSIONS = [
    '.m4v',
    '.mp4',
    '.mov',
    '.mkv',
    '.avi'
]

BITRATE_MAX = "17M"
BITRATE_AVG = "5M"
BITRATE_MIN = "1M"
PACKET_SIZE = "2000"
BURST_BITS = "60000000"
BITRATE_UDP = "60000000"

@dataclass
class BroadcastInfo():
    broadcast_address: str
    broadcast_port: str
    service_name: str
    service_provider: str
    include_subtitles: bool


def broadcast_media(filename: str, broadcast_info: BroadcastInfo):
    filter = f'scale=1920:1080:force_original_aspect_ratio=decrease,pad=width=1920:height=1080:x=(ow-iw)/2:y=(oh-iw)/2:color=black'

    if broadcast_info.include_subtitles:
        filter += f',subtitles={shlex.quote(filename)}'
    
    ffmpeg_cmd = [
        # Base Command
        'ffmpeg', '-re', '-i',
        filename,
        # Scale to 1080p, preserving aspect ratio, and letter boxing
        '-filter_complex', filter,
        #'-filter_complex', f'',
        # Output MPEG Transport Stream, with broadcast name
        '-f', 'mpegts', '-metadata', f'service_name={broadcast_info.service_name}', '-metadata', f'service_provider={broadcast_info.service_provider}',
        # Output Video
        '-c:v', 'mpeg2video', '-b:v', BITRATE_AVG, '-minrate', BITRATE_MIN, '-maxrate', BITRATE_MAX, '-qscale:v', '2',
        # Output Audio
        '-c:a', 'ac3', '-ar', '44100',
        # Output Destination
        f'udp://{broadcast_info.broadcast_address}:{broadcast_info.broadcast_port}?pkt_size={PACKET_SIZE}?bitrate={BITRATE_UDP}&burst_bits={BURST_BITS}'
    ]

    logging.info(f'Playing Media File: {filename}')
    logging.debug(f'Playback Command: {' '.join(ffmpeg_cmd)}')

    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--broadcast_addr", required=True, help="IP address to broadcast to")
    parser.add_argument("--broadcast_port", required=True, help="Port to broadcast to")
    parser.add_argument("--service_name", help="The Name of your Channel")
    parser.add_argument("--service_provider", help="The cable provider")
    parser.add_argument("--media_dir", action="append", required=True, help="Media Directory")
    parser.add_argument("--randomized", action="store_true", help="Randomize the files")
    parser.add_argument("--include_subtitles", action="store_true", help="Include Subtitles. Note only use this if you are sure all files have subtitle tracks.")
    parser.add_argument('--debug', action="store_true", help="Print FFMPEG commands")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(format='%(levelname)7s: %(module)16s:%(lineno)-3d %(message)s', level=log_level)

    if args.include_subtitles:
        logging.info("Note: Playback performance will be greatly decreased with subtitle playback")

    media_files = []
    for media_dir in args.media_dir:
        files = os.listdir(media_dir)

        if not args.randomized:
            files.sort()

        for file in files:
            _, ext = os.path.splitext(file)

            if ext in WHITELISTED_EXTENSIONS:
                media_files.append(media_dir + os.sep + file)

    for media_file in media_files:
        media = BroadcastInfo(args.broadcast_addr, args.broadcast_port, args.service_name, args.service_provider, args.include_subtitles)
        broadcast_media(media_file, media)
    