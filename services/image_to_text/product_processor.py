import cv2
import numpy as np
from PIL import Image
import base64
import io
import openai
from ultralytics import YOLO
import torch
from typing import Dict, List, Tuple, Optional
import json
import time

class HybridProductAnalyzer:
    def __init__(self, openai_api_key: str, yolo_model_path: str = "yolov8n.pt"):
        """
        Initialize the hybrid analyzer with local CV models and OpenAI API
        
        Args:
            openai_api_key: Your OpenAI API key
            yolo_model_path: Path to YOLO model (downloads automatically if not found)
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.yolo_model = YOLO(yolo_model_path)
        self.confidence_threshold = 0.5
        
    def preprocess_image(self, image_path: str) -> Dict:
        """
        Local preprocessing to extract basic features and detect objects
        """
        # Load image
        image = cv2.imread(image_path)
        original_image = image.copy()
        
        preprocessing_results = {
            'image_path': image_path,
            'image_size': image.shape[:2],
            'detected_objects': [],
            'image_quality_metrics': {},
            'cropped_product': None
        }
        
        # 1. Object Detection with YOLO
        results = self.yolo_model(image)
        
        # Extract detected objects and find the main product
        main_product_box = None
        main_product_box_area = 0
        max_confidence = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    conf = float(box.conf[0])
                    if conf > self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        class_id = int(box.cls[0])
                        class_name = self.yolo_model.names[class_id]
                        
                        obj_info = {
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2],
                            'area': (x2-x1) * (y2-y1)
                        }
                        preprocessing_results['detected_objects'].append(obj_info)
                        
                        # Assume largest detected object is the main product
                        if conf > max_confidence and obj_info['area'] > 1000:  # Minimum size threshold
                            max_confidence = conf
                            main_product_box_area = obj_info['area']
                            main_product_box = [x1, y1, x2, y2]
        
        # 2. Crop main product if detected
        if main_product_box:
            x1, y1, x2, y2 = main_product_box
            # Add padding around the detected object
            padding = 20
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)
            
            cropped_product = original_image[y1:y2, x1:x2]
            preprocessing_results['cropped_product'] = cropped_product
            preprocessing_results['main_product_bbox'] = [x1, y1, x2, y2]
        
        # 3. Basic Image Quality Assessment
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Blur detection (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        preprocessing_results['image_quality_metrics'] = {
            'is_blurry': blur_score < 100,  # Threshold for blur detection
            'is_too_dark': brightness < 50,
            'is_too_bright': brightness > 200,
            'bad_framed':main_product_box_area/(image.shape[1]*image.shape[0]) > 0.6
        }
        
        return preprocessing_results
    
    
    def encode_image_to_base64(self, image: np.ndarray) -> str:
        """Convert numpy array image to base64 string for GPT-4 Vision"""
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
            
        pil_image = Image.fromarray(image_rgb)
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def analyze_with_gpt4_vision(self, preprocessing_results: Dict) -> Dict:
        """
        Send preprocessed information and image to GPT-4 Vision for detailed analysis
        """
        # Use cropped product if available, otherwise full image
        if preprocessing_results['cropped_product'] is not None:
            analysis_image = preprocessing_results['cropped_product']
            context = "cropped product image"
        else:
            analysis_image = cv2.imread(preprocessing_results['image_path'])
            context = "full image"
        
        # Encode image
        base64_image = self.encode_image_to_base64(analysis_image)
        
        # Create context from preprocessing
        preprocessing_context = self._create_preprocessing_context(preprocessing_results)
        
        # GPT-4 Vision prompt
        prompt = f"""
You are an expert product condition assessor. Analyze this {context} and provide a detailed assessment.

PREPROCESSING CONTEXT:
{preprocessing_context}

Please provide a JSON response with the following structure:
{{
    "condition": "perfect|good|fair|poor|broken",
    "confidence": 0.0-1.0,
    "description": "Detailed description of the product and its condition",
    "defects_found": [
        {{
            "type": "scratch|dent|stain|crack|wear|discoloration|other",
            "severity": "minor|moderate|severe",
            "location": "description of where the defect is located",
            "description": "detailed description of the defect"
        }}
    ],
    "overall_assessment": "Brief summary of why this condition was assigned",
    "recommended_action": "keep|repair|replace|sell_as_damaged"
}}

Focus on:
1. Verifying the defects detected in preprocessing
2. Finding additional defects not caught by basic CV
3. Assessing overall product condition holistically
4. Providing actionable recommendations
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            # Parse GPT-4 response
            gpt_analysis = json.loads(response.choices[0].message.content)
            
            return {
                'gpt_analysis': gpt_analysis,
                'preprocessing_results': preprocessing_results,
                'analysis_timestamp': time.time(),
                'model_used': 'gpt-4-vision-preview'
            }
            
        except Exception as e:
            return {
                'error': f"GPT-4 Vision analysis failed: {str(e)}",
                'preprocessing_results': preprocessing_results,
                'fallback_condition': self._fallback_condition_assessment(e)
            }
    
    def _create_preprocessing_context(self, results: Dict) -> str:
        """Create human-readable context from preprocessing results"""
        context_parts = []
        
        # Detected objects
        if results['detected_objects']:
            objects = [f"{obj['class']} (conf: {obj['confidence']:.2f})" 
                      for obj in results['detected_objects']]
            context_parts.append(f"Detected objects: {', '.join(objects)}")
        
        # Image quality
        quality = results['image_quality_metrics']
        quality_issues = []
        if quality.get('is_blurry'): quality_issues.append("blurry")
        if quality.get('is_too_dark'): quality_issues.append("too dark")
        if quality.get('is_too_bright'): quality_issues.append("too bright")
        
        if quality_issues:
            context_parts.append(f"Image quality issues: {', '.join(quality_issues)}")
        
        return "\n".join(context_parts) if context_parts else "No specific issues detected in preprocessing"
    
    def _fallback_condition_assessment(self, error) -> Dict:
        """Simple fallback assessment if GPT-4 fails"""
        
        return {
            'condition': "unidentify",
            'confidence': 0,  
            'description': str(error),
            'note': 'This is a fallback assessment due to GPT-4 Vision API failure'
        }
    
    def analyze_product(self, image_path: str) -> Dict:
        """
        Main method to analyze a product image
        """
        print(f"Starting analysis of {image_path}")
        
        # Step 1: Local preprocessing
        print("1. Running local preprocessing...")
        preprocessing_results = self.preprocess_image(image_path)
        bad_quality_reply = self.image_quality_reply(preprocessing_results['image_quality_metrics'])
        if bad_quality_reply:
            print("2. Bad quality reply fallback...")
            return {
                'condition': "unidentify",
                'confidence': 1,  
                'description': bad_quality_reply,
                'note': 'This is a fallback assessment due to image bad quality'
            }
        
        # Step 2: GPT-4 Vision analysis
        print("2. Analyzing with GPT Vision...")
        final_results = self.analyze_with_gpt4_vision(preprocessing_results)
        
        print("Analysis complete!")
        return final_results
    
    def image_quality_reply(self,image_quality_metrics, image_name=None):
        """
        Generate user-friendly messages for image quality issues.
        """
        
        # Define user-friendly messages for each quality issue
        quality_messages = {
            'is_blurry': "The image appears to be blurry or out of focus",
            'is_too_dark': "The image is too dark and lacks sufficient lighting",
            'is_too_bright': "The image is overexposed or too bright",
            'bad_framed': "The main product takes up too much of the frame"
        }
        
        # Define suggestions for each issue
        quality_suggestions = {
            'is_blurry': "Try taking a sharper photo with better focus",
            'is_too_dark': "Please take the photo in better lighting conditions",
            'is_too_bright': "Reduce the lighting or avoid direct flash",
            'bad_framed': "Step back to include more background around the product"
        }
        
        # Collect active quality issues
        active_issues = [issue for issue, is_active in image_quality_metrics.items() if is_active]
        
        if not active_issues:
            return None
        
        # Build the message
        image_ref = f"'{image_name}'" if image_name else "The uploaded image"
        
        if len(active_issues) == 1:
            issue = active_issues[0]
            message = f"❌ {image_ref} cannot be processed.\n\n"
            message += f"Issue: {quality_messages[issue]}.\n"
            message += f"Suggestion: {quality_suggestions[issue]}."
        else:
            message = f"❌ {image_ref} cannot be processed due to multiple quality issues:\n\n"
            
            for i, issue in enumerate(active_issues, 1):
                message += f"{i}. {quality_messages[issue]}\n"
            
            message += "\nSuggestions:\n"
            for i, issue in enumerate(active_issues, 1):
                message += f"{i}. {quality_suggestions[issue]}\n"
        
        message += "\n💡 Please upload a new image with better quality."
        
        return message

# Usage example
if __name__ == "__main__":
    import os
    # Initialize analyzer
    analyzer = HybridProductAnalyzer(
        openai_api_key=os.environ['OPENAI_API_KEY'],
        yolo_model_path="yolov8n.pt"  # Will download automatically if not present
    )
    
    pictures = ["bad_framed_laptop.png", "blurry_laptop.png", "bright_laptop.png",
                "obscure_laptop.png", "chrased_laptop.jpg", "laptop.jpg"]

    for pic in pictures:
        # Analyze a product image
        results = analyzer.analyze_product("services\image_to_text\\testing_images\{}".format(pic))
        
        # Print results
        if 'gpt_analysis' in results:
            analysis = results['gpt_analysis']
            print(f"\nProduct Condition: {analysis['condition']}")
            print(f"Confidence: {analysis['confidence']:.2f}")
            print(f"Description: {analysis['description']}")
            print(f"Overall Assessment: {analysis['overall_assessment']}")
            
            if analysis['defects_found']:
                print("\nDefects Found:")
                for defect in analysis['defects_found']:
                    print(f"- {defect['type']} ({defect['severity']}): {defect['description']}")
        else:
            print("Analysis failed or used fallback method")
            print(results)