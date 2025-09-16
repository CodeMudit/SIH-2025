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

data = {
    'Apple__Apple_scab': {
        'cause': 'Caused by the fungus Venturia inaequalis, which overwinters in infected leaves and spreads via spores in wet spring conditions.',
        'cure': 'Apply fungicides (e.g., captan) during bud break; rake and destroy fallen leaves; choose resistant varieties like Liberty.'
    },
    'Apple_Black_rot': {
        'cause': 'Caused by the fungus Diplodia seriata (syn. Botryosphaeria obtusa), entering through wounds and thriving in warm, humid conditions.',
        'cure': 'Sanitation: Remove infected fruit and cankers; apply copper-based fungicides early season; prune for air circulation.'
    },
    'Apple_Cedar_apple_rust': {
        'cause': 'Caused by the fungus Gymnosporangium juniperi-virginianae, requiring alternating hosts (apple and cedar/juniper) for its life cycle.',
        'cure': 'Remove nearby cedars/juniper galls; apply myclobutanil fungicide at bud break; plant resistant apples like Enterprise.'
    },
    'Apple__healthy': {
        'cause': 'No disease detected; healthy leaves indicate proper care and resistance.',
        'cure': 'Maintain with balanced fertilizer, regular watering, and pruning; monitor for early signs of issues.'
    },
    'Background_without_leaves': {
        'cause': 'Not a disease; this class represents images without plant leaves (e.g., empty backgrounds in dataset).',
        'cure': 'Upload a clear image of plant leaves for analysis; ensure good lighting and focus on foliage.'
    },
    'Blueberry__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Continue good practices: acidic soil (pH 4.5-5.5), mulch, and net against birds.'
    },
    'Cherry_Powdery_mildew': {
        'cause': 'Caused by the fungus Podosphaera clandestina, favoring cool, dry conditions on young leaves.',
        'cure': 'Apply sulfur-based fungicides; improve air flow by pruning; water at base to keep foliage dry.'
    },
    'Cherry__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Prune annually for shape; fertilize in spring; ensure full sun and well-drained soil.'
    },
    'Corn__Cercospora_leaf_spot Gray_leaf_spot': {
        'cause': 'Caused by the fungus Cercospora zeae-maydis, spreading in warm, humid weather via spores on debris.',
        'cure': 'Rotate crops; apply fungicides like azoxystrobin; remove infected residue post-harvest.'
    },
    'Corn_Common_rust': {
        'cause': 'Caused by the fungus Puccinia sorghi, with spores overwintering on alternate hosts like oxalis.',
        'cure': 'Plant resistant hybrids (e.g., DKC 62-08); apply triazoles early; destroy volunteer corn.'
    },
    'Corn_Northern_Leaf_Blight': {
        'cause': 'Caused by the fungus Exserohilum turcicum, thriving in moderate temps (60-80°F) and high humidity.',
        'cure': 'Use resistant varieties; apply propiconazole at tasseling; rotate with non-host crops.'
    },
    'Corn__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Maintain fertility with NPK; space plants for air flow; irrigate evenly.'
    },
    'Grape__Black_rot': {
        'cause': 'Caused by the fungus Guignardia bidwellii, spores spread by rain from infected debris.',
        'cure': 'Apply mancozeb pre-bloom; prune for canopy openness; sanitize tools.'
    },
    'Grape_Esca(Black_Measles)': {
        'cause': 'Caused by a complex of fungi (e.g., Phaeomoniella), entering via pruning wounds.',
        'cure': 'Delay pruning until dry weather; apply aramid fungicides to cuts; remove infected vines.'
    },
    'Grape__Leaf_blight(Isariopsis_Leaf_Spot)': {
        'cause': 'Caused by the fungus Septoria leaf spot (Isariopsis), splashing from soil in wet conditions.',
        'cure': 'Fungicides like chlorothalonil; mulch to reduce splash; remove lower leaves.'
    },
    'Grape___healthy': {
        'cause': 'No disease detected.',
        'cure': 'Trellis for sun exposure; balanced pruning; monitor soil moisture.'
    },
    'Orange__Haunglongbing(Citrus_greening)': {
        'cause': 'Caused by the bacterium Liberibacter asiaticus, transmitted by Asian citrus psyllid.',
        'cure': 'Remove infected trees; control psyllids with imidacloprid; no cure—focus on prevention.'
    },
    'Peach__Bacterial_spot': {
        'cause': 'Caused by the bacterium Xanthomonas arboricola pv. pruni, spread by rain/splashing.',
        'cure': 'Copper sprays at bud swell; choose resistant varieties like Contender; avoid overhead watering.'
    },
    'Peach__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Thin fruit for size; fertilize post-harvest; ensure good drainage.'
    },
    'Pepper,bell_Bacterial_spot': {
        'cause': 'Caused by Xanthomonas spp., entering via wounds in warm, wet conditions.',
        'cure': 'Fixed copper bactericides; rotate crops; use disease-free seeds.'
    },
    'Pepper,_bell__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Stake for air flow; consistent watering; mulch to suppress weeds.'
    },
    'Potato__Early_blight': {
        'cause': 'Caused by the fungus Alternaria solani, spores from debris in warm, wet weather.',
        'cure': 'Apply chlorothalonil every 7-10 days; rotate 3 years; hill soil for protection.'
    },
    'Potato_Late_blight': {
        'cause': 'Caused by Phytophthora infestans, spreading rapidly in cool, moist conditions.',
        'cure': 'Fungicides like mefenoxam; destroy volunteers; plant certified seed.'
    },
    'Potato__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Fertilize balanced; space 12" apart; harvest when vines yellow.'
    },
    'Raspberry__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Trellis canes; thin annually; acidic soil pH 5.5-6.5.'
    },
    'Soybean_healthy': {
        'cause': 'No disease detected.',
        'cure': 'Inoculate seeds; row spacing 30"; weed control.'
    },
    'Squash__Powdery_mildew': {
        'cause': 'Caused by Podosphaera xanthii, in warm, dry days with cool nights.',
        'cure': 'Sulfur dust; reflective mulch; resistant varieties like Silver Queen.'
    },
    'Strawberry__Leaf_scorch': {
        'cause': 'Caused by the fungus Diplocarpon earliae, spores in wet foliage.',
        'cure': 'Fungicides like captan; improve drainage; remove old leaves post-harvest.'
    },
    'Strawberry__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Mulch with straw; renovate after fruiting; pH 5.5-6.5.'
    },
    'Tomato__Bacterial_spot': {
        'cause': 'Caused by Xanthomonas spp., via seeds or transplants in warm, wet weather.',
        'cure': 'Copper + mancozeb; fixed copper sprays; rotate 2-3 years.'
    },
    'Tomato_Early_blight': {
        'cause': 'Caused by Alternaria solani, from soil splash in humid conditions.',
        'cure': 'Chlorothalonil weekly; stake for air flow; mulch heavily.'
    },
    'Tomato_Late_blight': {
        'cause': 'Caused by Phytophthora infestans, rapid spread in cool, moist nights.',
        'cure': 'Mefenoxam at first symptoms; destroy debris; greenhouse ventilation.'
    },
    'Tomato__Leaf_Mold': {
        'cause': 'Caused by Passalora fulva, high humidity in enclosed spaces.',
        'cure': 'Improve ventilation; potassium phosphite sprays; resistant varieties.'
    },
    'Tomato__Septoria_leaf_spot': {
        'cause': 'Caused by Septoria lycopersici, spores from debris in wet weather.',
        'cure': 'Mancozeb every 7 days; rotate crops; lower leaves removed.'
    },
    'Tomato_Spider_mites Two-spotted_spider_mite': {
        'cause': 'Caused by Tetranychus urticae mites, thriving in hot, dry conditions.',
        'cure': 'Insecticidal soap or miticides; increase humidity; release predators like ladybugs.'
    },
    'Tomato__Target_Spot': {
        'cause': 'Caused by Corynespora cassiicola, warm, humid greenhouses.',
        'cure': 'Azoxystrobin; sanitize pots; avoid overhead irrigation.'
    },
    'Tomato__Tomato_Yellow_Leaf_Curl_Virus': {
        'cause': 'Transmitted by whiteflies (Bemisia tabaci), persistent virus.',
        'cure': 'Control whiteflies with imidacloprid; reflective mulch; remove infected plants.'
    },
    'Tomato_Tomato_mosaic_virus': {
        'cause': 'Caused by Tobacco mosaic virus (TMV), spread by handling/tools.',
        'cure': 'No cure—destroy plants; sanitize tools with 10% bleach; resistant varieties like Big Beef.'
    },
    'Tomato__healthy': {
        'cause': 'No disease detected.',
        'cure': 'Full sun; even watering; support with cages.'
    }
}


# Now len(label) == 39—wait, still 39? Wait, count again.
# Actually, standard is 39 for some splits, but your model has 40. Check model summary.

# Load disease dict

plant_disease = [{'name': label, 'cause': info['cause'], 'cure': info['cure']} for label, info in data.items()]
try:
    with open("plant_disease.json", 'r', encoding='utf-8') as file:
        plant_disease = json.load(file)
    disease_dict = {disease['name']: disease for disease in plant_disease}  # Defined here
    print("✅ Disease dictionary loaded successfully")
except Exception as e:
    print(f"❌ Error loading disease dictionary: {e}")
    disease_dict = {}  # Empty fallback

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