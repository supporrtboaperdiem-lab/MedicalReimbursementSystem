from paddleocr import PaddleOCR


class PaddleEngine:
    """
    Singleton PaddleOCR engine.

    The OCR model is loaded only once when the application starts,
    which greatly improves performance.
    """

    _ocr = None

    @classmethod
    def instance(cls):
        if cls._ocr is None:

            cls._ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en"
            )

        return cls._ocr

    @classmethod
    def recognize(cls, image):

        ocr = cls.instance()

        return ocr.ocr(
            image,
            cls=True
        )