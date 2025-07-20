from flask import Flask, request, render_template
from convert import convert_to_stl
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        image = request.files.get("image")
        prompt = request.form.get("prompt")
        if not image or not prompt:
            return render_template("index.html", error="Please provide an image and prompt")
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return render_template("index.html", error="Only PNG/JPG images are supported")
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)
        print(f"Image saved at: {image_path}")
        output_path = os.path.join(STATIC_FOLDER, "output.stl")
        try:
            print(f"Calling convert_to_stl with image: {image_path}, prompt: {prompt}, output: {output_path}")
            if not os.path.exists(image_path):
                raise ValueError(f"Image not found at: {image_path}")
            result_path = convert_to_stl(image_path, prompt, output_path)
            print(f"STL generated at: {result_path}")
            if os.path.exists(result_path) and os.access(result_path, os.R_OK):
                print(f"File exists and is readable: {os.access(result_path, os.R_OK)}")
                return render_template("result.html", stl_file="output.stl")
            else:
                raise ValueError("STL file was not generated or is unreadable")
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            return render_template("index.html", error=f"Conversion failed: {str(e)}")
    return render_template("index.html", error=None)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)