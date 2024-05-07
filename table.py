from PIL import Image, ImageDraw, ImageFont

# Example table data
table_data = [
    ['Type', 'Rental Value', 'Level', 'Next Redeem'],
    ['winery', '10 000', '5', 'in 2 days'],
    ['steelworks', '20 000', '5', 'in 2 days'],
    ['butchery', '10 000', '5', 'in 2 days'],
    ['winery', '10 000', '5', 'in 2 days'],
    ['winery', '10 000', '5', 'in 2 days'],
]

# Define table parameters
cell_width = 120
cell_height = 40
padding = 5
header_color = (215, 62, 46)  # Dark Orange
cell_color = (50, 50, 50)  # Dark grey
text_color = (255, 255, 255)  # White
border_color = (215, 62, 46)  # Dark Orange
header_font = ImageFont.truetype("LibreBaskerville-Bold.ttf", 14)
cell_font = ImageFont.truetype("LibreBaskerville-Regular.ttf", 12)

# Calculate image size based on table content
width = len(table_data[0]) * cell_width
height = len(table_data) * cell_height

# Add padding for the border
border_padding = 10
total_width = width + 2 * border_padding
total_height = height + 2 * border_padding

# Create image
image = Image.new('RGB', (total_width, total_height), color='white')
draw = ImageDraw.Draw(image)

# Draw border around the table
border_width = 3  # Border width
draw.rectangle([(0, 0), (total_width - 1, total_height - 1)], fill=border_color, width=border_width)

# Draw table headers with borders and styling
for i, header in enumerate(table_data[0]):
    draw.rectangle([(i * cell_width + border_padding, border_padding),
                     ((i + 1) * cell_width + border_padding, cell_height + border_padding)],
                    outline='black', fill=header_color)
    draw.text((i * cell_width + padding + border_padding, padding + border_padding), header,
              fill='white', font=header_font)

# Draw table cells with borders and styling
for i, row in enumerate(table_data[1:], start=1):
    for j, cell in enumerate(row):
        draw.rectangle([(j * cell_width + border_padding, i * cell_height + border_padding),
                         ((j + 1) * cell_width + border_padding, (i + 1) * cell_height + border_padding)],
                        outline='black', fill=cell_color)
        draw.text((j * cell_width + padding + border_padding, i * cell_height + padding + border_padding),
                  cell, fill=text_color, font=cell_font)

# Save image
image.save('table_image.png')

# Display image
image.show()
