class SubtitleService:
    def __init__(self, client):
        self.client = client

    def generate_subtitle(self, video_id, subtitle_text):
        # TODO: 调用IMS字幕接口
        pass

    def align_subtitle(self, video_id, subtitle_file):
        # TODO: 调用字幕校准接口
        pass 