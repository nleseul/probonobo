from PIL import ImageChops

class ScreenshotRegionIdentifier:

    def __init__(self, **kwargs):
        self.coords = kwargs['coords']
        self.reference = kwargs['reference']
        self.threshold = kwargs.get('threshold')
        self.debug_name = kwargs.get('debug_name')

        if (self.threshold is None):
            self.threshold = 0

    def __call__(self, *args, **kwargs):
        screenshot = kwargs['screenshot']
        crop_rect = self.coords + tuple(map(lambda x, y: x + y, self.coords, self.reference.size))
        cropped_screenshot = screenshot.crop(crop_rect)

        diff = ImageChops.difference(cropped_screenshot, self.reference)
        bounds = diff.getbbox()
        extrema = diff.getextrema()

        matches = max(ex[1] for ex in extrema) <= self.threshold

        if not matches and self.debug_name is not None:
            cropped_screenshot.save(self.debug_name + '-compare.png')
            diff.save(self.debug_name + '-diff.png')

            for y in range(diff.height):
                for x in range(diff.width):
                    print(diff.getpixel((x, y)), end=' ')
                print()

        return matches
