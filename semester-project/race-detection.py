from deepface import DeepFace
import os

image_directory = "/Users/maanitmalhan/Documents/UConn/CSE 3000/semester-project/generated images/GEMINI/BELOW AVERAGE TEACHER"
try:
    image_files = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]
except FileNotFoundError:
    print(f"Error: Directory not found at {image_directory}")
    image_files = []

image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', ".heic"))]

if not image_files:
    print(f"No image files found with common image extensions in the directory: {image_directory}")
else:
    for img_file in image_files:
        original_img_path = os.path.join(image_directory, img_file)
        print(f"\nAnalyzing image: {img_file}")

        try:
            # Analyze face, race, gender, and age
            demographics = DeepFace.analyze(img_path=original_img_path, actions=["race", "gender", "age"], enforce_detection=True)

            if isinstance(demographics, list) and len(demographics) == 1:
                face_data = demographics[0] 

                dominant_race = face_data.get('dominant_race', 'unknown')
                dominant_gender = face_data.get('dominant_gender', 'unknown')
                age = int(face_data.get('age', -1)) # Convert age to integer

                # Get the original file extension
                _, file_extension = os.path.splitext(img_file)

                # Create the new filename
                new_filename = f"{dominant_race}_{dominant_gender}_{age}{file_extension}"
                new_img_path = os.path.join(image_directory, new_filename)

                # Rename the original file
                os.rename(original_img_path, new_img_path)
                print(f"  Analysis Successful. Renamed '{img_file}' to '{new_filename}'")
                print(f"    Dominant Race: {dominant_race}, Gender: {dominant_gender}, Age: {age}")

            elif isinstance(demographics, list) and len(demographics) > 1:
                print(f"  Analysis Complete for {img_file}. Detected {len(demographics)} faces. Skipping rename as multiple faces found.")
               
        except Exception as e:
            print(f"❌ Error during analysis or no face detected in {img_file}: {e}")
            print(f"  Skipping rename for '{img_file}'.")