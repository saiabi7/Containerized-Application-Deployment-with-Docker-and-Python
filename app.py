import docker
import os
from docker.errors import APIError, ImageNotFound, NotFound, ContainerError, BuildError

# Set Docker host
os.environ["DOCKER_HOST"] = "unix:///var/run/docker.sock"
print(f"Docker Host: {os.environ['DOCKER_HOST']}")

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
        container_name = "custom-jenkins"
        try:
            container = client.containers.get(container_name)
            print(f"Stopping container {container_name}...")
            container.stop()
            print(f"Removing container {container_name}...")
            container.remove(force=True)
            print(f"Container {container_name} removed successfully.")
        except NotFound:
            print(f"Container {container_name} not found.")
        except APIError as e:
            print(f"Error removing container: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Delete specific image
        image_name = "custom-jenkins"
        try:
            client.images.remove(image_name, force=True)
            print(f"Successfully deleted image: {image_name}")
        except ImageNotFound:
            print(f"Image {image_name} not found.")
        except APIError as e:
            print(f"Error deleting image: {e}")

        # Build a new Docker image
        dockerfile_path = "/opt/import"
        print(f"Building the Docker image from {dockerfile_path}...")
        try:
            image, logs = client.images.build(path=dockerfile_path, tag="custom-jenkins:latest")
            for log in logs:
                if 'stream' in log:
                    print(log['stream'].strip())
            print("Image 'custom-jenkins:latest' built successfully.")
        except BuildError as e:
            print(f"Failed to build the image. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during image build: {e}")

        # Run the container
        try:
            container = client.containers.run("custom-jenkins:latest", detach=True, name="custom-jenkins")
            print(f"Container {container_name} is running successfully.")
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
