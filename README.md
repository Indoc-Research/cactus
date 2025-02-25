# 🚀 ***Research Pods* Proof-of-Concept (PoC)**
Welcome to *cactus*, our Research Pod Proof-of-Concept repository! This project is - for the most part - the outcome of a 2-day hackathon of the Indoc Research Europe gGmbH team, and it showcases what we call "Research Pods". In a nutshell, Research Pods enable the on-demand deployment, configuration, and management of customizable, cloud-based JupyterHub environments, designed to streamline research software (RS) usage and development.

## 🌟 Overview
Research Pods are scalable, secure, and customizable computing environments that enable researchers to:

- Seamlessly access and use research software with pre-configured compute resources.
- Define and install custom RS stacks by linking to public repositories.
- Maintain full control over resource management, including pod creation and deletion.

This PoC showcases the automated deployment of Research Pods on GDPR-compliant European cloud infrastructure ([Exoscale](https://www.exoscale.com/)) and demonstrates their flexibility in supporting various research needs.

## 🎬 Demonstrations
Below, you’ll find three video recordings that illustrate the key functionalities of Research Pods.



### 1️⃣ Deploying a Research Pod from pre-configured RS stacks

<video src="./media/ResearchPod_Creation_demo.mp4" width="768" height="432" controls></video>

This demo showcases:
- Selecting from predefined RS stacks.
- Configuring compute resources (CPU, RAM, GPU).
- Automatically launching a secure JupyterHub instance on Exoscale.
- Accessing the pod via GitHub authentication.


### 2️⃣ Deploying a Research Pod with custom RS from a public repository

<video src="./media/ResearchPod_custom_RS.mp4" width="768" height="432" controls></video>

This demo illustrates:
- Provisioning a Research Pod with a custom RS sourced from a GitHub repository URL.
- Automating the validation and quality assurance process before installation.


### 3️⃣ Deleting Research Pods for efficient cost management

<video src="./media/ResearchPod_deletion_demo.mp4" width="768" height="432" controls></video>

This demo highlights:
- Deleting previously created Research Pods.
- Freeing up resources to control costs and manage quotas.
- Ensuring efficient cleanup of compute environments.


## ⚙️ Key Features
- Dynamic JupyterHub deployment on cloud infrastructure.
- Customizable research software installation from predefined stacks or public repositories.
- Automated decommissioning for efficient cost management.

## 📌 Next Steps
We hope to secure funding to continue with the full implementation of Research Pods that we envision. Stay tuned for updates!