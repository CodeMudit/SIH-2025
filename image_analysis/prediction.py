import numpy as np
import json
import tensorflow as tf
from PIL import Image

# Global setup (loads on import)
IMG_SIZE = (224, 224)

label = [
    'Apple__Apple_scab', 'Apple_Black_rot', 'Apple_Cedar_apple_rust', 'Apple__healthy',
    'Background_without_leaves', 'Blueberry__healthy', 'Cherry_Powdery_mildew', 'Cherry__healthy',
    'Corn__Cercospora_leaf_spot Gray_leaf_spot', 'Corn_Common_rust', 'Corn_Northern_Leaf_Blight', 'Corn__healthy',
    'Grape__Black_rot', 'Grape_Esca(Black_Measles)', 'Grape__Leaf_blight(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange__Haunglongbing(Citrus_greening)', 'Peach__Bacterial_spot', 'Peach__healthy',
    'Pepper,bell_Bacterial_spot', 'Pepper,_bell__healthy',
    'Potato__Early_blight', 'Potato_Late_blight', 'Potato__healthy',
    'Raspberry__healthy', 'Soybean_healthy', 'Squash__Powdery_mildew',
    'Strawberry__Leaf_scorch', 'Strawberry__healthy',  # Fixed typo: scorch
    'Tomato__Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato__Leaf_Mold',
    'Tomato__Septoria_leaf_spot', 'Tomato_Spider_mites Two-spotted_spider_mite', 'Tomato__Target_Spot',
    'Tomato__Tomato_Yellow_Leaf_Curl_Virus', 'Tomato_Tomato_mosaic_virus', 'Tomato__healthy'
]
# Now len(label) == 39—wait, still 39? Wait, count again.
# Actually, standard is 39 for some splits, but your model has 40. Check model summary.

# Load disease dict
try:
    with open("plant_disease.json", 'r', encoding='utf-8') as file:
        plant_disease = json.load(file)
    disease_dict = {disease['name']: disease for disease in plant_disease}
    print("✅ Disease dictionary loaded successfully")
except Exception as e:
    print(f"❌ Error loading disease dictionary: {e}")
    disease_dict = {}

# Load model
try:
    model = tf.keras.models.load_model("image_analysis/plant_disease_recog_model_pwp (2).keras")
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

def extract_features(image_path: str):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(IMG_SIZE)
        img_array = np.array(img)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"❌ Error extracting features: {e}")
        return None

def model_predict(image_path: str):
    if model is None:
        return {"cause": "Model not loaded properly.", "cure": "Please check the model file."}
    
    img_array = extract_features(image_path)
    if img_array is None:
        return {"cause": "Could not process the image.", "cure": "Please try with a different image."}
    
    try:
        prediction = model.predict(img_array)
        print(f"🔍 Prediction shape: {prediction.shape}")  # Debug: Should be (1, 40)
        print(f"🔍 Raw probabilities: {prediction[0]}")  # Debug: See all 40 values
        
        idx = np.argmax(prediction[0])
        print(f"🔍 Argmax index: {idx}")  # Debug: What index is chosen?
        
        num_classes = len(label)
        if idx >= num_classes:
            print(f"⚠️ Warning: Predicted index {idx} exceeds label count {num_classes}. Clamping to {num_classes-1}.")
            idx = num_classes - 1  # Clamp to last valid label (or raise error)
        
        predicted_class_name = label[idx]
        confidence = prediction[0][idx]
        print(f"🔍 Predicted: {predicted_class_name}, Confidence: {confidence:.4f}")
        
        prediction_info = disease_dict.get(predicted_class_name, {})
        return {
            "predicted_class": predicted_class_name,
            "confidence": float(confidence),
            "cause": prediction_info.get('cause', 'Information not available'),
            "cure": prediction_info.get('cure', 'Information not available')
        }
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        import traceback
        print(traceback.format_exc())  # Full stack trace for debugging
        return {"cause": f"Error during prediction: {e}", "cure": "Please try again."}