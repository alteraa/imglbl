import os
import random
import shutil
import functools
import gradio as gr
from pathlib import Path

CHOICE_TO_DIR = {
    "Class A": Path("class_a"),
    "Class B": Path("class_b"),
    "Discard": Path("discard"),
}


def get_images():
    """Get all images from original_images directory"""
    return [
        f
        for f in os.listdir("original_images")
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
    ]


def print_reamining_images(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        remaining_images = get_images()
        print(f"Remaining images: {len(remaining_images)}")
        return result

    return wrapper


def get_random_image():
    """Get a random image from original_images directory"""
    images = get_images()
    if len(images) == 0:
        raise gr.Error("No images found!")
    img_path = os.path.join("original_images", random.choice(images))
    return img_path, img_path


@print_reamining_images
def process_image(choice, current_img_path):
    """Process the image based on user's choice"""
    current_img_path = Path(current_img_path)
    target_img = CHOICE_TO_DIR[choice] / current_img_path.name
    if not current_img_path.is_file():
        return get_random_image()
    shutil.move(str(current_img_path), str(target_img))
    return get_random_image()


# Create the Gradio interface
with gr.Blocks() as app:
    gr.HTML("<h1 style='text-align: center;'>Image Labeling</h1>")

    # Container for centering everything
    with gr.Column(elem_classes="center-container"):
        # Image container
        with gr.Column(elem_classes="image-container"):
            image = gr.Image(
                label="Current Image",
                height=400,
                width=400,
                show_label=False,
                container=False,
            )
            image_path = gr.Textbox(visible=False)  # Hidden textbox to store image path

    # Load event to get a random image when the app starts
    app.load(fn=get_random_image, inputs=None, outputs=[image, image_path])

    # Button container
    with gr.Row(equal_height=True, variant="panel", elem_classes="button-container"):
        btn_a = gr.Button("Class A", size="sm")
        btn_b = gr.Button("Class B", size="sm")
        btn_discard = gr.Button("Discard", size="sm")

    # Read custom CSS from file
    with open("style.css", "r") as f:
        custom_css = f"<style>{f.read()}</style>"
        # Add custom CSS
        gr.HTML(custom_css)

    # Connect buttons to the processing function
    btn_a.click(
        fn=process_image,
        inputs=[gr.Textbox(value="Class A", visible=False), image_path],
        outputs=[image, image_path],
    )
    btn_b.click(
        fn=process_image,
        inputs=[gr.Textbox(value="Class B", visible=False), image_path],
        outputs=[image, image_path],
    )
    btn_discard.click(
        fn=process_image,
        inputs=[gr.Textbox(value="Discard", visible=False), image_path],
        outputs=[image, image_path],
    )

# Launch the application
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7000, max_threads=40)
