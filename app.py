import docker
import os
from docker.errors import APIError, ImageNotFound, NotFound, ContainerError, BuildError  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

DOCKER_HOST = os.getenv('DOCKER_HOST')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')
IMAGE_NAME = os.getenv('IMAGE_NAME')
DOCKERFILE_PATH = os.getenv('DOCKERFILE_PATH')

if not all([DOCKER_HOST, CONTAINER_NAME, IMAGE_NAME, DOCKERFILE_PATH]):
    print("Error: Missing one or more required environment variables (DOCKER_HOST, CONTAINER_NAME, IMAGE_NAME, DOCKERFILE_PATH).")
    exit(1)

os.environ["DOCKER_HOST"] = DOCKER_HOST
print(f"Docker Host: {DOCKER_HOST}")

def get_image_list():
    try:
        # Initialize Docker client
        client = docker.from_env()

        # List all images
        images = client.images.list()
        print("Available Docker Images:")
        for x in images:
            print(f"Image ID: {x.short_id}, TAGS: {x.tags}")

        # List all containers
        containers = client.containers.list()
        print("Available Docker Containers:")
        for y in containers:
            print(f"CONTAINER ID: {y.short_id}, IMAGE: {y.image.tags}")

        # Stop and remove container if it exists
        try:
            container = client.containers.get(CONTAINER_NAME)
            print(f"Stopping container {CONTAINER_NAME}...")
            container.stop()
            print(f"Removing container {CONTAINER_NAME}...")
            container.remove(force=True)
            print(f"Container {CONTAINER_NAME} removed successfully.")
        except NotFound:
            print(f"Container {CONTAINER_NAME} not found.")
        except APIError as e:
            print(f"Error removing container: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Delete specific image
        try:
            client.images.remove(IMAGE_NAME, force=True)
            print(f"Successfully deleted image: {IMAGE_NAME}")
        except ImageNotFound:
            print(f"Image {IMAGE_NAME} not found.")
        except APIError as e:
            print(f"Error deleting image: {e}")

        # Build a new Docker image
        print(f"Building the Docker image from {DOCKERFILE_PATH}...")
        try:
            image, logs = client.images.build(path=DOCKERFILE_PATH, tag=f"{IMAGE_NAME}:latest")
            for log in logs:
                if 'stream' in log:
                    print(log['stream'].strip())
            print(f"Image '{IMAGE_NAME}:latest' built successfully.")
        except BuildError as e:
            print(f"Failed to build the image. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during image build: {e}")

        # Run the container
        try:
            container = client.containers.run(f"{IMAGE_NAME}:latest", detach=True, name=CONTAINER_NAME)
            print(f"Container {CONTAINER_NAME} is running successfully.")
        except ContainerError as e:
            print(f"Failed to run the container as it exited with a non-zero exit code. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while running the container: {e}")

        return {"images": images, "containers": containers}

    except APIError as e:
        print(f"Error connecting to Docker: {e}")
        return None

if __name__ == '__main__':
    get_image_list()
