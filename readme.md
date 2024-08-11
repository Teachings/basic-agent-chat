**Getting Started**
====================

### Create Conda Environment

Create a new Conda environment for your project:
```bash
conda create --name mgraph python=3.12 pip
```
### Activate Environment

Activate the newly created environment:
```bash
conda activate mgraph
```
### Install Requirements

Install the required dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```
### Run the Application

Start the Uvicorn server with the following command:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
This will start the development server, listening on all available network interfaces ( `0.0.0.0` ) on port `8000`, and automatically reload when changes are detected.
