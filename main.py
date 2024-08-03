from pytubefix import YouTube
import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, AudioFileClip
import os

def get_video(root):
    url = url_entry.get()
    yt = YouTube(url)
    streams = yt.streams

    tk.Label(root, text="Select format").pack(pady=10)
    format_var = tk.StringVar(root)
    format_menu = tk.OptionMenu(root, format_var, "MP3", "VIDEO")
    format_menu.pack(pady=5)
    format_var.set("MP3")

    resolution_var = tk.StringVar(root)
    resolution_menu = None
    download_button = None

    def on_format_change(*args):
        nonlocal resolution_menu, download_button
        format_choice = format_var.get()
        
        for widget in root.winfo_children():
            if isinstance(widget, (tk.OptionMenu, tk.Label)) and widget != format_menu:
                widget.pack_forget()

        if format_choice == "VIDEO":
            video_streams = streams.filter(file_extension='mp4', adaptive=True)
            resolutions = sorted(set([stream.resolution for stream in video_streams if stream.resolution]))
            
            resolution_label = tk.Label(root, text="Choose resolution")
            resolution_label.pack(pady=10)
            resolution_var.set("")

            resolution_menu = tk.OptionMenu(root, resolution_var, *resolutions)
            resolution_menu.pack(pady=5)
            
        else:
            resolution_var.set("")
            resolution_menu = None

        if download_button:
            download_button.pack_forget()

        download_button = tk.Button(root, text="Download", command=download)
        download_button.pack(pady=20)

    format_var.trace_add("write", on_format_change)
    
    def download():
        format_choice = format_var.get()
        download_path = filedialog.askdirectory()
        if not download_path:
            status_label.config(text="Download failed", fg="red")
            return

        if format_choice == "VIDEO":
            resolution = resolution_var.get()
            video_stream = yt.streams.filter(res=resolution, mime_type="video/mp4", adaptive=True).first()
            audio_stream = yt.streams.filter(only_audio=True, adaptive=True).first()
            
            if video_stream and audio_stream:
                video_path = video_stream.download(output_path=download_path, filename_prefix="video_")
                audio_path = audio_stream.download(output_path=download_path, filename_prefix="audio_")
                merge_video_audio(video_path, audio_path, download_path + "/" + yt.title + ".mp4")
                try:
                    os.remove(video_path)  # Sil
                    os.remove(audio_path)  # Sil
                except Exception as e:
                    status_label.config(text=f"Error deleting files: {e}", fg="red")
                else:
                    status_label.config(text="Download and merge completed", fg="green")
            else:
                status_label.config(text="Download failed", fg="red")
        
        else:
            stream = yt.streams.filter(only_audio=True).first()
            if stream:
                stream.download(output_path=download_path, filename_prefix="audio_")
                status_label.config(text="Download completed", fg="green")
            else:
                status_label.config(text="Download failed", fg="red")
        
    def merge_video_audio(video_path, audio_path, output_path):
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(output_path, codec='libx264')

    status_label = tk.Label(root, text="")
    status_label.pack(pady=10)
    
root = tk.Tk()
root.title("YouTube Downloader")

tk.Label(root, text="Enter YouTube URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Choose video", command=lambda: get_video(root)).pack(pady=20)
url_status = tk.Label(root, text="")
url_status.pack(pady=10)

root.mainloop()