from flask import Flask, request, jsonify
import docker, tarfile, io

from models import db, Image
from factory import make_app, make_celery

app = make_app()
celery = make_celery(app)

db.init_app(app)

with app.app_context():
    db.create_all()

# Required `base_image`
# Optional `packages`, `tag`
# POST /images → create a new image
@app.route("/images", methods=["POST"])
def create_image():
    data = request.json
    image = Image(
        base_image=data["base_image"],
        packages=data.get("packages", [])
    )
    db.session.add(image)
    db.session.commit()

    # Lancer le build asynchrone
    build_image.delay(image.id, data.get("tag", "latest"))

    return jsonify({"id": image.id, "status": image.status}), 201

# GET /images → list all the images available
@app.route("/images", methods=["GET"])
def list_images():
    images = Image.query.all()
    return jsonify([{
        "id": i.id,
        "base_image": i.base_image,
        "packages": i.packages,
        "status": i.status,
        "docker_tag": i.docker_tag
    } for i in images])

# GET /images/:id → get a specific image
@app.route("/images/<id>", methods=["GET"])
def get_image(id):
    image = Image.query.get_or_404(id)
    return jsonify({
        "id": image.id,
        "base_image": image.base_image,
        "packages": image.packages,
        "status": image.status,
        "docker_tag": image.docker_tag
    })


@celery.task
def build_image(image_id: str, tag: str):
    image = Image.query.get(image_id)
    if not image:
        return

    image.status = "building"
    db.session.commit()

    # Build the image
    docker_client = docker.from_env()
    dockerfile = f"""
    FROM {image.base_image}
    RUN apt-get update && apt-get install -y {' '.join(image.packages)} && rm -rf /var/lib/apt/lists/*
    CMD ["bash"]
    """
    dockerfile_bytes = dockerfile.encode("utf-8")
    dockerfile_stream = io.BytesIO()
    with tarfile.open(fileobj=dockerfile_stream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name="Dockerfile")
        tarinfo.size = len(dockerfile_bytes)
        tar.addfile(tarinfo, io.BytesIO(dockerfile_bytes))
    dockerfile_stream.seek(0)  # ptr reset

    image_name = f"container-factory/{image.id}:{tag}"

    try:
        # Build the image
        docker_image, logs = docker_client.images.build(
            fileobj=dockerfile_stream,
            custom_context=True,
            rm=True,
            tag=image_name,
            pull=True,
            encoding="utf-8"
        )

        # Stream logs (optionnal)
        for log in logs:
            if "stream" in log:
                print(log["stream"].strip())

        image.status = "ready"
        image.docker_tag = image_name
    except Exception as e:
        print(str(e))
        image.status = "failed"

    db.session.commit()

