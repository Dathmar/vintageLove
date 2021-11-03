from PIL import Image
import qrcode


def generate_qr_code(url, save_loc):
    logo = Image.open(r'static/img/logo.png')

    # taking base width
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    # You need to convert the image into RGB in order to use it
    img_qr_big = qr.make_image(fill_color='#0A486A', back_color="white").convert('RGB')

    # Where to place the logo within the QR Code
    pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
    img_qr_big.paste(logo, pos)

    # Path where you want to save the Generate QR Code along with the name in a series or the number series
    img_qr_big.save(save_loc)


if __name__ == '__main__':
    generate_qr_code('https://www.localvintagestore.com/bespoke-shipping/vintage-love',
                             'static/vintage-love_qr.png')
