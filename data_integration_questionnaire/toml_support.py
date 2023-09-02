from pathlib import Path
import tomli
from data_integration_questionnaire.config import cfg

def read_toml(file: Path) -> dict:
    with open(file, "rb") as f:
        return tomli.load(f)
    
def read_prompts_toml() -> dict:
    return read_toml(cfg.project_root/'prompts.toml')
    
if __name__ == "__main__":
    from data_integration_questionnaire.log_init import logger
    prompts_config = read_prompts_toml()
    assert prompts_config is not None
    assert prompts_config['data_integration_questionnaire_generator'] is not None
    logger.info("prompts: %s", prompts_config)