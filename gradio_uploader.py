import gradio as gr
from datetime import date
from uploader_utils import toggle_visibility, upload, default_thumbnail_path, default_data_path


with gr.Blocks() as demo:

    # Webpage Title
    gr.Markdown("## Upload Experimental Data")

    # User inputs
    with gr.Row():
        name = gr.Textbox(label="Name", scale=1)
        email = gr.Textbox(label="Email", scale=1)
        experiment = gr.Textbox(label="Experiment Name", scale=1)

        # Specifies where in the Minio database must this experiment be saved.
        minio_bucket = gr.Textbox(label="Minio Bucket")
        exp_date = gr.Textbox(label="Date", value=date.today().isoformat(), scale=1)

    # User pics one of the option, determines if path textboxes appear
    is_default = gr.Radio(["Default", "Other"], label="Default Directory",
                            info="Are you saving files to the default directory in the other computer?")

    # Path textboxes
    with gr.Row():
        data_path = gr.Textbox(label="Experiment Path",
                               placeholder=f"Default path: {default_data_path}",
                               info="Please provide full path.",
                               visible = False,
                               scale=1)

        thumbnail_path = gr.Textbox(label="Thumbnail Path",
                                    placeholder= f"Default path: {default_thumbnail_path}",
                                    info="Please provide full path.",
                                    visible = False,
                                    scale=1)

    # If is_default Radio object is changed, trigger toggle_visibility function and update path textbox visability
    is_default.change(fn=toggle_visibility, inputs=is_default, outputs=[data_path, thumbnail_path])

    # Fields where user can upload files
    with gr.Row():
        data_file = gr.File(label="Data File", file_count="single", file_types=['.json', '.csv'])
        thumbnail_file = gr.File(label="Thumbnail File", file_count="single", file_types=['.png', '.jpg', '.jpeg'])

    submit = gr.Button("Upload")

    output = gr.Textbox(label="Status")

    submit.click(
        upload,
        inputs=[name,
                email,
                exp_date,
                experiment,
                data_file,
                thumbnail_file,
                minio_bucket,
                data_path,
                thumbnail_path],
        outputs=output,
    )

demo.launch()

if __name__ == "__main__":
    demo.launch()
