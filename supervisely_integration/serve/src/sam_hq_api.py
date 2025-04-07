from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import torch
import numpy as np
from typing import List, Dict, Optional, Tuple
import json
import cv2
from segment_anything import sam_hq_model_registry, SamPredictor
import io
from PIL import Image

app = FastAPI(title="SAM-HQ API")

# Model configuration
MODEL_DATA_PATH = "./models/model_data.json"
WEIGHTS_LOCATION = "/weights"
MODEL_TYPE = "vit_h"  # Default model type

class ModelInfo(BaseModel):
    name: str
    weights_link: str
    description: Optional[str] = None

class DownloadRequest(BaseModel):
    model_name: str
    custom_link: Optional[str] = None

class SegmentationRequest(BaseModel):
    points: List[List[float]]  # List of [x, y] coordinates
    point_labels: List[int]    # 1 for foreground, 0 for background
    multimask_output: bool = True

class SegmentationResponse(BaseModel):
    masks: List[List[List[bool]]]  # List of binary masks
    scores: List[float]            # Confidence scores for each mask
    logits: List[List[List[float]]] # Raw logits for each mask

# Global model instance
model = None
predictor = None

def load_model_data() -> List[Dict]:
    """Load model information from JSON file"""
    try:
        with open(MODEL_DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def download_weights(model_name: str, weights_link: str) -> str:
    """Download model weights to the specified location"""
    weights_file_name = model_name.lower().replace(" ", "_").replace("-", "_") + ".pth"
    weights_dst_path = os.path.join(WEIGHTS_LOCATION, weights_file_name)
    
    if not os.path.exists(weights_dst_path):
        # In a real implementation, you would download the weights here
        # For now, we'll just create an empty file to simulate the download
        os.makedirs(WEIGHTS_LOCATION, exist_ok=True)
        torch.save({}, weights_dst_path)
    
    return weights_dst_path

def initialize_model(model_type: str = MODEL_TYPE, checkpoint_path: Optional[str] = None):
    """Initialize the SAM-HQ model"""
    global model, predictor
    
    if checkpoint_path is None:
        checkpoint_path = os.path.join(WEIGHTS_LOCATION, f"{model_type}.pth")
    
    if not os.path.exists(checkpoint_path):
        raise HTTPException(status_code=404, detail=f"Model checkpoint not found at {checkpoint_path}")
    
    model = sam_hq_model_registry[model_type](checkpoint=checkpoint_path)
    model.to(device="cuda" if torch.cuda.is_available() else "cpu")
    predictor = SamPredictor(model)

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models"""
    model_data = load_model_data()
    return [ModelInfo(**model) for model in model_data]

@app.post("/download")
async def download_model(request: DownloadRequest):
    """Download a specific model"""
    model_data = load_model_data()
    
    if request.custom_link:
        # Handle custom model download
        weights_path = download_weights("custom_model", request.custom_link)
        return {"status": "success", "weights_path": weights_path}
    
    # Find the requested model in the model data
    model_info = next((model for model in model_data if model["Model"] == request.model_name), None)
    
    if not model_info:
        raise HTTPException(status_code=404, detail=f"Model {request.model_name} not found")
    
    weights_path = download_weights(model_info["Model"], model_info["weights_link"])
    return {"status": "success", "weights_path": weights_path}

@app.post("/segment")
async def segment_image(
    file: UploadFile = File(...),
    points: str = None,
    point_labels: str = None,
    multimask_output: bool = True
):
    """Segment an image using SAM-HQ"""
    global predictor
    
    if predictor is None:
        initialize_model()
    
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image = np.array(image)
        
        # Convert points and labels from string to lists
        points_list = json.loads(points) if points else []
        point_labels_list = json.loads(point_labels) if point_labels else []
        
        # Convert points to numpy array
        points_array = np.array(points_list) if points_list else None
        point_labels_array = np.array(point_labels_list) if point_labels_list else None
        
        # Set image and predict
        predictor.set_image(image)
        masks, scores, logits = predictor.predict(
            point_coords=points_array,
            point_labels=point_labels_array,
            multimask_output=multimask_output
        )
        
        # Convert results to list format for JSON serialization
        masks_list = masks.tolist()
        scores_list = scores.tolist()
        logits_list = logits.tolist()
        
        return {
            "masks": masks_list,
            "scores": scores_list,
            "logits": logits_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_initialized": model is not None} 