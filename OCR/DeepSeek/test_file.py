from engine_deep_seek_engine import DeepSeekExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 1 - Init engine 2 agent -> Check format: 
# 2 - if docs use Rasterizer in pdf_processor
# 2 - if pdf  use Deepseek   in deepseek_engine 
# 3 -  => Save as md
# 4 - Clean data
class DeepSeekTestFlow:

    def __init__(self, workspace_dir:str):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=true, exist_ok=true)

        self.raw_dir = self.workspace / "raw_extracted"
        self.raw_dir.mkdir(exist_ok=True)
        
        self.clean_dir = self.workspace / "clean_markdown"
        self.clean_dir.mkdir(exist_ok=True)