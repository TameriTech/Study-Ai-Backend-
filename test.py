# import google.generativeai as genai
# from moviepy.editor import VideoFileClip
# import whisper
# # Step 1: Extract Audio from Video
# video_path = r"C:\Users\temba\OneDrive\Desktop\Big-O notation in 5 minutes.mp4"
# audio_path = "extracted_audio.mp3"

# # Configure the client
# genai.configure(api_key="AIzaSyCxenYhoXs_YHzZO0hqQ9kw8xTtIARGkPM")

# # Create the model
# model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro'

# # Generate content
# response = model.generate_content(
#     "Please summarize the key points of this YouTube video in 3 sentences: https://www.youtube.com/watch?v=Zca5Fb2aJT0&ab_channel=AIWorkshop"
# )

# # print(response.text)



# # Load video and extract audio
# video = VideoFileClip(video_path)
# video.audio.write_audiofile(audio_path, codec='mp3')  # Saves as MP3

# # Step 2: Transcribe Audio to Text
# print("Transcribing audio... (This may take a few minutes)")
# whisper_model = whisper.load_model("base")  # Use "small", "medium", or "large" for better accuracy
# transcription = whisper_model.transcribe(audio_path)
# video_text = transcription["text"]

# print("Transcript extracted successfully!")

# # Step 3: Send to Gemini for Summary + Quiz
# genai.configure(api_key="AIzaSyCxenYhoXs_YHzZO0hqQ9kw8xTtIARGkPM")  # 🔑 Replace with your real API key

# model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro'

# prompt = f"""
# I want the the full text from this Video Transcript:
# {video_text}
# """

# response = model.generate_content(prompt)
# print("\n--- SUMMARY & QUIZ ---\n")
# print(video_text)