import os
import google.generativeai as genai

default_video_path = r"C:\Users\temba\OneDrive\Desktop\Big-O notation in 5 minutes.mp4"

client = genai.configure(api_key="AIzaSyCxenYhoXs_YHzZO0hqQ9kw8xTtIARGkPM")

myfile = client.files.upload(file=default_video_path)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=[myfile, "Summarize this video. Then create a quiz with an answer key based on the information in this video."]
)

print(response.text)