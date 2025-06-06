import gradio as gr


def greet(name: str, intensity: int) -> str:
    return 'Hello ' + name + '!'* intensity

demo = gr.Interface(
    fn=greet,
    inputs = ["text", gr.Slider(value=2, minimum=1, maximum=10, step=1)],
    outputs = [gr.Textbox(label="greeting", lines=3)]
)


demo.launch(share=True)