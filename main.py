import os
import sys

import AveryLabels
from reportlab.lib.units import mm
from reportlab_qrcode import QRCodeImage
from reportlab.pdfgen import canvas

### config ###
labelForm = 4731

# mode "qr" prints a QR code and an ASN (archive serial number) text
mode = "qr"

# mode text prints a free text
#mode = "text"
#text="6y"

# print multiple labels on a single cutout of a label sheet
subLabelsX = 1
subLabelsY = 1

# prefix for the ASNs (make sure to also update your paperless config if you change this value)
prefix = 'GAN'
includePrefixInLabel = True
# what was the first ASN number printed on this sheet
firstASNOnSheet = 379
# how many labels have already been printed on this sheet successfully
labelsAlreadyPrinted = 0
# how many labels have been corrupted on this sheet because of misprints
labelsCorrupted = 0
# how many labels should be printed now
labelsToPrint = 189
# set this to 3 if the top left corner of your labels is in the correct position but your top right corner is 3 mm too far down
rotateOffset = -1*mm

fontSize = 2*mm
qrSize = 0.9
qrMargin = 1*mm

debug = False
positionHelper = True

### pre-calculation ###
asnsAlreadyPrinted = (labelsAlreadyPrinted-labelsCorrupted)*subLabelsX*subLabelsY
startASN = firstASNOnSheet + asnsAlreadyPrinted
offsetLabels = labelsAlreadyPrinted+labelsCorrupted

### globals ###
currentASN = startASN

# debug
count = 0


def render(c: canvas.Canvas, width: float, height: float):
    global currentASN
    global subLabelsX
    global subLabelsY

    subLabelWidth = width/subLabelsX
    subLabelHeight = height/subLabelsY

    for i in range(subLabelsX):
        for j in range(subLabelsY-1, -1, -1):  # no idea why inverted...
            subX = subLabelWidth*i
            subY = subLabelHeight*j

            c.saveState()
            c.translate(subX, subY)

            if mode == "qr":
                barcode_value = f"{prefix}{currentASN:05d}"
                label_value = f"{prefix if includePrefixInLabel else ''}{currentASN:05d}"
                currentASN = currentASN + 1

                qr = QRCodeImage(barcode_value, size=subLabelHeight*qrSize)
                qr.drawOn(c, x=qrMargin, y=subLabelHeight*((1-qrSize)/2))
                c.setFont("Helvetica", size=fontSize)
                c.drawString(x=subLabelHeight, y=(
                    subLabelHeight-fontSize)/2, text=label_value)

            elif mode == "text":
                if debug:
                    global count
                    count = count + 1

                c.drawString(
                    x=(subLabelWidth-2*fontSize)/2, y=(subLabelHeight-fontSize)/2,
                    text=text if not debug else str(count)
                )

            if positionHelper:
                r = 0.1
                d = 0
                if debug:
                    r = 0.5
                    d = r
                c.circle(x_cen=0+d, y_cen=0+d, r=r, stroke=1)
                c.circle(x_cen=subLabelWidth-d, y_cen=0+d, r=r, stroke=1)
                c.circle(x_cen=0+d, y_cen=subLabelHeight-d, r=r, stroke=1)
                c.circle(x_cen=subLabelWidth-d,
                            y_cen=subLabelHeight-d, r=r, stroke=1)

            c.restoreState()


outputDirectory = 'out'
fileName = os.path.join(outputDirectory, f"labels-{labelForm}-{mode}.pdf")

label = AveryLabels.AveryLabel(labelForm)
label.debug = debug
try:
    os.makedirs(outputDirectory, exist_ok=True)
except OSError as oe:
    sys.exit(f"Failed to create directory '{outputDirectory}': {oe}")
label.open(fileName)
label.render(render, count=labelsToPrint, offset=offsetLabels, rotateOffset=rotateOffset)
label.close()

print
print(fileName)
