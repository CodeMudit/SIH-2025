from pydantic import BaseModel

class ImageAnalysisResponse(BaseModel):
    filename: str
    analysis_result: str
    timestamp: str