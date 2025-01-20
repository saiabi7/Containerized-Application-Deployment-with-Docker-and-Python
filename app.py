import docker
from flask import Flask, jsonify, request
import os
from docker.errors import APIError, ImageNotFound, NotFound, ContainerError, BuildError

app = Flask(__name__)

# Set Docker host
os.environ["DOCKER_HOST"] = "unix:///var/run/docker.sock"
print(f"Docker Host: {os.environ['DOCKER_HOST']}")

@app.route('/docker', methods=['POST'])
def get_image_list():
    try:
        # Initialize Docker client
        client = docker.from_env()

        # List all images
        images = client.images.list()
        image_data = []
        for image in images:
            image_data.append({"short_id": image.short_id, "tags": image.tags})

        # List all containers
        containers = client.containers.list()
        container_data = []
        for container in containers:
            container_data.append({
                "short_id": container.short_id,
                "image": container.image.tags
            })

        # Stop and remove container if it exists
        container_name = "custom-jenkins"
        try:
            container = client.containers.get(container_name)
            container.stop()
            container.remove(force=True)
        except NotFound:
            return jsonify({"status": "error", "message": f"Container {container_name} not found."}), 404
        except APIError as e:
            return jsonify({"status": "error", "message": f"Error removing container: {str(e)}"}), 500

        # Delete specific image
        image_name = "custom-jenkins"
        try:
            client.images.remove(image_name, force=True)
        except ImageNotFound:
            return jsonify({"status": "error", "message": f"Image {image_name} not found."}), 404
        except APIError as e:
            return jsonify({"status": "error", "message": f"Error deleting image: {str(e)}"}), 500

        # Build a new Docker image
        dockerfile_path = "/opt/import"
        try:
            image, logs = client.images.build(path=dockerfile_path, tag="custom-jenkins:latest")
            for log in logs:
                if 'stream' in log:
                    print(log['stream'].strip())
        except BuildError as e:
            return jsonify({"status": "error", "message": f"Failed to build the image. Error: {str(e)}"}), 500

        # Run the container
        try:
            container = client.containers.run("custom-jenkins:latest", detach=True, name="custom-jenkins")
        except ContainerError as e:
            return jsonify({"status": "error", "message": f"Failed to run the container. Error: {str(e)}"}), 500

        # Return successful response with Docker data
        return jsonify({
            "status": "success",
            "data": {
                "images": image_data,
                "containers": container_data
            }
        })

    except APIError as e:
        return jsonify({"status": "error", "message": f"Error connecting to Docker: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
