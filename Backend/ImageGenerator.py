import asyncio
import aiohttp
import base64
from pathlib import Path
from typing import Optional, List
import os
from datetime import datetime

class AsyncImageGenerator:
    def __init__(self, api_token: str):
        """Initialize the image generator with Hugging Face API token."""
        self.api_token = api_token
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        
    async def generate_image(self, prompt: str, output_dir: str = "generated_images") -> Optional[str]:
        """
        Generate an image from a text prompt asynchronously.
        
        Args:
            prompt: Text description of the image to generate
            output_dir: Directory to save the generated image
            
        Returns:
            Path to the saved image if successful, None otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": prompt}
                ) as response:
                    if response.status != 200:
                        print(f"Error: API request failed with status {response.status}")
                        return None
                    
                    # Get the binary image data
                    image_data = await response.read()
                    
                    # Create output directory if it doesn't exist
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    
                    # Generate unique filename based on timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{output_dir}/generated_{timestamp}.png"
                    
                    # Save the image
                    with open(filename, "wb") as f:
                        f.write(image_data)
                    
                    return filename
                    
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None

    async def generate_multiple(self, prompts: List[str]) -> List[Optional[str]]:
        """
        Generate multiple images concurrently from a list of prompts.
        
        Args:
            prompts: List of text prompts to generate images from
            
        Returns:
            List of paths to saved images (None for failed generations)
        """
        tasks = [self.generate_image(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

async def main():
    # Replace with your Hugging Face API token
    api_token = "your_api_token_here"
    generator = AsyncImageGenerator(api_token)
    
    # Example prompts
    prompts = [
        "A serene mountain landscape at sunset",
        "A futuristic city with flying cars",
        "A magical forest with glowing mushrooms"
    ]
    
    print("Starting image generation...")
    results = await generator.generate_multiple(prompts)
    
    for prompt, filepath in zip(prompts, results):
        if filepath:
            print(f"Generated image for '{prompt}' saved at: {filepath}")
        else:
            print(f"Failed to generate image for '{prompt}'")

if __name__ == "__main__":
    asyncio.run(main())