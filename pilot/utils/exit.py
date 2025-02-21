# exit.py
import os
import hashlib
import requests

from helpers.cli import terminate_running_processes
from utils.questionary import styled_text


def send_telemetry(path_id):
    # Prepare the telemetry data
    telemetry_data = {
        "pathId": path_id,
        "event": "pilot-exit"
    }

    try:
        response = requests.post("https://api.pythagora.io/telemetry", json=telemetry_data)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to send telemetry data: {err}")


def send_feedback(feedback, path_id):
    """Send the collected feedback to the endpoint."""
    # Prepare the feedback data (you can adjust the structure as per your backend needs)
    feedback_data = {
        "pathId": path_id,
        "data": feedback,
        "event": "pilot-feedback"
    }

    try:
        response = requests.post("https://api.pythagora.io/telemetry", json=feedback_data)
        response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to send feedback data: {err}")


def get_path_id():
    # Calculate the SHA-256 hash of the installation directory
    installation_directory = os.path.abspath(os.path.join(os.getcwd(), ".."))
    return hashlib.sha256(installation_directory.encode()).hexdigest()


def ask_to_store_prompt(project, path_id):
    init_prompt = project.main_prompt if project is not None and project.main_prompt else None
    if init_prompt is None:
        return

    # Prepare the prompt data
    telemetry_data = {
        "pathId": path_id,
        "event": "pilot-prompt",
        "data": init_prompt
    }
    question = ('We would appreciate if you let us store your initial app prompt. If you are OK with that, please just '
                'press ENTER')

    try:
        answer = styled_text(project, question, ignore_user_input_count=True)
        if answer == '':
            response = requests.post("https://api.pythagora.io/telemetry", json=telemetry_data)
            response.raise_for_status()
    except requests.RequestException as err:
        print(f"Failed to store prompt: {err}")


def ask_user_feedback(project, path_id, ask_feedback):
    question = ('How did GPT Pilot do? Were you able to create any app that works? Please write any feedback you have '
                'or just press ENTER to exit:')
    feedback = None
    if ask_feedback:
        feedback = styled_text(project, question, ignore_user_input_count=True)
    if feedback:  # only send if user provided feedback
        send_feedback(feedback, path_id)


def exit_gpt_pilot(project, ask_feedback=True):
    terminate_running_processes()
    path_id = get_path_id()

    send_telemetry(path_id)

    ask_to_store_prompt(project, path_id)

    ask_user_feedback(project, path_id, ask_feedback)

    print('Exit', type='exit')
