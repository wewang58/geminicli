# Gemini CLI for HyperShift

This repository contains custom commands and scripts for the Gemini CLI, specifically tailored for HyperShift development and testing workflows.

## Overview

The `geminicli` project provides a set of automated commands that can be invoked through the Gemini CLI interface. These commands streamline common tasks like building binaries, creating container images, and testing pull requests.

## Available Commands

### `/build-pr`

**Primary Function:** Automated tool to build HyperShift components (CLI, images, operators) directly from a Pull Request and optionally push them to a container repository.

#### Options

- `--cli`: Build `hypershift` CLI.
- `--hcp`: Build `hcp` CLI (product CLI).
- `--operator`: Build `hypershift-operator` binary.
- `--cpo`: Build `control-plane-operator` binary.
- `--operator-image`: Build `hypershift-operator` container image.
- `--cpo-image`: Build `control-plane-operator` container image.
- `--all`: Build everything.
- `--tag <tag>`: Set image tag (default: `latest`).
- `--push`: Push built images to a registry.
- `--operator-name <name>`: Set `hypershift-operator` image name.
- `--cpo-name <name>`: Set `control-plane-operator` image name.
- `--pr <id>`: Checkout a specific PR before building (e.g., `--pr 1234`).

#### Usage Examples

1.  **Build CLI and operator image**:
    ```bash
    /build-pr --cli --operator-image
    ```

2.  **Build everything with a specific tag**:
    ```bash
    /build-pr --all --tag my-feature
    ```

3.  **Build with custom image names**:
    ```bash
    /build-pr --operator-image --operator-name my-reg/hypershift-operator --tag v1.0
    ```

4.  **Build a specific PR**:
    ```bash
    /build-pr --pr 1234 --all
    ```

5.  **Build and push images to a repository**:
    ```bash
    /build-pr --pr 1234 --operator-image --push --operator-name quay.io/my-user/hypershift-operator --tag test-v1
    ```

## Repository Structure

- `.gemini/commands/`: Contains the Gemini command definitions (`.toml` files) and their associated logic.
- `hack/`: Contains helper scripts and implementation logic for the commands.

## Getting Started

To use these commands, ensure you have the Gemini CLI installed and configured to point to this repository's root directory.

## Contributing

To add a new command:
1.  Create a new `.toml` definition in `.gemini/commands/`.
2.  Implement the command logic in a script within `hack/` or directly in the `.toml` if simple.
3.  Update the documentation as needed.