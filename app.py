from flask import Flask, request, jsonify
import time, random

from models import db, Image
from factory import make_app, make_celery

app = make_app()
celery = make_celery(app)

db.init_app(app)

with app.app_context():
    db.create_all()

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
    build_image.delay(image.id)

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
def build_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return

    image.status = "building"
    db.session.commit()

    # Build simulation
    # TODO: build the image
    time.sleep(5)
    if random.random() < 0.9:
        image.status = "ready"
        image.docker_tag = f"container-factory/{image.id}:latest"
    else:
        image.status = "failed"

    db.session.commit()

