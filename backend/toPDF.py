# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# def save_transcript_to_pdf(transcript_text, file_path):
#     # Create a PDF file
#     c = canvas.Canvas(file_path, pagesize=letter)
    
#     # Set font and size
#     c.setFont("Helvetica", 12)

#     # Split transcript text into paragraphs
#     paragraphs = transcript_text.split('\n\n')

#     # Write each paragraph to the PDF
#     for i, paragraph in enumerate(paragraphs):
#         c.drawString(72, 800 - i * 12, paragraph)

#     # Save the PDF file
#     c.save()


# # import os
# # from fpdf import FPDF

# # def save_summary_as_pdf(summary, filename):
# #     # Create instance of FPDF class
# #     pdf = FPDF()

# #     # Add a page
# #     pdf.add_page()

# #     # Set style and size of font
# #     pdf.set_font("Arial", size=12)

# #     # Add the summary to the PDF
# #     pdf.multi_cell(0, 10, txt=summary)

# #     # Get the current working directory
# #     current_directory = os.getcwd()

# #     # save the pdf with name .pdf
# #     pdf.output("GFG.pdf")   

# #     # # Save the PDF in the current working directory
# #     # pdf.output(os.path.join(current_directory, f"Senior\\LASER-main\\backend\\uploads\\Accounts_images\\{filename}.pdf"))

