# Docker factory

> [!WARNING]
> This project is only made for educational purposes. This is not by any means ready for deployement.

## Setup

In order to setup this project you'll need docker up and running on your local machine.
You can use the following commands to build and start the project:

```console
$ docker compose build
$ docker compose up -d
```

To turn off the system use:

```console
$ docker compose down
```

## Specification

You have access to several request to the API. By default the API is accesssible on port 8989, feel free to change it inside the `docker-compose.yml` file.

#### Creating new docker images

<details>
  <summary><code>POST</code> <code><b>/images</b></code> <code>create a new docker image with the given configuration</code></summary>

  ##### Parameters
  
  > | name      |  type     | data type               | description                                                                                                |
  > |-----------|-----------|-------------------------|------------------------------------------------------------------------------------------------------------|
  > | None      |  required | object (JSON)           | The configuration of the image to create `{"base_image": required, "packages": optional, "tag": optional}` |

  ##### Responses

  > | http code     | content-type                      | response                                                            |
  > |---------------|-----------------------------------|---------------------------------------------------------------------|
  > | `201`         | `application/json`                | `{"id": uuid, "status": "pending"}`                                 |

  ##### Example curl command

  > ```command
  > $ curl -X POST http://localhost:8989/images \
  >     -H "Content-Type: application/json" \
  >     -d '{
  >        "base_image": "ubuntu:22.04",
  >        "packages": ["python3", "curl"]
  >     }'
  > ```
</details>

#### Get the detail of images

<details>
  <summary><code>GET</code> <code><b>/images</b></code> <code>list all available images</code></summary>

  ##### Parameters

  > None  

  ##### Responses

  > | http code     | content-type                      | response                                                                                             |
  > |---------------|-----------------------------------|------------------------------------------------------------------------------------------------------|
  > | `200`         | `application/json`                | `[]{"id": uuid, "base_image": string, "docker_tag": string, "packages": []string, "status": string}` |

  ##### Example curl command

  > ```command
  > $ curl -X GET http://localhost:8989/images
  > ```
</details>


<details>
  <summary><code>GET</code> <code><b>/images/{uuid}</b></code> <code>get the status of a specific image</code></summary>

  ##### Parameters

  > | name   |  type      | data type      | description                                                  |
  > |--------|------------|----------------|--------------------------------------------------------------|
  > | `uuid` |  required  | uuid           | The specific image unique idendifier                         | 

  ##### Responses

  > | http code     | content-type                      | response                                                                                           |
  > |---------------|-----------------------------------|----------------------------------------------------------------------------------------------------|
  > | `200`         | `application/json`                | `{"id": uuid, "base_image": string, "docker_tag": string, "packages": []string, "status": string}` |

  ##### Example curl command

  > ```command
  > $ curl -X GET http://localhost:8989/images/eaf62131-6a62-4c6c-9b94-c66cfde2d49a
  > ```
</details>
