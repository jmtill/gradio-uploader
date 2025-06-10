import json
import os
import serial
import gradio as gr
from datetime import date

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "115200"))


def send_to_serial(data: dict) -> str:
    """Send JSON data over a serial connection."""
    try:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=10) as ser:
            message = json.dumps(data)
            # Add newline as delimiter
            ser.write(message.encode("utf-8") + b"\n")
        return "Data sent successfully"
    except Exception as e:
        return f"Failed to send data: {e}"


def upload(name: str, orcid: str, exp_date: str, experiment: str, json_file) -> str:
    try:
        file_content = json_file.decode("utf-8")
        json_data = json.loads(file_content)
    except Exception as e:
        return f"Invalid JSON file: {e}"

    payload = {
        "name": name,
        "orcid": orcid,
        "date": exp_date,
        "experiment": experiment,
        "data": json_data,
    }
    return send_to_serial(payload)


def default_date() -> str:
    return date.today().isoformat()


with gr.Blocks() as demo:
    gr.Markdown("## Experiment Uploader")
    name = gr.Textbox(label="Name")
    email = gr.Textbox(label="Email")
    exp_date = gr.Textbox(label="Date", value=default_date())
    experiment = gr.Textbox(label="Experiment Name")
    json_file = gr.File(label="JSON Data File", file_count="single")
    submit = gr.Button("Upload")
    output = gr.Textbox(label="Status")

    submit.click(
        upload,
        inputs=[name, email, exp_date, experiment, json_file],
        outputs=output,
    )

if __name__ == "__main__":
    demo.launch()