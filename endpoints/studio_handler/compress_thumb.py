from PIL import Image
import os

async def compress_thumb(img_path, name, max_width= 720, max_height=404):
    # Open the image file
    image = Image.open(img_path)

        # Convert RGBA to RGB if needed
    if image.mode == "RGBA":
        image = image.convert("RGB")

    # Define the target size in bytes (50KB in this case)
    target_size_kb = 50

    # Initial quality setting
    quality = 80

    original_width, original_height = image.size

    # Calculate the new dimensions while maintaining aspect ratio
    if original_width > max_width or original_height > max_height:
        image.thumbnail((max_width, max_height), Image.LANCZOS)

    #Get current scripts directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the absolute path to the 'compressed_images' directory
    compressed_images_dir = os.path.join(current_dir, 'compressed_images')

    # Create the directory if it doesn't exist
    os.makedirs(compressed_images_dir, exist_ok=True)

    # Create a temporary file path for saving the compressed image
    temp_path = os.path.join(compressed_images_dir, f"{name}.jpg")

    # Perform iterative compression until the image size is less than the target size
    while True:
        # Compress the image with the current quality setting
        image.save(temp_path, quality=quality)

        # Check the size of the compressed image
        temp_size = os.path.getsize(temp_path)

        # If the size of the compressed image is less than the target size, or quality is below 50, break out of the loop
        if temp_size / 1024 < target_size_kb or quality <= 50:
            break

        # Reduce quality by 5 for the next iteration
        quality -= 5

    # If quality is at or below 50, display a message indicating that further compression cannot be done without excessive quality loss
    if quality <= 50:
        print("Can't compress further without excessive quality loss.")
    else:
        # Display some information about the final compressed image
        print("Final Compressed Image Size:", temp_size / 1024, "KB")

        # Close the original image
        image.close()

        # You may want to return the final path instead of the temporary path
        # final_compressed_image_path = "compressed_example.jpg"
        # os.rename(temp_path, final_compressed_image_path)

        # Open the final compressed image
        # final_compressed_image = Image.open(final_compressed_image_path)

        # Display the final compressed image if needed
        # final_compressed_image.show()

        # Close the final compressed image
        # final_compressed_image.close()

    return temp_path

