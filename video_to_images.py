import cv2
import os

def get_video_duration(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the frames per second (fps) and frame count of the input video
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the duration in seconds
    duration = frame_count / fps

    # Release the video capture object
    cap.release()

    return duration

def adjust_jpeg_quality(frame, target_size_kb, max_iterations=10):
    # Initialize the compression quality
    jpeg_quality = 85

    for _ in range(max_iterations):
        # Encode the frame with the current quality
        _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])

        # Get the size of the encoded frame in kilobytes
        size_kb = len(encoded_frame.tobytes()) / 1024

        # Print the frame size in each iteration
        print(f"Quality: {jpeg_quality}, Size: {size_kb:.2f} KB")

        # Check if the size is below the target size
        if size_kb < target_size_kb:
            return jpeg_quality
        else:
            # Adjust the quality for the next iteration
            jpeg_quality -= 5

    # If no suitable quality is found, return the default quality
    return 85

def extract_frames(video_path, output_folder, interval=0.033, target_size_kb=20, resize_factor=0.5):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the frames per second (fps) of the input video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get the video duration
    duration = get_video_duration(video_path)
    print(f"Video duration: {duration} seconds")

    # Calculate the frame interval in frames
    frame_interval = max(int(fps * interval), 1)

    # Iterate through frames at the specified interval
    for i in range(0, int(fps * duration), frame_interval):
        # Set the video capture to the desired frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)

        # Read the frame
        ret, frame = cap.read()

        # If the frame is read successfully, resize and save it with adjusted compression
        if ret:
            seconds = i / fps

            # Resize the frame
            height, width = frame.shape[:2]
            new_height = int(height * resize_factor)
            new_width = int(width * resize_factor)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            # Adjust JPEG quality based on the target file size
            jpeg_quality = adjust_jpeg_quality(resized_frame, target_size_kb)

            output_path = os.path.join(output_folder, f"frame_{seconds:.3f}.jpg")

            # Save the resized frame with adjusted compression
            cv2.imwrite(output_path, resized_frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
            
            print(f"Frame at {seconds:.3f} seconds saved to {output_path} with quality {jpeg_quality}, size: {os.path.getsize(output_path)/1024:.2f} KB")
        else:
            print(f"Error reading frame at {i / fps} seconds")

    # Release the video capture object
    cap.release()

if __name__ == "__main__":
    # Specify the input video file, output folder, and other parameters
    input_video = "graph.mov"
    output_folder = "output_frames"
    target_size_kb = 25  # Target file size in kilobytes
    resize_factor = 0.5  # Adjust the resize factor as needed

    # Call the function to extract frames every 0.033 seconds, resize, and save with adjusted compression
    extract_frames(input_video, output_folder, interval=0.033, target_size_kb=target_size_kb, resize_factor=resize_factor)
