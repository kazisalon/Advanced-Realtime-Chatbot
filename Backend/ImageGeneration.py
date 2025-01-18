import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Add debug directory check
if not os.path.exists("Data"):
    print("Creating Data directory")
    os.makedirs("Data")
else:
    print("Data directory exists")


# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = r"Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    print(f"Looking for images with prompt: {prompt}")
    print(f"In folder: {os.path.abspath(folder_path)}")

    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError as e:
            print(f"Unable to open {image_path}. Error: {str(e)}")


API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}


async def query(payload):
    print(f"Making API request with payload: {payload}")
    try:
        response = await asyncio.to_thread(
            requests.post, API_URL, headers=headers, json=payload
        )
        print(f"API Response Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"API Error Response: {response.text}")
            return None
        return response.content
    except Exception as e:
        print(f"API request failed: {str(e)}")
        return None


# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    print(f"Starting image generation for prompt: {prompt}")
    tasks = []

    # Create 4 image generation tasks
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }

        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    print("Waiting for API responses...")
    image_bytes_list = await asyncio.gather(*tasks)

    success_count = 0
    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                file_path = rf"Data\{prompt.replace(' ', '_')}{i + 1}.jpg"
                print(f"Saving image {i+1} to: {file_path}")
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                success_count += 1
            except Exception as e:
                print(f"Error saving image {i+1}: {str(e)}")

    print(f"Successfully generated and saved {success_count} images")
    return success_count > 0


# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    print(f"Starting GenerateImages for prompt: {prompt}")
    try:
        success = asyncio.run(
            generate_images(prompt)
        )  # Run the async image generation function
        if success:
            open_images(prompt)  # Open the generated images
        return success
    except Exception as e:
        print(f"Error in GenerateImages: {str(e)}")
        return False


# Main loop to monitor for image generation requests
print("Starting main loop...")
while True:
    try:
        # Read the status and prompt from the data file
        data_file_path = r"..\frontend\Files\ImageGeneration.data"
        print(f"Checking data file at: {os.path.abspath(data_file_path)}")

        with open(data_file_path, "r") as f:
            Data: str = f.read()

        print(f"Read data: {Data}")
        Prompt, Status = Data.split(",")
        print(f"Prompt: {Prompt}, Status: {Status}")

        # If the status indicates an image generation request
        if Status == "True":
            print("Generating Images ...")
            ImageStatus = GenerateImages(prompt=Prompt)

            # Reset the status in the file after generating images
            print("Updating status file...")
            with open(data_file_path, "w") as f:
                f.write("False,False")
            print("Status file updated")
            break  # Exit the loop after processing the request

        else:
            sleep(1)  # Wait for 1 second before checking again

    except Exception as e:
        print(f"Error in main loop: {str(e)}")
        sleep(1)
