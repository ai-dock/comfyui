[![Docker Build](https://github.com/ai-dock/comfyui/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ai-dock/comfyui/actions/workflows/docker-build.yml)

# AI-Dock + ComfyUI Docker Image

Run [ComfyUI](https://github.com/comfyanonymous/ComfyUI) in a cloud-first AI-Dock container.

>[!NOTE]
>These images do not bundle models or third-party configurations. You should use a [provisioning script](https://github.com/ai-dock/base-image/wiki/4.0-Running-the-Image#provisioning-script) to automatically configure your container. You can find examples in `config/provisioning`.

## Documentation

All AI-Dock containers share a common base which is designed to make running on cloud services such as [vast.ai](https://link.ai-dock.org/vast.ai) and [runpod.io](https://link.ai-dock.org/template) as straightforward and user friendly as possible.

Common features and options are documented in the [base wiki](https://github.com/ai-dock/base-image/wiki) but any additional features unique to this image will be detailed below.

#### Version Tags

The `:latest` tag points to `:latest-cuda`

Tags follow these patterns:

##### _CUDA_
- `:pytorch-[pytorch-version]-py[python-version]-cuda-[x.x.x]-base-[ubuntu-version]`

- `:latest-cuda` &rarr; `:pytorch-2.2.0-py3.10-cuda-11.8.0-base-22.04`

- `:latest-cuda-jupyter` &rarr; `:jupyter-pytorch-2.2.0-py3.10-cuda-11.8.0-base-22.04`

##### _ROCm_
- `:pytorch-[pytorch-version]-py[python-version]-rocm-[x.x.x]-runtime-[ubuntu-version]`

- `:latest-rocm` &rarr; `:pytorch-2.2.0-py3.10-rocm-5.7-runtime-22.04`

- `:latest-rocm-jupyter` &rarr; `:jupyter-pytorch-2.2.0-py3.10-rocm-5.7-runtime-22.04`

##### _CPU_
- `:pytorch-[pytorch-version]-py[python-version]-ubuntu-[ubuntu-version]`

- `:latest-cpu` &rarr; `:pytorch-2.2.0-py3.10-cpu-22.04` 

- `:latest-cpu-jupyter` &rarr; `:jupyter-pytorch-2.2.0-py3.10-cpu-22.04` 

Browse [here](https://github.com/ai-dock/comfyui/pkgs/container/comfyui) for an image suitable for your target environment.

Supported Python versions: `3.11`, `3.10`

Supported Pytorch versions: `2.2.0`, `2.1.2`

Supported Platforms: `NVIDIA CUDA`, `AMD ROCm`, `CPU`


## Additional Environment Variables

| Variable                 | Description |
| ------------------------ | ----------- |
| `AUTO_UPDATE`            | Update ComfyUI on startup (default `true`) |
| `COMFYUI_BRANCH`         | ComfyUI branch/commit hash (default `master`) |
| `COMFYUI_FLAGS`          | Startup flags. eg. `--gpu-only --highvram` |
| `COMFYUI_PORT_HOST`      | ComfyUI interface port (default `8188`) |
| `COMFYUI_URL`            | Override `$DIRECT_ADDRESS:port` with URL for ComfyUI |

See the base environment variables [here](https://github.com/ai-dock/base-image/wiki/2.0-Environment-Variables) for more configuration options.

### Additional Micromamba Environments

| Environment    | Packages |
| -------------- | ----------------------------------------- |
| `comfyui`      | ComfyUI and dependencies |

This micromamba environment will be activated on shell login.

See the base micromamba environments [here](https://github.com/ai-dock/base-image/wiki/1.0-Included-Software#installed-micromamba-environments).

## Additional Services

The following services will be launched alongside the [default services](https://github.com/ai-dock/base-image/wiki/1.0-Included-Software) provided by the base image.

### ComfyUI

The service will launch on port `8188` unless you have specified an override with `COMFYUI_PORT_HOST`.

ComfyUI will be updated to the latest version on container start. You can pin the version to a branch or commit hash by setting the `COMFYUI_BRANCH` variable.

You can set startup flags by using variable `COMFYUI_FLAGS`.

To manage this service you can use `supervisorctl [start|stop|restart] comfyui`.


### ComfyUI RP API

This service is available on port `8188` and is used to test the [RunPod serverless](https://link.ai-dock.org/runpod-serverless) API.

You can access the api directly at `/rp-api/runsync` or you can use the Swager/openAPI playground at `/rp-api`.

There are several [example payloads](https://github.com/ai-dock/comfyui/tree/main/build/COPY_ROOT/opt/serverless/docs/example_payloads) included in this repository.

This API is available on all platforms - But the container can ony run in serverless mode on RunPod infrastructure.

To learn more about the serverless API see the [serverless section](#runpod-serverless)

<details>
  <summary>API Playground</summary>
    <br>
    <img src="https://raw.githubusercontent.com/ai-dock/comfyui/main/.github/images/api1.png">
</details>

>[!NOTE]
>All services are password protected by default. See the [security](https://github.com/ai-dock/base-image/wiki#security) and [environment variables](https://github.com/ai-dock/base-image/wiki/2.0-Environment-Variables) documentation for more information.

## Pre-Configured Templates

**Vast.​ai**

- [comfyui:latest](https://link.ai-dock.org/template-vast-comfyui)

- [comfyui:latest-jupyter](https://link.ai-dock.org/template-vast-comfyui-jupyter)

---

**Runpod.​io**

- [comfyui:latest](https://link.ai-dock.org/template-runpod-comfyui)

- [comfyui:latest-jupyter](https://link.ai-dock.org/template-runpod-comfyui-jupyter)

---

## RunPod Serverless

The container can be used as a [RunPod serverless](https://link.ai-dock.org/runpod-serverless) worker.  To enable serverless mode you must run the container with environment variables `SERVERLESS=true` and `WORKSPACE=/runpod-volume`.

The handlers will accept a job, process it and upload your images to s3 compatible storage.

You may either set your s3 credentials as environment variables or you can pass them to the worker in the payload.

You should set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL` and `AWS_BUCKET_NAME`.

<details>
  <summary>Serverless template example</summary>
    <br>
    <img src="https://raw.githubusercontent.com/ai-dock/comfyui/main/.github/images/runpod-template.png">
</details>

If passed in the payload these variables should be in lowercase.

Incorrect or unset s3 credentials will not resut in job failure. You can still retrieve your images from the network volume.

When used in serverless mode, the container will skip provisioning and will not update ComfyUI or the nodes on start so you must either ensure everyting you need is built into the image (see [Building Images](#building-images)) or first run the container with a network volume in GPU Cloud to get everything set up before launching your workers.

After launching a serverless worker, any instances of the container launched on the network volume in GPU cloud will also skip auto-updating. All updates must be done manually.

The API is documented in openapi format. You can test it in a running container on the ComfyUI port at `/rp-api/docs` - See [ComfyUI RP API](#comfyui-rp-api) for more information.

---

The API can use multiple handlers which you may define in the payload. Three handlers have been included for your convenience

### Handler: RawWorkflow

This handler should be passed a full ComfyUI workflow in the payload.  It will detect any URL's and download the files into the input directory before replacing the URL value with the local path of the resource.  This is very useful when working with image to image and controlnets.

This is the most flexible of all handlers.

<details>
  <summary>RawWorkflow schema</summary>
    <br>
    <img src="https://raw.githubusercontent.com/ai-dock/comfyui/main/.github/images/api-schema-rawworkflow.png">
    <br>
    <a target="_blank" href="https://raw.githubusercontent.com/ai-dock/comfyui/main/build/COPY_ROOT/opt/serverless/docs/example_payloads/raw_controlnet_t2i_adapters.json">Example payload</a>
</details>


### Handler: Text2Image

This is a basic handler that is bound to a static workflow file (`/opt/serverless/workflows/text2image.json`).

You can define several overrides to modify the workflow before processing.

<details>
  <summary>Text2Image schema</summary>
    <br>
    <img src="https://raw.githubusercontent.com/ai-dock/comfyui/main/.github/images/api-schema-text2image.png">
    <br>
    <a target="_blank" href="https://raw.githubusercontent.com/ai-dock/comfyui/main/build/COPY_ROOT/opt/serverless/docs/example_payloads/bound_text2image.json">Example payload</a>

</details>

### Handler: Image2Image

This is a basic handler that is bound to a static workflow file (`/opt/serverless/workflows/image2image.json`).

You can define several overrides to modify the workflow before processing. 

<details>
  <summary>Image2Image schema</summary>
  <br>
  <img src="https://raw.githubusercontent.com/ai-dock/comfyui/main/.github/images/api-schema-text2image.png">
  <br>
  <a target="_blank" href="https://raw.githubusercontent.com/ai-dock/comfyui/main/build/COPY_ROOT/opt/serverless/docs/example_payloads/bound_image2image.json">Example payload</a>
</details>

These handlers demonstrate how you can create a simple endpoint which will require very little frontend work to implement.

You can find example payloads for these handlers [here](https://github.com/ai-dock/comfyui/tree/main/build/COPY_ROOT/opt/serverless/docs/example_payloads)

---


_The author ([@robballantyne](https://github.com/robballantyne)) may be compensated if you sign up to services linked in this document. Testing multiple variants of GPU images in many different environments is both costly and time-consuming; This helps to offset costs_