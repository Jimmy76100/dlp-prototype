# dlp-prototype
Data Loss Prevention (DLP) System Prototype

A prototype Data Loss Prevention (DLP) system, written in Python, designed to monitor and protect sensitive data across two critical channels:

Endpoint (Data-at-Rest): A lightweight agent watches the file system. When a file containing sensitive data (like a credit card number) is created or modified, the agent automatically moves it to a secure quarantine.

Network (Data-in-Motion): A network proxy intercepts outgoing HTTP uploads. If a file being uploaded contains sensitive data, the upload is blocked, and a 403 Forbidden error is returned to the user.

This project was built to explore the core challenges of data classification (using RegEx and Luhn checks) and policy enforcement in a real-world, multi-component system.

System Architecture

The system runs as three separate, concurrent components:

Central Server (server/app.py)

A Flask server that acts as the central logging and administrative hub.

The endpoint agent sends "violation" logs to this server (not fully implemented, but the API endpoint exists).

Status: (Terminal 1)

Endpoint Agent (endpoint_agent/agent.py)

A watchdog-based script that monitors a specified folder (e.g., Desktop or Downloads).

Uses textract to read file contents and detector/detectors.py to scan for patterns.

Action: Quarantines sensitive files upon detection.

Status: (Terminal 2)

Network Proxy (network_proxy/mitm_addon.py)

An mitmproxy addon script that inspects all outgoing network traffic.

Parses multipart/form-data uploads to find file content.

Uses detector/detectors.py to scan the content.

Action: Blocks the HTTP request with a 403 error if a match is found.

Status: (Terminal 3)

How to Run

You will need 3-4 separate terminal/PowerShell windows to run all components.

1. Initial Setup

Clone the repository and cd into the dlp-prototype directory.

Create a Python virtual environment:

python -m venv venv


Activate the environment. (This is required for every terminal you open).

On Windows PowerShell: You must first allow local scripts for this terminal session:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process


Then, activate:

.\venv\Scripts\Activate


Install all the required dependencies:

pip install -r requirements.txt


2. Configure Local Paths

Before running, you must edit the endpoint_agent/agent.py script to set your local test paths.

Open endpoint_agent/agent.py.

Change these two variables to point to real, existing folders on your machine:

path_to_watch = r"C:\Users\YourUser\Desktop\dlp_test_folder"
QUARANTINE_DIR = r"C:\Users\YourUser\Desktop\dlp_quarantine"


3. Run the System

Important: Each of these must be run in a new terminal, and you must activate the venv (.\venv\Scripts\Activate) in each one.

🟢 Terminal 1: Start the Central Server

(venv) PS> cd server
(venv) PS> python app.py


(Leave this running. It will host the logger at http://127.0.0.1:5000)

🔵 Terminal 2: Start the Endpoint Agent

(venv) PS> python -m endpoint_agent.agent


(Leave this running. It will print "Agent started..." and wait.)

🟡 Terminal 3: Start the Network Proxy

(venv) PS> mitmproxy -s network_proxy/mitm_addon.py


(Leave this running. It will open the mitmproxy TUI and wait for traffic.)

How to Test

Once all three terminals are running, you can test the system.

1. Generate Test Data

First, run the test-data generator in a fourth terminal (remember to activate the venv).

(venv) PS> python tests/generate_dataset.py


(This creates tests/dataset/positive and tests/dataset/negative folders.)

2. Test the Endpoint Agent

Open your Windows File Explorer.

Navigate to tests/dataset/positive.

Copy the file pos_0.txt.

Navigate to the folder you are watching (e.g., C:\Users\YourUser\Desktop\dlp_test_folder).

Paste the file.

Observe Terminal 2: You will see it print Processing..., Matches found: {'CREDIT_CARD_LUHN': ...}, and Quarantined file.... The file will disappear from your test folder.

3. Test the Network Proxy

Go back to your fourth terminal.

Run the following curl.exe command to simulate a file upload through the proxy:

curl.exe -x [http://127.0.0.1:8080](http://127.0.0.1:8080) -F "file=@tests/dataset/positive/pos_0.txt" [http://httpbin.org/post](http://httpbin.org/post)


Observe Terminal 4: The command will fail and print: Blocked by DLP: Sensitive data detected in file upload.

Observe Terminal 3: You will see the debug output !! DLP VIOLATION FOUND !! and a 403 Forbidden status on the request.

Project Structure

dlp-prototype/
├─ README.md
├─ requirements.txt
├─ detector/
│  ├─ detectors.py         # RegEx/Luhn detection logic
│  └─ extractor.py         # textract wrapper
├─ endpoint_agent/
│  └─ agent.py             # Filesystem monitor (watchdog)
├─ network_proxy/
│  └─ mitm_addon.py        # Network monitor (mitmproxy)
├─ policy/
│  └─ policies.json        # (Future use) Policy rules
├─ server/
│  └─ app.py               # Central logger (Flask)
└─ tests/
   ├─ generate_dataset.py  # Creates test files
   └─ dataset/             # (storage for test files)
