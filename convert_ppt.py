import os
import sys

try:
    import comtypes.client
except ImportError:
    import subprocess
    print("Installing comtypes...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes"])
    import comtypes.client

def pptx_to_pdf(pptx_path, pdf_path):
    pptx_path = os.path.abspath(pptx_path)
    pdf_path = os.path.abspath(pdf_path)
    
    print(f"Opening PowerPoint to convert {pptx_path}...")
    try:
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        # Minimize window or keep it invisible if possible, but visible=True is safer on Windows
        powerpoint.Visible = 1 
        
        deck = powerpoint.Presentations.Open(pptx_path)
        deck.SaveAs(pdf_path, 32) # 32 represents ppSaveAsPDF
        deck.Close()
        powerpoint.Quit()
        print(f"Successfully saved as PDF: {pdf_path}")
        return True
    except Exception as e:
        print(f"Failed to convert using PowerPoint COM: {e}")
        return False

if __name__ == "__main__":
    pptx_to_pdf("presentation.pptx", "presentation.pdf")
