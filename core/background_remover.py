import cv2
import numpy as np

class BackgroundRemover:
    def __init__(self):
        self.model = None
        self.torch = None
        self.rvm_rec = [None, None, None, None]
        self.bg_threshold = 0.7

    def _model_lazy_load(self):
        if self.model is None:
            import torch
            from RobustVideoMatting.model import MattingNetwork

            self.torch = torch
            self.model = MattingNetwork(variant='resnet50').eval().cuda()
            self.model.load_state_dict(torch.load('rvm_resnet50.pth'))

    def set_threshold(self, value):
        self.bg_threshold = value

    def remove_bg(self, frame_bg):
        self._model_lazy_load()
        frame_rgb = cv2.cvtColor(frame_bg, cv2.COLOR_BGR2RGB)

        tensor = self.torch.from_numpy(frame_rgb).float() / 255.0
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to("cuda")

        with self.torch.no_grad():
            outs = self.model(tensor, *self.rvm_rec, downsample_ratio=0.25)

        fgr, pha = outs[0], outs[1]
        self.rvm_rec = outs[2:6]

        fgr = (fgr[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        pha = pha[0].cpu().numpy()

        pha = np.where(pha < self.bg_threshold, 0, pha)
        pha = (pha * 255).astype(np.uint8)

        result = cv2.cvtColor(fgr, cv2.COLOR_RGB2BGRA)
        result[:, :, 3] = pha

        return result

    def apply_green_bg(self, result):
        green_bg = np.zeros_like(result)
        green_bg[:, :, 0] = 0
        green_bg[:, :, 1] = 255
        green_bg[:, :, 2] = 0
        green_bg[:, :, 3] = 255

        alpha = result[:, :, 3:4] / 255.0
        blended = result[:, :, :3] * alpha + green_bg[:, :, :3] * (1 - alpha)

        bgra = np.zeros_like(result)
        bgra[:, :, :3] = blended
        bgra[:, :, 3] = 255

        return bgra.astype(np.uint8)

bg_remover = BackgroundRemover()
