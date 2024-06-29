import streamlit as st

def main():
    st.title("SVG Canvas Example")

    # JavaScript code to load SVG into the canvas
    script = """
    <script>
        // Function to load SVG into the canvas
        function loadSVG() {
            // Get the canvas element
            var canvas = document.getElementById('canvas');
            var ctx = canvas.getContext('2d');

            // Create a new image element
            var img = new Image();

            // Set the source of the image (replace 'example.svg' with your SVG file path or URL)
            img.src = 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Square_-_black_simple.svg';

            // When the image is loaded, draw it onto the canvas
            img.onload = function() {
                ctx.drawImage(img, 0, 0);
            };
        }

        // Call the function to load SVG when the window is loaded
        window.onload = loadSVG;
    </script>
    """

    # Display the canvas element
    st.components.v1.html("""
    <canvas id="canvas" width="500" height="500"></canvas>
    """ + script)
     st.sidebar.write("SVG Canvas Preview:")
    st.sidebar.write(svg_canvas(width, height, '<rect width="100%" height="100%" fill="lightgray"/>'), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
