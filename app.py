import gradio as gr
import torch
from PIL import Image
from diffusers import DiffusionPipeline
import random

# Initialize the base model and specific LoRA
base_model = "black-forest-labs/FLUX.1-dev"
pipe = DiffusionPipeline.from_pretrained(base_model, torch_dtype=torch.bfloat16)

lora_repo = "parth29vc/shm-v2"
trigger_word = "GN"  # Leave trigger_word blank if not used.
pipe.load_lora_weights(lora_repo)

pipe.to("cuda")

MAX_SEED = 2**32-1

def run_lora(prompt, cfg_scale, steps, randomize_seed, seed, width, height, lora_scale, progress=gr.Progress(track_tqdm=True)):
    # Set random seed for reproducibility
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    generator = torch.Generator(device="cuda").manual_seed(seed)

    # Update progress bar (0% saat mulai)
    progress(0, "Starting image generation...")

    # Generate image with progress updates
    for i in range(1, steps + 1):
        # Simulate the processing step (in a real scenario, you would integrate this with your image generation process)
        if i % (steps // 10) == 0:  # Update every 10% of the steps
            progress(i / steps * 100, f"Processing step {i} of {steps}...")

    # Generate image using the pipeline
    image = pipe(
        prompt=f"{prompt} {trigger_word}",
        num_inference_steps=steps,
        guidance_scale=cfg_scale,
        width=width,
        height=height,
        generator=generator,
        joint_attention_kwargs={"scale": lora_scale},
    ).images[0]

    # Final update (100%)
    progress(100, "Completed!")

    yield image, seed

# Example cached image and settings
example_image_path = "samples/samples_1725343907682__000001000_1.jpg"  # Replace with the actual path to the example image
example_prompt = """a digital art, an old GN walking in a jungle with his friend bhai mardana who plays  a simple stringed instrument, such as a rabab (a precursor to the sarangi)"""
example_cfg_scale = 3.2
example_steps = 32
example_width = 1152
example_height = 896
example_seed = 3981632454
example_lora_scale = 0.85

def load_example():
    # Load example image from file
    example_image = Image.open(example_image_path)
    return example_prompt, example_cfg_scale, example_steps, False, example_seed, example_width, example_height, example_lora_scale, example_image

with gr.Blocks() as app:
    gr.Markdown("# Flux RealismLora Image Generator")
    with gr.Row():
        with gr.Column(scale=3):
            prompt = gr.TextArea(label="Prompt", placeholder="Type a prompt", lines=5)
            generate_button = gr.Button("Generate")
            cfg_scale = gr.Slider(label="CFG Scale", minimum=1, maximum=20, step=0.5, value=example_cfg_scale)
            steps = gr.Slider(label="Steps", minimum=1, maximum=100, step=1, value=example_steps)
            width = gr.Slider(label="Width", minimum=256, maximum=1536, step=64, value=example_width)
            height = gr.Slider(label="Height", minimum=256, maximum=1536, step=64, value=example_height)
            randomize_seed = gr.Checkbox(False, label="Randomize seed")
            seed = gr.Slider(label="Seed", minimum=0, maximum=MAX_SEED, step=1, value=example_seed)
            lora_scale = gr.Slider(label="LoRA Scale", minimum=0, maximum=1, step=0.01, value=example_lora_scale)
        with gr.Column(scale=1):
            result = gr.Image(label="Generated Image")
            gr.Markdown("Generate images using RealismLora and a text prompt.\n[[non-commercial license, Flux.1 Dev](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md)]")

    # Automatically load example data and image when the interface is launched
    app.load(load_example, inputs=[], outputs=[prompt, cfg_scale, steps, randomize_seed, seed, width, height, lora_scale, result])
    
    generate_button.click(
        run_lora,
        inputs=[prompt, cfg_scale, steps, randomize_seed, seed, width, height, lora_scale],
        outputs=[result, seed]
    )

app.queue()
app.launch(share=True, show_error=True)